"""Behavioral checks with simulated registers, serial traffic and time; no hardware."""

import csv
import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import measure_efficiency as tool


class Clock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def report():
    payload = bytes((1, 2)) + bytes(31)
    return b"\xff\x55" + payload + bytes(((sum(payload) & 0xff) ^ 0x44,))


def reply(value):
    return tool.PX100_REPLY + value.to_bytes(3, "big") + b"\xce\xcf"


def arguments(**updates):
    values = dict(source_port="FAKE_SOURCE", load_port="FAKE_LOAD", probe=False,
                  voltages=tool.VOLTAGES, currents=tool.CURRENTS, seconds=1,
                  settle=0, settle_timeout=15, point_retries=1, output_dir=None, ovp=None, ocp=None,
                  voltage_tolerance=0.05, current_tolerance=0.05)
    values.update(updates)
    return SimpleNamespace(**values)


class Rig:
    def __init__(self, clock):
        self.clock = clock
        self.regs = {8: 500, 9: 100, 82: 550, 83: 150, 18: 1}
        self.original = dict(self.regs)
        self.load_on = True
        self.load_current = 10  # centiamps
        self.writes = []
        self.commands = []
        self.closed = []
        self.suppress_replies = False
        self.wrong_current = False
        self.current_query_override = None
        self.mode = 0
        self.fail_off = False
        self.fail_restore = None
        self.fail_input = False
        self.fail_load_open = False
        self.port = FakePort(self)
        self.instrument = FakeInstrument(self)
        self.module = SimpleNamespace(instrument=self.instrument, volts_resolution=100,
                                      amps_resolution=1000, max_set_current=6,
                                      max_ocp_current=6.2, max_set_voltage=25,
                                      get_input_voltage=self.input_voltage)

    def input_voltage(self):
        if self.fail_input:
            raise TimeoutError("input read failed")
        return 30

    def open_load(self, *args, **kwargs):
        if self.fail_load_open:
            raise OSError("load port unavailable")
        return self.port


class FakeInstrument:
    def __init__(self, rig):
        self.rig = rig
        self.serial = SimpleNamespace(write_timeout=None, close=lambda: rig.closed.append("source"))

    def write_register(self, address, value):
        r = self.rig
        r.writes.append((address, value))
        if address == 18 and value == 0 and r.fail_off:
            raise TimeoutError("source OFF failed")
        if address == r.fail_restore and value == r.original[address]:
            raise TimeoutError("restore failed")
        r.regs[address] = value

    def read_register(self, address):
        return self.rig.regs[address]

    def read_registers(self, address, count):
        r = self.rig
        if (address, count) == (10, 9):
            voltage = r.regs[8] if r.regs[18] else 0
            current = r.load_current * 10 if r.load_on else 0
            protection = 1 if voltage > r.regs[82] else 2 if current > r.regs[83] else 0
            if protection:
                r.regs[18] = 0
            return [voltage, current, 0, 0, 3000, 0, protection, r.mode, r.regs[18]]
        return [r.regs[index] for index in range(address, address + count)]


class FakePort:
    port = "FAKE_LOAD"

    def __init__(self, rig):
        self.rig = rig
        self.rx = bytearray(report())
        self.chunk_size = 256

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rig.closed.append("load")

    @property
    def in_waiting(self):
        return len(self.rx)

    def read(self, count):
        count = min(count, self.chunk_size)
        data = bytes(self.rx[:count])
        del self.rx[:count]
        if not data:
            self.rig.clock.sleep(0.05)
        return data

    def write(self, packet):
        r = self.rig
        command, first, second = packet[2:5]
        r.commands.append(command)
        if command == 1:
            r.load_on = bool(first)
        elif command == 2:
            r.load_current = first * 100 + second
        if r.suppress_replies:
            return len(packet)
        if command < 0x10:
            self.rx.extend(tool.PX100_ACK)
        else:
            values = {0x10: int(r.load_on), 0x11: r.regs[8] * 10 - 100,
                      0x12: 100 if r.wrong_current else r.load_current * 10,
                      0x17: r.load_current, 0x18: 0}
            if r.current_query_override is not None:
                values[0x12] = r.current_query_override
            self.rx.extend(reply(values[command]))
        return len(packet)


class EfficiencyTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.rig = Rig(self.clock)
        self.source = tool.RKSource(self.rig.module)
        self.load = tool.AtorchLoad(self.rig.port)
        self.out = StringIO()
        for context in (patch.object(tool, "time", self.clock), redirect_stdout(self.out),
                        redirect_stderr(self.out), patch.object(sys, "path", sys.path[:])):
            context.__enter__()
            self.addCleanup(context.__exit__, None, None, None)

    def configured(self):
        self.source.configure_limits(arguments())
        self.source.set_enabled(True)
        self.load.receive(tool.ATORCH_REPORT, 4)

    def run_rig(self, args):
        if not args.probe and args.output_dir is None:
            temporary = TemporaryDirectory()
            self.addCleanup(temporary.cleanup)
            args.output_dir = Path(temporary.name) / "results"
        with patch.dict(sys.modules, {
            "serial": SimpleNamespace(Serial=self.rig.open_load),
            "RK6006_module": SimpleNamespace(RK6006=lambda port: self.rig.module),
        }):
            tool.run(args)

    def assert_restored(self):
        self.assertEqual({key: self.rig.regs[key] for key in (8, 9, 82, 83)},
                         {key: self.rig.original[key] for key in (8, 9, 82, 83)})
        self.assertEqual(self.rig.regs[18], 0)
        self.assertFalse(self.rig.load_on)

    def test_default_limits_and_restoration(self):
        self.assertEqual(tool.planned_limits(arguments()), (2.1, 22, 2.31))
        settings = self.source.snapshot_settings()
        self.source.configure_limits(arguments())
        self.assertEqual((self.rig.regs[82], self.rig.regs[83], self.rig.regs[9]), (2200, 2310, 2100))
        self.source.set_voltage(20)
        tool.shutdown(self.source, self.load, settings)
        self.assert_restored()

    def test_explicit_limits(self):
        self.assertEqual(tool.planned_limits(arguments(ovp=23, ocp=2.5)), (2.1, 23, 2.5))

    def test_invalid_limits(self):
        for changes in ({"ovp": 20}, {"ocp": 2.1}, {"ovp": float("nan")},
                        {"ocp": float("inf")}, {"ovp": 20.001}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                tool.planned_limits(arguments(**changes))

    def test_source_range_checks_before_writes(self):
        for changes in ({"ovp": 28}, {"ocp": 6.3}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.source.configure_limits(arguments(**changes))
        self.assertEqual(self.rig.writes, [])

    def test_register_readback_failure(self):
        with patch.object(self.rig.instrument, "read_register", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "did not confirm"):
                self.source.set_voltage(5)

    def test_constant_power_integration(self):
        self.configured()
        point = tool.measure_point(self.source, self.load, 5, 0.1, 10)
        self.assertAlmostEqual(point.source_wh, 0.5 * 10 / 3600)
        self.assertAlmostEqual(point.load_wh, 0.49 * 10 / 3600)
        self.assertAlmostEqual(point.efficiency_pct, 98)
        self.assertEqual(point.window_s, 10)

    def test_wrong_voltage_is_rejected(self):
        self.configured()
        with self.assertRaisesRegex(RuntimeError, "Wrong source voltage"):
            tool.measure_point(self.source, self.load, 20, 0.1, 1)

    def test_wrong_current_is_rejected(self):
        self.configured()
        with self.assertRaisesRegex(RuntimeError, "Wrong load current"):
            tool.measure_point(self.source, self.load, 5, 2, 1)

    def test_mid_window_current_error_is_rejected(self):
        self.configured()
        with patch.object(self.load, "read", side_effect=[(4.9, 0.1), (4.9, 0.01)]):
            with self.assertRaisesRegex(RuntimeError, "Wrong load current"):
                tool.measure_point(self.source, self.load, 5, 0.1, 1)

    def test_settling_waits_for_delayed_current_readings(self):
        self.configured()
        readings = [(4.9, 0.086)] * 4 + [(4.9, 0.1)] * 3
        with patch.object(self.load, "read", side_effect=readings) as read:
            tool.wait_for_settle(self.source, self.load, 5, 0.1, arguments(settle=2))
        self.assertEqual(read.call_count, 7)
        self.assertGreaterEqual(self.clock.monotonic(), 5)

    def test_settling_requires_consecutive_acceptable_samples(self):
        self.configured()
        readings = [(4.9, 0.1)] * 2 + [(4.9, 0.086)] + [(4.9, 0.1)] * 3
        with patch.object(self.load, "read", side_effect=readings) as read:
            tool.wait_for_settle(self.source, self.load, 5, 0.1, arguments())
        self.assertEqual(read.call_count, 6)

    def test_settling_readings_are_excluded_from_energy_window(self):
        self.configured()
        readings = iter([(4.9, 0.086)] * 4 + [(4.9, 0.1)] * 50)
        with patch.object(self.load, "read", side_effect=lambda: next(readings)):
            tool.wait_for_settle(self.source, self.load, 5, 0.1, arguments())
            point = tool.measure_point(self.source, self.load, 5, 0.1, 10)
        self.assertAlmostEqual(point.source_wh, 0.5 * 10 / 3600)
        self.assertAlmostEqual(point.load_wh, 0.49 * 10 / 3600)
        self.assertAlmostEqual(point.efficiency_pct, 98)

    def test_settling_timeout_includes_last_reading_error(self):
        self.configured()
        start = self.clock.monotonic()
        with patch.object(self.load, "read", return_value=(4.9, 0.086)):
            with self.assertRaisesRegex(tool.OperatingPointError, "Did not settle.*Wrong load current.*0.086"):
                tool.wait_for_settle(self.source, self.load, 5, 0.1, arguments(settle_timeout=3))
        self.assertAlmostEqual(self.clock.monotonic() - start, 3)

    def test_settling_allows_temporary_cc_mode(self):
        with patch.object(self.source, "read", side_effect=[tool.OperatingPointError("CC mode")] + [(5, 0.1)] * 3):
            with patch.object(self.load, "read", return_value=(4.9, 0.1)):
                tool.wait_for_settle(self.source, self.load, 5, 0.1, arguments())

    def test_settling_does_not_retry_protection_or_communication_errors(self):
        for error in (RuntimeError("OCP/2"), TimeoutError("No communication")):
            with self.subTest(error=error), patch.object(self.source, "read", side_effect=error) as read:
                with self.assertRaises(type(error)):
                    tool.wait_for_settle(self.source, self.load, 5, 0.1, arguments())
                self.assertEqual(read.call_count, 1)

    def test_nonfinite_measurement_is_rejected(self):
        self.configured()
        with patch.object(self.load, "read", return_value=(float("nan"), 0.1)):
            with self.assertRaisesRegex(RuntimeError, "Invalid or missing"):
                tool.measure_point(self.source, self.load, 5, 0.1, 1)

    def test_cc_mode_is_rejected(self):
        self.configured()
        self.rig.mode = 1
        with self.assertRaisesRegex(RuntimeError, "not in CV"):
            self.source.read()

    def test_protection_is_named(self):
        self.rig.regs[82] = 450
        with self.assertRaisesRegex(RuntimeError, "OVP/1"):
            self.source.read()

    def test_fragmented_report_and_reply(self):
        self.rig.port.chunk_size = 1
        self.assertEqual(self.load.query(0x11), 4900)
        self.assertEqual(self.load.query(0x12), 100)

    def test_stale_partial_reply_prevents_new_request(self):
        self.rig.port.rx.clear()
        self.load.buffer.extend(reply(5000)[:3])
        with self.assertRaisesRegex(RuntimeError, "incomplete stale"):
            self.load.query(0x12)
        self.assertEqual(self.rig.commands, [])
        self.assertFalse(self.load.synchronized)

    def test_stale_complete_reply_prevents_new_request(self):
        self.rig.port.rx.extend(reply(5000))
        with self.assertRaisesRegex(RuntimeError, "stale PX100"):
            self.load.query(0x12)
        self.assertEqual(self.rig.commands, [])

    def test_timeout_blocks_late_reply_and_only_allows_unverified_off(self):
        self.rig.suppress_replies = True
        with self.assertRaises(TimeoutError):
            self.load.query(0x11)
        self.rig.port.rx.extend(reply(5000))
        with self.assertRaisesRegex(RuntimeError, "synchronization lost"):
            self.load.query(0x12)
        with self.assertRaisesRegex(RuntimeError, "synchronization lost"):
            self.load.set_enabled(True)
        with self.assertRaisesRegex(RuntimeError, "without verification"):
            self.load.set_enabled(False)
        self.assertEqual(self.rig.commands, [0x11, 0x01])
        self.assertFalse(self.rig.load_on)

    def test_interrupted_transaction_blocks_more_queries(self):
        self.rig.port.rx.clear()
        with patch.object(self.rig.port, "read", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.load.query(0x11)
        with self.assertRaisesRegex(RuntimeError, "synchronization lost"):
            self.load.query(0x12)

    def test_full_sweep_csv_html_and_restoration(self):
        with TemporaryDirectory() as temporary:
            folder = Path(temporary) / "results"
            args = arguments(output_dir=folder)
            total_points = len(args.voltages) * len(args.currents)
            self.run_rig(args)
            with (folder / "results.csv").open(newline="", encoding="utf-8") as output:
                points = list(csv.DictReader(output))
            self.assertEqual(len(points), total_points)
            self.assertEqual({(float(p["set_v"]), float(p["set_a"])) for p in points},
                             {(v, a) for v in args.voltages for a in args.currents})
            for point in points:
                self.assertAlmostEqual(float(point["efficiency_pct"]),
                                       100 * (float(point["set_v"]) - 0.1) / float(point["set_v"]))
            html = (folder / "results.html").read_text(encoding="utf-8")
            self.assertIn(f"{total_points}/{total_points} points", html)
            self.assertIn("<svg", html)
            self.assertIn('href="debug.jsonl"', html)
            self.assertNotIn("Run stopped", html)
            events = [json.loads(line) for line in (folder / "debug.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[0]["event"], "session_start")
            self.assertEqual(events[-1]["event"], "session_end")
            self.assertEqual(events[-1]["status"], "complete")
            self.assertEqual(sum(event["event"] == "point_complete" for event in events), total_points)
        self.assert_restored()
        self.assertCountEqual(self.rig.closed, ["source", "load"])

    def test_initial_report_timeout_turns_source_off(self):
        self.rig.port.rx.clear()
        with self.assertRaises(TimeoutError):
            self.run_rig(arguments())
        self.assertEqual(self.rig.regs[18], 0)
        self.assertEqual(self.rig.commands, [])  # Unidentified load is not controlled.
        self.assertCountEqual(self.rig.closed, ["source", "load"])

    def test_debug_log_preserves_rejected_spike_raw_reply_and_shutdown(self):
        measure = tool.measure_point

        def spike(*args, **kwargs):
            self.rig.current_query_override = 187
            return measure(*args, **kwargs)

        with TemporaryDirectory() as temporary, patch.object(tool, "measure_point", side_effect=spike):
            folder = Path(temporary) / "results"
            with self.assertRaisesRegex(tool.OperatingPointError, "ATORCH 4.900 V / 0.187 A"):
                self.run_rig(arguments(output_dir=folder, voltages=(5,), currents=(0.1,)))
            events = [json.loads(line) for line in (folder / "debug.jsonl").read_text(encoding="utf-8").splitlines()]
        observed = [event for event in events if event["event"] == "sample" and event["phase"] == "measurement"]
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0]["load_a"], 0.187)
        self.assertEqual(observed[0]["source_a"], 0.1)
        self.assertTrue(any(event["event"] == "atorch_query" and event["command"] == "0x12"
                            and event["value"] == 187 for event in events))
        self.assertTrue(any(event["event"] == "atorch_rx" and "ca cb 00 00 bb ce cf" in event["data_hex"]
                            for event in events))
        self.assertTrue(any(event["event"] == "sample" and event["phase"] == "settling" for event in events))
        self.assertTrue(any(event["event"] == "rk_restore" and event["address"] == 82 for event in events))
        self.assertEqual(events[-1]["status"], "error")
        self.assertIn("0.187", events[-1]["error"])
        self.assertEqual([event["elapsed_s"] for event in events], sorted(event["elapsed_s"] for event in events))
        self.assert_restored()

    def test_debug_log_covers_initialization_failure(self):
        self.rig.fail_load_open = True
        with TemporaryDirectory() as temporary:
            folder = Path(temporary) / "results"
            with self.assertRaises(OSError):
                self.run_rig(arguments(output_dir=folder))
            events = [json.loads(line) for line in (folder / "debug.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(events[-1]["error"], "load port unavailable")
        self.assertTrue(any(event["event"] == "shutdown_end" and event["success"] for event in events))

    def test_debug_disk_failure_does_not_prevent_off(self):
        output = SimpleNamespace(write=lambda line: self.fail_disk(), flush=lambda: None)
        debug = tool.DebugLog(output)
        source = tool.RKSource(self.rig.module, debug)
        source.set_enabled(False)
        self.assertEqual(self.rig.regs[18], 0)
        self.assertTrue(debug.failed)
        self.assertIn("Debug logging stopped", self.out.getvalue())

    def fail_disk(self):
        raise OSError("disk full")

    def test_invalid_checksum_is_preserved_in_debug_log(self):
        output = StringIO()
        bad_report = bytearray(report())
        bad_report[-1] ^= 1
        self.rig.port.rx = bad_report + report()
        load = tool.AtorchLoad(self.rig.port, tool.DebugLog(output))
        self.assertTrue(load.read_enabled())
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertTrue(any(event["event"] == "atorch_frame" and not event["valid"] for event in events))

    def test_nonfinite_debug_values_remain_valid_json(self):
        output = StringIO()
        tool.DebugLog(output)("test", voltage=float("nan"))
        event = json.loads(output.getvalue(), parse_constant=lambda constant: self.fail("Nonstandard JSON"))
        self.assertEqual(event["voltage"], "nan")

    def test_load_open_failure_turns_source_off(self):
        self.rig.fail_load_open = True
        with self.assertRaisesRegex(OSError, "load port unavailable"):
            self.run_rig(arguments())
        self.assertEqual(self.rig.regs[18], 0)
        self.assertEqual(self.rig.closed, ["source"])

    def test_input_read_failure_turns_source_off(self):
        self.rig.fail_input = True
        with self.assertRaisesRegex(TimeoutError, "input read failed"):
            self.run_rig(arguments())
        self.assertEqual(self.rig.regs[18], 0)

    def test_probe_does_not_change_settings_or_outputs(self):
        self.run_rig(arguments(probe=True))
        self.assertEqual(self.rig.writes, [])
        self.assertTrue(all(command >= 0x10 for command in self.rig.commands))
        self.assertEqual(self.rig.regs, self.rig.original)
        self.assertTrue(self.rig.load_on)

    def test_failed_point_is_not_recorded_and_completed_point_survives(self):
        with TemporaryDirectory() as temporary:
            folder = Path(temporary) / "results"
            # First 0.1 A point succeeds. A failed 0.2 A regulation is rejected.
            self.rig.wrong_current = True
            with self.assertRaisesRegex(RuntimeError, "Wrong load current"):
                self.run_rig(arguments(output_dir=folder, voltages=(5,), currents=(0.1, 0.2)))
            with (folder / "results.csv").open(newline="", encoding="utf-8") as output:
                points = list(csv.DictReader(output))
            self.assertEqual(len(points), 1)
            self.assertEqual(float(points[0]["set_a"]), 0.1)
            self.assertIn("Wrong load current", (folder / "results.html").read_text(encoding="utf-8"))
        self.assert_restored()

    def test_interrupted_measurement_restores_settings(self):
        with TemporaryDirectory() as temporary, patch.object(tool, "measure_point", side_effect=KeyboardInterrupt):
            folder = Path(temporary) / "results"
            with self.assertRaises(KeyboardInterrupt):
                self.run_rig(arguments(output_dir=folder))
            self.assertIn("KeyboardInterrupt", (folder / "results.html").read_text(encoding="utf-8"))
        self.assert_restored()

    def test_rejected_window_is_repeated_whole_and_marked_in_results(self):
        measure = tool.measure_point
        calls = 0

        def first_window_spike(source, load, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls != 1:
                return measure(source, load, *args, **kwargs)
            read = load.read
            readings = iter((998, 1003, 808))

            def spike_read():
                self.rig.current_query_override = next(readings, 1000)
                try:
                    return read()
                finally:
                    self.rig.current_query_override = None

            with patch.object(load, "read", side_effect=spike_read):
                return measure(source, load, *args, **kwargs)

        with TemporaryDirectory() as temporary, patch.object(tool, "measure_point", side_effect=first_window_spike):
            folder = Path(temporary) / "results"
            self.run_rig(arguments(output_dir=folder, voltages=(20,), currents=(1, 2), seconds=10))
            with (folder / "results.csv").open(newline="", encoding="utf-8") as output:
                points = list(csv.DictReader(output))
            self.assertEqual([int(p["attempts"]) for p in points], [2, 1])
            self.assertAlmostEqual(float(points[0]["source_wh"]), 20 * 10 / 3600, places=10)
            self.assertAlmostEqual(float(points[0]["load_wh"]), 19.9 * 10 / 3600, places=10)
            self.assertEqual(float(points[0]["window_s"]), 10)
            self.assertIn("Attempts", (folder / "results.html").read_text(encoding="utf-8"))
            events = [json.loads(line) for line in (folder / "debug.jsonl").read_text(encoding="utf-8").splitlines()]
        starts = [e for e in events if e["event"] == "point_start"]
        self.assertEqual([(e["set_a"], e["attempt"]) for e in starts], [(1, 1), (1, 2), (2, 1)])
        self.assertEqual(sum(e["event"] == "point_rejected" for e in events), 1)
        self.assertTrue(any(e["event"] == "sample" and e["load_a"] == 0.808 for e in events))
        rejected = next(i for i, e in enumerate(events) if e["event"] == "point_rejected")
        repeated = next(i for i, e in enumerate(events) if e["event"] == "point_start" and e["attempt"] == 2)
        self.assertTrue(any(e["event"] == "shutdown_end" and e["success"] for e in events[rejected:repeated]))
        self.assertEqual(sum(e["event"] == "point_complete" for e in events), 2)
        self.assert_restored()

    def test_persistent_operating_point_error_stops_after_retry_limit(self):
        with TemporaryDirectory() as temporary, patch.object(tool, "measure_point", side_effect=tool.OperatingPointError("persistent deviation")) as measure:
            folder = Path(temporary) / "results"
            with self.assertRaisesRegex(tool.OperatingPointError, "persistent deviation"):
                self.run_rig(arguments(output_dir=folder, voltages=(20,), currents=(1,)))
            with (folder / "results.csv").open(newline="", encoding="utf-8") as output:
                self.assertEqual(list(csv.DictReader(output)), [])
        self.assertEqual(measure.call_count, 2)
        self.assert_restored()

    def test_point_retries_can_be_disabled(self):
        with patch.object(tool, "measure_point", side_effect=tool.OperatingPointError("deviation")) as measure:
            with self.assertRaisesRegex(tool.OperatingPointError, "deviation"):
                self.run_rig(arguments(voltages=(20,), currents=(1,), point_retries=0))
        self.assertEqual(measure.call_count, 1)
        self.assert_restored()

    def test_protection_errors_do_not_repeat_point(self):
        with patch.object(tool, "measure_point", side_effect=RuntimeError("OCP/2")) as measure:
            with self.assertRaisesRegex(RuntimeError, "OCP/2"):
                self.run_rig(arguments(voltages=(20,), currents=(1,)))
        self.assertEqual(measure.call_count, 1)
        self.assert_restored()

    def test_failed_off_prevents_another_point_attempt(self):
        def reject_and_lose_off(*args, **kwargs):
            self.rig.fail_off = True
            raise tool.OperatingPointError("deviation")

        with patch.object(tool, "measure_point", side_effect=reject_and_lose_off) as measure:
            with self.assertRaisesRegex(RuntimeError, "OFF could not be verified"):
                self.run_rig(arguments(voltages=(20,), currents=(1,)))
        self.assertEqual(measure.call_count, 1)
        self.assertEqual(self.rig.writes.count((18, 1)), 1)
        self.assertFalse(self.rig.load_on)

    def test_measurement_timeout_restores_source_and_reports_unverified_load_off(self):
        measure = tool.measure_point

        def lose_replies(*args, **kwargs):
            self.rig.suppress_replies = True
            return measure(*args, **kwargs)

        with TemporaryDirectory() as temporary, patch.object(tool, "measure_point", side_effect=lose_replies):
            folder = Path(temporary) / "results"
            with self.assertRaises(TimeoutError):
                self.run_rig(arguments(output_dir=folder))
            self.assertIn("no reply", (folder / "results.html").read_text(encoding="utf-8"))
        self.assert_restored()
        self.assertIn("OFF sent without verification", self.out.getvalue())
        self.assertCountEqual(self.rig.closed, ["source", "load"])
        self.assertEqual(self.rig.writes.count((18, 1)), 1)

    def test_partial_protection_update_is_restored_without_enabling_source(self):
        write = self.rig.instrument.write_register

        def fail_new_ocp(address, value):
            if (address, value) == (83, 2310):
                raise TimeoutError("OCP write failed")
            write(address, value)

        with TemporaryDirectory() as temporary, patch.object(self.rig.instrument, "write_register", side_effect=fail_new_ocp):
            with self.assertRaisesRegex(TimeoutError, "OCP write failed"):
                self.run_rig(arguments(output_dir=Path(temporary) / "results"))
        self.assert_restored()
        self.assertNotIn((18, 1), self.rig.writes)

    def test_invalid_cli_options_are_rejected_before_connecting(self):
        for option in (["--ovp", "5.5"], ["--ocp", "0.15"],
                       ["--current-tolerance", "nan"], ["--voltage-tolerance", "1"],
                       ["--settle-timeout", "nan"], ["--settle-timeout", "2"],
                       ["--point-retries", "-1"]):
            with self.subTest(option=option), patch.object(sys, "argv", ["tool"] + option), patch.object(tool, "run") as run:
                with self.assertRaises(SystemExit) as stopped:
                    tool.main()
                self.assertEqual(stopped.exception.code, 2)
                run.assert_not_called()

    def test_restore_failure_still_restores_other_registers(self):
        settings = self.source.snapshot_settings()
        self.configured()
        self.source.set_voltage(20)
        self.rig.fail_restore = 8
        with self.assertRaisesRegex(RuntimeError, "register 8 could not be restored"):
            tool.shutdown(self.source, self.load, settings)
        self.assertEqual(self.rig.regs[18], 0)
        self.assertFalse(self.rig.load_on)
        for address in (9, 82, 83):
            self.assertEqual(self.rig.regs[address], settings[address])

    def test_failed_source_off_skips_restoration_but_attempts_load_off(self):
        settings = self.source.snapshot_settings()
        self.configured()
        self.rig.fail_off = True
        before = dict(self.rig.regs)
        with self.assertRaisesRegex(RuntimeError, "settings not restored"):
            tool.shutdown(self.source, self.load, settings)
        self.assertEqual(self.rig.regs, before)
        self.assertFalse(self.rig.load_on)

    def test_cleanup_failure_does_not_hide_original_error(self):
        self.rig.fail_input = True
        with patch.object(self.rig.module, "get_input_voltage", side_effect=self.fail_input_then_off):
            with self.assertRaisesRegex(TimeoutError, "original input error"):
                self.run_rig(arguments())
        self.assertIn("source OFF failed", self.out.getvalue())

    def fail_input_then_off(self):
        self.rig.fail_off = True
        raise TimeoutError("original input error")


if __name__ == "__main__":
    unittest.main()
