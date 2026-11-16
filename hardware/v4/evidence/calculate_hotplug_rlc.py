"""Parameterized linear hot-plug screen, not a hardware qualification.

Requires Python 3 and numpy. No CAD reads/writes. See phase2-6-hotplug-envelope.md
for circuit, assumptions, manufacturer references and acceptance boundaries.
"""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VS = 21.0


def solve(l_uh, cin_uf, cd_uf, rs, rd, samples=20001):
    """Exact modal response sampled in time; state is [iL, VIN, Vd]."""
    inductance, cin, cd = l_uh * 1e-6, cin_uf * 1e-6, cd_uf * 1e-6
    matrix = np.array([[-rs / inductance, -1 / inductance, 0],
                       [1 / cin, -1 / (rd * cin), 1 / (rd * cin)],
                       [0, 1 / (rd * cd), -1 / (rd * cd)]])
    poles, vectors = np.linalg.eig(matrix)
    assert np.all(poles.real < 0), "Passive model must be stable"
    steady = np.array([0, VS, VS])
    amplitudes = vectors * np.linalg.solve(vectors, -steady)[None, :]
    end = max(200e-6, 12 / min(-poles.real))
    times = np.linspace(0, end, samples)
    states_complex = steady[:, None] + np.sum(
        amplitudes[:, :, None] * np.exp(poles[None, :, None] * times), axis=1)
    assert np.max(np.abs(states_complex.imag)) < 1e-7
    states = states_complex.real
    il, vin, vd = states
    assert np.max(np.abs(states[:, 0])) < 1e-7
    # Independent KCL/KVL check of the modal derivative at all sample points.
    derivative = np.sum(amplitudes[:, :, None] * poles[None, :, None]
                        * np.exp(poles[None, :, None] * times), axis=1).real
    residual = np.max(np.abs(derivative - (matrix @ states
                      + np.array([VS / inductance, 0, 0])[:, None])))
    assert residual < 1e-5 * max(1, np.max(np.abs(derivative)))
    pd = (vin - vd) ** 2 / rd
    input_energy = np.trapz(VS * il, times)
    dissipated = np.trapz(rs * il ** 2 + pd, times)
    stored = (inductance * il[-1] ** 2 + cin * vin[-1] ** 2
              + cd * vd[-1] ** 2) / 2
    balance = abs(input_energy - dissipated - stored) / max(abs(input_energy), 1e-12)
    assert balance < 0.002, "Time grid too coarse for energy verification"
    return dict(L_uH=l_uh, Cin_uF=cin_uf, Cd_uF=cd_uf, Rs_ohm=rs, Rd_ohm=rd,
                peak_V=float(vin.max()), peak_resistor_W=float(pd.max()),
                resistor_energy_mJ=float(np.trapz(pd, times) * 1e3),
                energy_balance_relative=balance, end_us=end * 1e6,
                samples=samples)


def undamped_peak(l_uh, cin_uf, rs):
    """Independent second-order series-RLC step peak without damping branch."""
    zeta = rs / 2 * np.sqrt(cin_uf / l_uh)
    return float(VS if zeta >= 1 else VS *
                 (1 + np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2))))


def main():
    screen = json.loads((HERE / 'phase2-5-hotplug-screen.json').read_text())
    # Use the prior sensitivity value, never relabel it as guaranteed Cmin.
    cd_low = screen['kemet_Ceff_sensitivity']['combined_sensitivity_uF']
    rows = [solve(*args) for args in itertools.product(
        [0.1, 1.0, 10.0], [0.1, 1.0, 10.0, 30.0],
        [cd_low, 2.2, 2.783], [0.05, 0.2], [1.862, 2.142])]
    worst = max(rows, key=lambda row: row['peak_V'])
    refined = solve(*(worst[key] for key in
                      ['L_uH', 'Cin_uF', 'Cd_uF', 'Rs_ohm', 'Rd_ohm']), samples=40001)
    convergence = abs(worst['peak_V'] - refined['peak_V'])
    assert convergence < 0.01
    worst_power = max(rows, key=lambda row: row['peak_resistor_W'])
    worst_energy = max(rows, key=lambda row: row['resistor_energy_mJ'])
    power_refined = solve(*(worst_power[key] for key in
                            ['L_uH', 'Cin_uF', 'Cd_uF', 'Rs_ohm', 'Rd_ohm']), samples=40001)
    assert abs(power_refined['peak_resistor_W'] - worst_power['peak_resistor_W']) < 0.1
    # Independently compare a two-state modal solution with the RLC formula.
    analytic = undamped_peak(1, 10, 0.2)
    a = np.array([[-0.2 / 1e-6, -1 / 1e-6], [1 / 10e-6, 0]])
    ev, vec = np.linalg.eig(a)
    amp = vec * np.linalg.solve(vec, -np.array([0, VS]))[None, :]
    t = np.linspace(0, 200e-6, 40001)
    curve = VS + np.sum(amp[1, :, None] * np.exp(ev[:, None] * t), axis=0).real
    assert abs(curve.max() - analytic) < 0.001
    result = dict(date='2026-10-10', verdict='PARAMETER_SCREEN_ONLY_NO_ACCEPTANCE',
                  model='21 V ideal source -> Rs+L -> Cin || (Rd series Cd); no load',
                  numpy_version=np.__version__, case_count=len(rows),
                  prior_screen_sha256=hashlib.sha256(
                      (HERE / 'phase2-5-hotplug-screen.json').read_bytes()).hexdigest(),
                  worst_voltage=worst, refined_worst=refined,
                  worst_resistor_power=worst_power, worst_resistor_energy=worst_energy,
                  refined_power_case=power_refined,
                  refinement_peak_difference_V=convergence,
                  independent_no_branch_peak_V=analytic,
                  independent_modal_peak_V=float(curve.max()),
                  max_energy_balance_relative=max(x['energy_balance_relative'] for x in rows),
                  rows=rows)
    (HERE / 'phase2-6-hotplug-rlc.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in
                      ['case_count', 'worst_voltage', 'refinement_peak_difference_V',
                       'max_energy_balance_relative']}, indent=2))


if __name__ == '__main__':
    main()
