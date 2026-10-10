"""First-order Phase 0 estimates; not a converter or thermal simulation.

Run with Python 3 from any directory. Recreates operating-corners.csv beside
this file. Assumes CCM, triangular ripple, 750 kHz, -20% L tolerance and 90%
efficiency where power conversion is used to estimate average input current.
L bias, core loss, semiconductor loss and control-loop transients are excluded.
"""
import csv
import math
from pathlib import Path

FREQUENCY = 750_000.0
L_NOMINAL = 2.2e-6
L_MINIMUM = L_NOMINAL * 0.8
EFFICIENCY = 0.90
DCR_TYPICAL_20C = 0.0045

# Average inductor current is output current in buck, input current in boost.
# These are deliberately independent corners, not simultaneous ratings.
corners = [
    ("forward buck, 4S SYS", 24.0, 12.0, 5.0, "buck"),
    ("forward buck, low 2S SYS", 12.0, 6.4, 5.0, "buck"),
    ("forward boost, 4S at 5V input", 5.0, 16.8, 3.3, "boost"),
    ("forward boost, 4S at 12V input", 12.0, 16.8, 3.3, "boost"),
    ("OTG buck, full 4S to 12V", 16.8, 12.0, 3.32, "buck"),
    ("OTG boost, low 2S to 12V - reject rating", 6.4, 12.0,
     12.0 * 3.32 / (EFFICIENCY * 6.4), "boost"),
]

rows = []
for name, vin, vout, average, mode in corners:
    numerator = (vout * (vin - vout) / vin if mode == "buck"
                 else vin * (vout - vin) / vout)
    ripple_nominal = numerator / (FREQUENCY * L_NOMINAL)
    ripple_minimum = numerator / (FREQUENCY * L_MINIMUM)
    rms = math.sqrt(average ** 2 + ripple_minimum ** 2 / 12)
    rows.append({
        "corner": name, "source_V": vin, "destination_V": vout,
        "I_L_average_A": round(average, 4),
        "ripple_nominal_L_App": round(ripple_nominal, 4),
        "ripple_minus20pct_L_App": round(ripple_minimum, 4),
        "peak_minus20pct_L_A": round(average + ripple_minimum / 2, 4),
        "rms_minus20pct_L_A": round(rms, 4),
        "copper_loss_typical_20C_W": round(rms ** 2 * DCR_TYPICAL_20C, 4),
    })

with Path(__file__).with_name("operating-corners.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
for row in rows:
    print(row)
