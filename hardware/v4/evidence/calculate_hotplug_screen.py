"""Reproduce phase 2.5 component screening; no CAD writes or hardware claims.

The 21 V ideal-step model excludes cable inductance and contact bounce. Typical
capacitor curves and assumed margins are not guaranteed production bounds.
Run from any directory; writes the adjacent phase2-5-hotplug-screen.json.
"""
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
v = 21.0
r = 2.0
c = 2.2e-6
# Vishay CRCW1206-HP J tolerance and +/-200 ppm/K; screening range -55..125 C.
# This is a screening range, not an approved UPS ambient specification.
r_min = r * 0.95 * (1 - 200e-6 * 100)
r_max = r * 1.05 * (1 + 200e-6 * 100)
# X7R tolerance and temperature only, at its 1 Vrms reference condition.
c_max = c * 1.10 * 1.15
peak = v * v / r_min
energy = c_max * v * v / 2
duration = r_max * c_max / 2
age_years = 10
age_hours = age_years * 365.25 * 24
age_factor = 1 - 0.03 * math.log10(age_hours / 48)
# KEMET typical curve at 21 V is approximately -11..-13%. Use -15% as
# an engineering screening allowance, not a manufacturer guaranteed bound.
bias_factor = 0.85
ac_factor = 0.95  # assumed allowance; published small-signal curve is typical
c_screen = c * 0.90 * 0.85 * bias_factor * age_factor * ac_factor
derated_power_125c = 0.75 * (155 - 125) / (155 - 70)
source_files = {
    "vishay_20043": "crcwhpe3.pdf",
    "panasonic_pulse_reference": "erjp-pulse.pdf",
    "murata_12A": "grm32er72a225ka35-12a.pdf",
    "kemet_exact_spec": "c1210c225k1ractu.pdf",
}
manifest = {}
for name, filename in source_files.items():
    path = HERE / "references" / filename
    manifest[name] = {
        "local_path": str(path.relative_to(HERE.parent)).replace("\\", "/"),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }
result = {
    "date": "2026-10-10",
    "verdict": "SCREENING_ONLY_NOT_COMPONENT_ACCEPTANCE",
    "source_manifest": manifest,
    "model": "Ideal 0-to-21 V step into series 2 ohm / shunt 2.2 uF; initially discharged",
    "nominal": {"peak_A": v / r, "peak_W": v * v / r,
                "tau_us": r * c * 1e6, "energy_mJ": c * v * v / 2 * 1e3},
    "screening_envelope": {
        "resistor_min_ohm": r_min, "resistor_max_ohm": r_max,
        "cap_max_uF_reference_AC_only": c_max * 1e6,
        "peak_A": v / r_min, "peak_W": peak,
        "energy_mJ": energy * 1e3,
        "same_peak_equal_energy_rectangle_us": duration * 1e6,
        "rectangle_duration_rounded_up_us": 3.0,
        "vishay_1206_single_curve_conservative_read_W_at_3us": 500,
        "vishay_1206_continuous_curve_conservative_read_W_at_3us": 300,
        "curve_reads": "Manual conservative reads from 20043 Rev 17-Mar-2026 p.5; not guaranteed digitized limits",
        "peak_below_screening_curve_reads": peak < 300,
        "pulse_average_W_at_100_Hz": energy * 100,
        "pulse_average_W_at_1000_Hz": energy * 1000,
        "rated_average_W_at_125C": derated_power_125c,
        "average_only_frequency_ceiling_Hz_at_125C": derated_power_125c / energy,
    },
    "kemet_Ceff_sensitivity": {
        "part": "C1210C225K1RACTU", "nominal_uF": 2.2,
        "tolerance_low_factor": 0.9, "temperature_low_factor": 0.85,
        "assumed_bias_low_factor_21V": bias_factor,
        "assumed_AC_low_factor": ac_factor,
        "assumed_age_years": age_years, "aging_reference_hours": 48,
        "aging_loss_per_decade_hours": 0.03, "age_factor": age_factor,
        "combined_sensitivity_uF": c_screen * 1e6,
        "warning": "Typical curves and multiplicative assumptions; not a guaranteed minimum or a damping acceptance test",
    },
    "unresolved": [
        "Supported cable/source and repeated-contact waveforms have not been measured",
        "Capacitor minimum effective capacitance required for actual damping is not established",
        "CRCW1206-HP pulse peak temperature margin and assembled-board thermal conditions need qualification",
        "KEMET exact lifecycle, land acceptance and live critical sourcing remain open",
        "Murata GRM32ER72A225KA35 is NRND in live SimSurfing; do not select for this new branch",
    ],
}
assert duration <= 3e-6
assert peak > result["nominal"]["peak_W"]
assert energy > result["nominal"]["energy_mJ"] / 1e3
out = HERE / "phase2-5-hotplug-screen.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"Saved {out.name}; peak={peak:.2f} W; rectangle={duration*1e6:.3f} us; "
      f"Ceff sensitivity={c_screen*1e6:.3f} uF; SCREENING ONLY")
