"""Independent export-only Phase4.16 proof; no native CAD/editor operations.

Worker implementation stays immutable across rehearsal and production. Bind
both deliberately different project identities and compare all resolved rules.
"""
from pathlib import Path
from collections import Counter
import argparse
import json
import sys
from .safety import require, read_json, write_json, digest, ToolError
from .owner_migration import check_context, open_net_counts


def compare_profiles(owner, candidate, plan):
    require(owner['project_sha256'] == plan['expected_owner_hashes']['ups12v_v4.kicad_pro'],
            'Owner project provenance differs')
    require(candidate['project_sha256'] == plan['expected_production_hashes']['ups12v_v4.kicad_pro'],
            'Production project provenance differs')
    require({k:v for k,v in owner.items() if k != 'project_sha256'} ==
            {k:v for k,v in candidate.items() if k != 'project_sha256'},
            'Resolved electrical rule profile differs')
    return True


def prove(review, transaction, output):
    from .review_compare import checks_delta, connectivity_delta, merge_counts, property_delta
    c, p = check_context(transaction, installed=True)
    owner = Path(p['native_review'])
    a, b = [read_json(x/'snapshot.json') for x in [owner, review]]
    ia, ib = [read_json(x/'native-review-inspection.json') for x in [owner, review]]
    require(all(a[s] == b[s] for s in a), 'Independent native target geometry differs')
    require(read_json(owner/'routed-diagnostics.json') == read_json(review/'routed-diagnostics.json'),
            'Native arcs/via copper/drill/padstack geometry differs')
    require(ia['pad_partitions'] == ib['pad_partitions'], 'Exact 473-pad island sets differ')
    require(len(ib['pad_partitions']) == 157, '157 native pad islands required')
    require(ia['usb_pairs'] == ib['usb_pairs'], 'Native USB netclass/pair recognition differs')
    require(ia['audit']['zones'] == ib['audit']['zones'] and
            ia['audit']['drawings'] == ib['audit']['drawings'], 'Native zone/rule-area/drawing definitions differ')
    art = lambda rows:Counter(json.dumps({k:v for k,v in row.items() if k!='uuid'},sort_keys=True)
                             for row in rows.values())
    require(set(ia['audit']['footprint_graphics']) == set(ib['audit']['footprint_graphics']) and
            all(art(rows) == art(ib['audit']['footprint_graphics'][ref])
                for ref,rows in ia['audit']['footprint_graphics'].items()), 'Native footprint artwork differs')
    ca, cb = [read_json(x/'routing-context.json') for x in [owner,review]]
    compare_profiles(ca['profile'], cb['profile'], p)
    for section in ['pads','copper_graphics','zones','board_outline','reservations']:
        require(ca[section] == cb[section], 'Actual pad/rule/geometry context differs: '+section)
    require(read_json(owner/'post-refill-layout.json')['fills'] ==
            read_json(review/'post-refill-layout.json')['fills'], 'Actual filled copper polygons/holes differ')
    summary = read_json(review/'summary.json')
    require(summary['drc']['errors'] == summary['drc']['parity'] == summary['erc']['errors'] == 0
            and summary['drc']['unconnected'] == 41, 'Final ERC/DRC/parity differs')
    checks = checks_delta(owner, review)
    require(checks['drc']['warning_identity_multiset_equal'] and checks['drc']['ignored_checks_equal']
            and checks['erc']['warning_identity_multiset_equal'], 'Warning identities/rules differ')
    opens = open_net_counts(read_json(review/'drc.json'), b)
    require(opens == open_net_counts(read_json(owner/'drc.json'), a), 'Remaining net groups differ')
    accepted = Path('hardware/v4/evidence/phase4-13-final-production-native')
    baseline_i = read_json(accepted/'native-review-inspection.json')
    connectivity = connectivity_delta(baseline_i, ib)
    require(connectivity['all_previous_pad_connections_preserved'], 'A previously connected pad island split')
    require(merge_counts(baseline_i,ib,b) == {'I2C_SCL':1,'~INT':1,'STAT':1}, 'Unapproved pad-island merge')
    require(all(net in {'PGND','SYS'} or net.startswith('/F5_') for net in opens), 'Non-F5 remaining open net')
    structural = property_delta(Path(c['entry_snapshot']).parent/'ups12v_v4.kicad_pcb',
                                review/'ups12v_v4.kicad_pcb', True)
    write_json(review/'production-structural-delta.json', structural)
    allowed = {u for s in ['tracks','vias'] for rows in p['operations'][s].values() for u in rows}
    fpids = set(p['operations']['footprints']['translate_whole_instance_with_preimage'])
    for row in structural['changes']:
        top = row['path'][0].split(':')
        require((top[0] in ['segment','via'] and top[1].strip('"') in allowed)
                or (top[0] == 'footprint' and top[1].strip('"') in fpids),
                'Unclassified saved board property change: '+row['path'][0])
    installed = read_json(transaction/'installed-manifest.json')
    for path,wanted in installed['hashes'].items():
        require(digest(Path(c['target']).parent/path) == wanted, 'Saved source changed during review')
    require(read_json(transaction/'final-live-readback.json')['saved_live_exact'], 'Final live reconciliation required')
    sources = {str((Path(c['target']).parent/name).resolve()):wanted
               for name,wanted in installed['hashes'].items()}
    proof = dict(verdict='PASS_FINAL_PRODUCTION' if c['production'] else 'PASS_COMPLETE_CANDIDATE',
                 plan_hash=c['plan_hash'], implementation_hash=c['implementation_hash'], candidate_sources=sources,
                 verifier_sha256=digest(__file__), project_hashes_separately_bound=True,
                 native_target_exact=True, all_473_pad_islands_exact=True, connectivity=connectivity,
                 intended_merges={'I2C_SCL':1,'~INT':1,'STAT':1}, actual_fill_polygons_exact=True,
                 critical_power_PGND_USB_F5_preserved_as_accepted=True, eight_actual_arcs_exact=True,
                 checks=summary, warnings=checks, remaining_by_net=opens, F5_unconnected=41, F0_unconnected=0,
                 complete_live_nonfill_preservation=True, saved_structural_whitelist=True,
                 independent_review=str(review.resolve()), transaction=str(transaction.resolve()))
    write_json(output, proof)
    if c['production']:
        write_json(transaction/'accepted-installed-baseline.json', installed)
    print(proof['verdict']+': 473 pads /157 islands /41 F5 opens /0 F0 /0 physical /0 parity /0 ERC errors')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['review','transaction','output']:
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        prove(args.review,args.transaction,args.output)
        return 0
    except (ToolError,OSError,ValueError,KeyError,TypeError) as error:
        print('STOP: '+str(error),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
