# Diagnostic trace follow-up - 2026-11-15

The owner reported a 187 mA ATORCH reading after the 100 mA point had settled,
followed by a successful run of that point. The saved successful CSV at
`../rk6006-atorch-20261115-184534-884366/results.csv` records source current
0.0975786584 A and load current 0.1000373044 A, source voltage 4.99 V and load
voltage 4.984887025 V. These reported averages explain the calculated 102.4147%
ratio; they do not establish calibration, USB return-path, communication or
physical load behavior as the cause. No per-sample/raw traffic evidence exists
for those original runs. The intermittent spike remains unconfirmed.

## Change

Normal measurement runs automatically create `debug.jsonl` before initialization,
in the same results directory as CSV/HTML. Each event is flushed with a UTC
timestamp and monotonic elapsed time. Recorded events cover RK6006 raw register
reads/write verification, ATORCH raw TX/RX and parsed frames/query values,
settling/measurement phases, paired readings before validation (including rejected
ones), errors, final OFF/settings restoration and session status. PX100 response
validation is explicitly labeled framing-only, not checksum validation; ATORCH
report checksums are checked. The error message also includes both instruments'
paired readings. `--probe` remains read-only and creates no results/debug folder.
Logging write failures disable logging and do not prevent OFF commands.

No operating-point tolerance, integration or measurement protocol was changed
to conceal the reported spike. The raw trace is intended to identify what data
actually arrived and compare both instruments at the rejected sample.

## Offline verification

Windows / Python 3.12.10:

```powershell
python -B -m unittest discover -s .\hardware\v4\tools\tests -p test_measure_efficiency.py -v
git diff --check
```

All 41 behavioral tests passed; full output is in `tests.log`. Added coverage
includes a 187 mA reply after settling, preservation of raw reply bytes and both
paired values, trace coverage of initialization failure and final restoration,
bad checksums, valid JSON for nonfinite readings, and a simulated full disk
without suppressing OFF. Existing complete-sweep/CSV/HTML checks still pass.

`simulated-spike/` contains a deliberately simulated run, not hardware evidence:
153 debug events were parsed and inspected, including the rejected 187 mA
sample and final shutdown. `simulated-console.txt` records its console output.

Source SHA256:
`AC2427942A7BA205A64C0564ECB69B27D13251615AC0D0278BDF6D56B3238FBD`.

Protocol framing/checksum reference:
[DL24 author implementation](https://github.com/tshaddack/dl24/blob/master/dl24.py).
No physical serial port was opened and no live instrument setting/output was
changed during this follow-up. A new owner run with the trace is still needed.
