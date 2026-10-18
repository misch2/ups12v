"""Review-only projections/calculations from accepted exports; no CAD/native imports.

Run from repository root with python -B <this file>, after the toolkit creates
actual-object-screen-final.json. Writes only this evidence directory. Does not
export fabrication data or change authoritative BOM/CAD.
"""
import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
V4 = ROOT / 'hardware/v4'
E = V4 / 'evidence'
PCB_HASH = '4eb7bd2c72fec3cf49d3746250864b5237e7919760ebdbc3647cbc0101fa8737'
F5 = set('U7 U8 Q10 L3 R60 R61 R62 R63 C60 C61 C62 C63 C64 C65 C66 C67 C68 C69 J8'.split())
BULK = set('C20 C22 C24 C25'.split())
BARE = set('TP5 TP6 TP7 TP8 TP13 TP14 TP15 TP16 TP17'.split())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def field(f):
    return f.get('text', {}).get('text', {}).get('text', '')


def sortref(ref):
    m = re.fullmatch(r'([A-Z]+)(\d+)', ref)
    return (m[1], int(m[2]))


def main():
    manifest_path = E / 'phase4-21-production-adoption/accepted-installed-baseline.json'
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest['hashes'].items():
        assert digest(V4 / 'ups_v4' / name) == expected, name
    assert manifest['hashes']['ups12v_v4.kicad_pcb'] == PCB_HASH
    protected = {str(p.relative_to(ROOT)): digest(p) for p in (V4 / 'ups_v4').rglob('*')
                 if p.is_file() and (p.suffix in {'.kicad_pcb', '.kicad_sch', '.kicad_pro', '.kicad_dru', '.kicad_mod', '.kicad_sym'}
                                     or p.name in {'fp-lib-table', 'sym-lib-table'})}
    protected['hardware/v4/V4_BOM_REVIEW.md'] = digest(V4 / 'V4_BOM_REVIEW.md')
    guard_path = OUT / 'preservation-before.json'
    if guard_path.exists():
        assert json.loads(guard_path.read_text()) == protected, 'Protected source drift'
    else:
        save(guard_path.name, protected)

    # Historical BOM inventory supplies recorded identities, never new selections.
    bom = (V4 / 'V4_BOM_REVIEW.md').read_text(encoding='utf-8')
    inventory = {}
    for section in re.split(r'(?m)^### ', bom)[1:]:
        heading = section.splitlines()[0].split(' — ')[0]
        if not re.fullmatch(r'[A-Z]+\d+(?:, [A-Z]+\d+)*', heading):
            continue
        for ref in heading.split(', '):
            inventory[ref] = section.split('\n## ')[0]
    accepted_projection = json.loads((E / 'phase4-19-final-audit/population.json').read_text())
    assert set(accepted_projection['f5_only']) == F5
    assert accepted_projection['schematic_sha256'] == manifest['hashes']['ups12v_v4.kicad_sch']
    special = {
        'J4': ('JST', 'S6B-XH-A(LF)(SN)', 'Newest BOM Phase4.3 cleanup; LCSC C157919; dated 2026-10-11'),
        'J6': ('JST', 'S2B-XH-A-1(LF)(SN)', 'Newest BOM Phase4.3 cleanup; LCSC C163035; dated 2026-10-11'),
        'Q1': ('Alpha & Omega Semiconductor', 'AON7528', 'Current BOM Phase4.3 and Phase4.19 independent review; accepted value AON7528'),
        'Q2': ('Alpha & Omega Semiconductor', 'AON7528', 'Current BOM Phase4.3 and Phase4.19 independent review; accepted value AON7528'),
        'U3': ('Texas Instruments', 'TPS62933DRLR', 'Current BOM normal-buck selection and Phase4.19 sourcing snapshot'),
    }
    rows = []
    for f in manifest['footprints'].values():
        ref = field(f['referenceField'])
        value = field(f['valueField'])
        fields = {i['name']: field(i) for i in f['definition']['items'] if 'name' in i}
        hist = inventory.get(ref, '')
        mpn = fields.get('MPN') or fields.get('Manufacturer_Part_Number') or 'OPEN'
        maker = fields.get('Manufacturer') or fields.get('Manufacturer_Name') or 'OPEN'
        identity_basis = 'Accepted PCB fields'
        if mpn == 'OPEN':
            match = re.search(r'Manufacturer / exact recorded MPN: (.*?) / `([^`]+)`', hist)
            if match and match[2] != 'OPEN':
                maker, mpn = match.groups()
                identity_basis = 'Retained BOM inventory, not a fresh qualification'
        if ref in special:
            maker, mpn, identity_basis = special[ref]
        fp = f['definition']['id']
        footprint = fp['libraryNickname'] + ':' + fp['entryName']
        structural = bool(f.get('attributes', {}).get('excludeFromBillOfMaterials'))
        if structural:
            role = 'PCB feature; no fitted component'
            maker, mpn = 'N/A', 'N/A'
        elif ref in BARE:
            role = 'Bare test pad; no fitted component'
            maker, mpn = 'N/A', 'N/A'
        else:
            role = 'Component'
        rating = fields.get('Parameters', '')
        recorded = re.search(r'Historical Bought / Parameters: `[^`]*` / `([^`]+)`', hist)
        if recorded and recorded[1] and recorded[1] not in rating:
            rating += '; ' + recorded[1]
        rating = (value + '; ' + rating.strip('; ')).rstrip('; ')
        if ref in {'Q1', 'Q2', 'Q10'}:
            rating += '; AON7528: 30V VDS, 20V gate rating; existing exposed-land deviation owner accepted for prototype2026-10-18'
        if ref == 'IC1':
            rating += '; BQ25798: 3.6-24V operating input; 30V abs max; 1-4 cells; 5A charger IC capability, not board load approval (TI product page checked2026-10-18)'
        if ref in {'U3', 'U7'}:
            rating += '; 3.8-30V input; 3A IC capability, not board thermal approval (TI TPS62933 product page checked2026-10-18)'
        if ref == 'U8':
            rating += '; 3.2-65V controller operating range; external MOSFET limits still apply (TI exact LM74700QDBVRQ1 page checked2026-10-18)'
        if ref in {'J1', 'J3'}:
            rating += '; retained Nano-Fit reference8A with20AWG, application-dependent; prototype tolerance risk owner accepted2026-10-18'
        if ref in {'J2', 'J8'}:
            rating += '; retained Nano-Fit reference7.75A with20AWG, application-dependent; no parallel contacts; prototype tolerance risk owner accepted2026-10-18'
        source = 'Retained source identities only; live price/MOQ/stock not refreshed in 4.22A'
        if mpn.startswith('OPEN'):
            source = 'Exact orderable MPN OPEN; supplier basket/price/MOQ/stock OPEN'
        if structural or ref in BARE:
            source = 'Not procured as a PCB component'
        if ref == 'U8':
            source = '2026-10-18 Phase4.19 LCSC C2941042 snapshot: out of stock; not refreshed in 4.22A'
        elif ref in {'U3', 'U7', 'J7'}:
            source = '2026-10-18 Phase4.19 LCSC snapshot: listed in stock; not refreshed in 4.22A'
        if ref == 'L1':
            source += '; Eaton DR125-2R2-R is a historical source-link candidate only, not a frozen MPN'
        hist_sources = re.findall(r'https?://[^\s)]+', hist)
        rows.append(dict(reference=ref, value_function=value, role=role,
                         manufacturer=maker, known_mpn=mpn, identity_basis=identity_basis,
                         footprint=footprint, component_ratings_recorded=rating,
                         rating_status='Recorded candidates only; missing voltage/power/tolerance/Ceff remain OPEN',
                         approval_status=fields.get('ApprovalStatus', 'See current BOM; no new approval'),
                         sourcing_status=source, recorded_source=fields.get('Source', ''),
                         recorded_lcsc=fields.get('LCSC Part', ''),
                         historical_bom_sources='; '.join(hist_sources),
                         historical_bought=fields.get('Bought', ''),
                         population_group='F5 only' if ref in F5 else 'Common F0/F5',
                         F0_state='DNP' if ref in F5 | BULK else ('PCB_FEATURE' if structural or ref in BARE else 'FITTED'),
                         F5_state='DNP' if ref in BULK else ('PCB_FEATURE' if structural or ref in BARE else 'FITTED'),
                         raw_accepted_fields=fields))
    rows.sort(key=lambda r: sortref(r['reference']))
    assert len(rows) == 154 and {r['reference'] for r in rows} >= F5 | BULK | BARE
    save('population-detail.json', dict(review_only=True, pcb_sha256=PCB_HASH,
                                      source_manifest_sha256=digest(manifest_path), components=rows))
    summaries = {}
    for variant in ('F0', 'F5'):
        projected = []
        for r in rows:
            item = {k: v for k, v in r.items() if k not in {'F0_state', 'F5_state', 'raw_accepted_fields'}}
            item.update(state=r[variant + '_state'], fitted_quantity=int(r[variant + '_state'] == 'FITTED'))
            projected.append(item)
        with (OUT / (variant + '-population-review.csv')).open('w', newline='', encoding='utf-8-sig') as handle:
            w = csv.DictWriter(handle, fieldnames=list(projected[0]))
            w.writeheader()
            w.writerows(projected)
        summaries[variant] = {s: [r['reference'] for r in projected if r['state'] == s]
                              for s in ('FITTED', 'DNP', 'PCB_FEATURE')}
    assert set(summaries['F0']['DNP']) == F5 | BULK
    assert set(summaries['F5']['DNP']) == BULK
    assert len(summaries['F5']['FITTED']) - len(summaries['F0']['FITTED']) == 19
    save('population-summary.json', summaries)
    snapshot = json.loads((E / 'phase4-21-final-production-native/snapshot.json').read_text())
    # Transcribe accepted exported coordinates only; no new geometry analysis.
    pins = [dict(reference=p['ref'], pin=p['pin'], net=p['net'],
                 top_view_x_mm=p['position'][0], top_view_y_mm=p['position'][1])
            for p in snapshot['pads'].values()
            if p['ref'] in {'J1', 'J2', 'J3', 'J4', 'J6', 'J7', 'J8', 'SW1', 'SW2'} | {r for r in BARE} | {'TP1', 'TP3', 'TP4'}
            and p['pin']]
    pins.sort(key=lambda p: (sortref(p['reference']), p['pin']))
    with (OUT / 'assembly-pinmap-review.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pins[0]))
        writer.writeheader()
        writer.writerows(pins)

    # Reuse accepted scalar paths, not route search/net resistance extraction.
    eng = json.loads((E / 'phase4-17-review/engineering.json').read_text())
    paths = eng['paths']
    rho = 1.724e-8
    hot = 1 + 0.00393 * (125 - 20)
    def via(d_mm, p_um):
        d, t = d_mm * 1e-3, p_um * 1e-6
        return rho * 0.0016 / (math.pi * t * (d + t))
    assert math.isclose(via(.4, 25), eng['current_screen']['via_single_R20_ohm'], rel_tol=1e-12)
    branch_parts = {
        'F5 SYS tap to U7 VIN': (sum(paths[n]['R20_ohm'] for n in ('SYS_B_bridge', 'SYS_local_feed', 'U7_VIN')),
                                paths['SYS_In2_branch']['R20_ohm'], 3, eng['current_screen']['SYS_branch_R20_ohm']),
        'F5 RAW pickup to J8, Q10 excluded': (sum(paths[n]['R20_ohm'] for n in ('RAW_to_Q10', 'Q10_to_output_vias')),
                                            paths['output_to_J8']['R20_ohm'], 1, eng['current_screen']['output_copper_R20_ohm']),
    }
    branch_results = []
    for name, (outer, inner, pair_transitions, original) in branch_parts.items():
        assert math.isclose(outer + inner + pair_transitions * via(.4, 25) / 2, original, rel_tol=1e-12)
        for inner_um, plating_um in ((35, 25), (35, 18), (30.5, 25), (30.5, 18), (17.5, 25), (17.5, 18), (15.2, 25), (15.2, 18)):
            resistance = outer + inner * 35 / inner_um + pair_transitions * via(.4, plating_um) / 2
            branch_results.append(dict(path=name, inner_um=inner_um, outer_um=35, plating_um=plating_um,
                                       R20_mohm=resistance * 1000, drop2A20_mV=resistance * 2000,
                                       loss2A20_mW=resistance * 4000, drop2A125_mV=resistance * 2000 * hot,
                                       loss2A125_mW=resistance * 4000 * hot,
                                       conditional_J8_low_V=(4.81714 - resistance * 2 * hot) if name.startswith('F5 RAW') else None))
    sheet = []
    for label, width, current in [('SYS/BATTERY trunk', 3, 3.74), ('VIN1/VBUS distribution', 2.2, 3.3),
                                  ('F5 OUT trunk', 2, 2), ('F5 SYS branch', 1.5, 2)]:
        for t in (35, 30.5, 17.5, 15.2):
            r = rho * .01 / (width * 1e-3 * t * 1e-6)
            sheet.append(dict(path=label, width_mm=width, inner_um=t, length_mm=10, current_A=current,
                              R20_mohm=r * 1000, drop20_mV=r * current * 1000,
                              loss20_mW=r * current**2 * 1000, loss125_mW=r * current**2 * hot))
    barrels = [dict(drill_mm=d, plating_um=t, barrel_R20_mohm=via(d, t) * 1000,
                    N_equal=n, array_R20_mohm=via(d, t) * 1000 / n)
               for d, ns in ((.3, (2, 6, 12)), (.4, (2, 3, 4))) for t in (25, 18) for n in ns]
    save('copper-sensitivity.json', dict(review_only=True, pcb_sha256=PCB_HASH, rho20_ohm_m=rho,
                                       temperature_coefficient_per_K=.00393, hot_factor125=hot,
                                       assumptions='35um outer fixed; 1.6mm barrel; nominal finished bore; equal parallel sharing; '
                                       '30.5um is owner-reported processed1oz calculator value, NOT guaranteed minimum; '
                                       '18um is an average-based sensitivity, NOT minimum plating; 17.5um ideal half-ounce and '
                                       '15.2um published example are scenarios, NOT fabrication guarantees',
                                       branch_parts_at35um=branch_parts, branches=branch_results,
                                       per10mm_inner_segments=sheet, via_arrays=barrels,
                                       relative_fixed_rise_current={str(t): (t/35)**.725 for t in (35, 30.5, 17.5, 15.2)},
                                       relative_fixed_current_rise={str(t): (35/t)**(.725/.44) for t in (35, 30.5, 17.5, 15.2)},
                                       length_tolerance_note='At1.76mm finished board (1.6mm nominal+10%), barrel terms multiply1.10 only; nominal remains1.6mm',
                                       selected_output_width_sensitivity_low_V=4.81714 - 2*hot*(
                                           (branch_parts['F5 RAW pickup to J8, Q10 excluded'][0]
                                            + branch_parts['F5 RAW pickup to J8, Q10 excluded'][1]*35/30.5)*1.25 + via(.4,18)/2)))
    for path, expected in protected.items():
        assert digest(ROOT / path) == expected, path
    save('preservation-after.json', protected)
    object_screen_path = OUT / 'actual-object-screen-final.json'
    object_screen = json.loads(object_screen_path.read_text())
    assert object_screen['source_pcb_sha256'] == PCB_HASH
    assert object_screen['actual_trace_screen']['min_track_width_mm'] == .1
    assert not object_screen['actual_trace_screen']['trace_to_other_fixed_copper_below_010']
    inputs = [manifest_path, E / 'phase4-21-final-production-native/routing-context.json',
              E / 'phase4-21-final-production-native/snapshot.json',
              E / 'phase4-19-final-audit/manufacturing-metadata.json',
              E / 'phase4-19-final-audit/population.json', E / 'phase4-17-review/engineering.json',
              V4 / 'V4_BOM_REVIEW.md', V4 / 'tools/v4kicad/manufacturing_screen.py',
              V4 / 'tools/tests/test_manufacturing_screen.py', Path(__file__), object_screen_path]
    save('analysis-source-manifest.json', {str(p.relative_to(ROOT)): digest(p) for p in inputs})
    save('verification.json', dict(pcb_hash_matches_owner=True, protected_files_unchanged=len(protected),
                                  references_complete=154, populations={v: {k: len(x) for k, x in s.items()} for v, s in summaries.items()},
                                  f5_exact19=True, bulk_dnp_both=True, accepted_F5_numeric_model_reproduced=True,
                                  native_or_editor_operations=0, fabrication_outputs_generated=0,
                                  cad_bom_writes=0, actual_object_screen_hash_bound=True,
                                  processed_inner_copper_scenario_um=30.5,
                                  via_minimum_plating_confirmed=False))
    print(json.dumps(json.loads((OUT / 'verification.json').read_text())))


if __name__ == '__main__':
    main()
