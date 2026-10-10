# C67 / C68 passive-value assessment

2026-10-10. Recommend C67 = 220 nF and C68 = 1 uF in the existing topology. Requested assessment only; CAD/BOM values remain unchanged, no fresh ERC or hardware measurements claimed.

## Manufacturer basis

TI LM74700-Q1, SNOSD17G Rev G, December 2020, section 10.1.1.2.3 specifies minimum 100 nF for VCAP and output; VCAP should also be at least ten times MOSFET Ciss. Table 10-1 uses 1 uF minimum in its particular application example; this is not an extra universal product requirement. Sections 6.5 and 12 cover pump characteristics and layout. Checked 2026-10-10: https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf

AOS AON7528 Rev 1.0 October 2023, p.2 lists typical Ciss = 2895 pF. Ten times this is 28.95 nF, so TI's 100 nF floor controls; typical Ciss is not a guaranteed worst-case bound. Checked 2026-10-10: https://www.aosmd.com/res/data_sheets/AON7528.pdf

## Engineering assessment

- C67 is VCAP-to-ANODE/F5_RAW, not ground. Nominal 100 nF has no tolerance/DC-bias reserve above TI's floor. At 220 nF, -10% tolerance and -15% temperature shift leave 168.3 nF before bias/aging. Retain a suitable 50 V X7R candidate in the existing 0603 footprint and check exact effective capacitance at up to 13.9 V differential. Voltage rating alone is insufficient proof.
- Larger C67 increases pump startup time. Illustrative constant-current C*dV/I at 6.6 V and 300 uA is 2.2 ms for 100 nF and 4.84 ms for 220 nF; neither is a guaranteed startup time. The existing MOSFET body diode supplies the forward path before gate enhancement. This trade-off does not justify redesign.
- C68 is F5_5V_OUT-to-PGND after Q10. Nominal 1 uF provides more local charge and margin above the controller's minimum. Check exact X7R effective capacitance around 5 V and voltage rating against permitted external backdrive; preserve compact local placement. A compatible 0603 part can be selected without changing topology.
- This is not meaningful 2 A hold-up: ideal 1 uF allows 0.125 us for a 0.25 V droop. Output response and stability remain hardware qualification matters.

## Follow-through

Both proposed changes are reasonable small passive adjustments, preserving all nets and F0/F5 population. No final MPN or supplier price/stock/MOQ was selected or verified. On implementation, update CAD procurement fields and split the BOM group, export XML, verify no connectivity/unrelated-property changes, run ERC and inspect the diff. No PCB exists; DRC/parity not applicable yet. The unavailable live PCB IPC endpoint does not prevent file-based schematic editing through Konnect.
