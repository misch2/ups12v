"""Independent saved/export proof for exact Phase4.18 F5 adoption; import-safe."""
from pathlib import Path
import argparse
from .safety import require,read_json,write_json,digest,ToolError
from .f5_migration import check_context,implementations,reconcile,COUNTS


def prove(review,transaction,output):
    from .review_compare import checks_delta,connectivity_delta,merge_counts
    from .f5_metadata import serialized_proof
    review,transaction,output=map(Path,[review,transaction,output]);c,p=check_context(transaction,installed=True)
    goal,entry=Path(p['goal']),Path(p['entry'])
    target,current=[read_json(d/'snapshot.json') for d in [goal,review]]
    require(target==current,'Saved native target geometry differs')
    require({s:len(current[s]) for s in COUNTS}==COUNTS,'Final object counts differ')
    require(read_json(goal/'routed-diagnostics.json')==read_json(review/'routed-diagnostics.json'),
            'Native arcs/vias/drills/padstacks differ')
    inspection=read_json(review/'native-review-inspection.json');audit=read_json(goal/'native-audit.json')
    require(inspection['audit']==audit,'Native artwork/zone/rule-area definitions differ')
    require(read_json(goal/'polygon-artwork.json')==read_json(review/'polygon-artwork.json'),
            'Exact polygon artwork vertices/holes differ')
    require(inspection['pad_partitions']==read_json(goal/'pad-partition.json') and
            len(inspection['pad_partitions'])==116,'All473pad island sets must match')
    baseline_i=dict(pad_partitions=read_json(entry/'pad-partition.json'))
    connectivity=connectivity_delta(baseline_i,inspection)
    require(connectivity['all_previous_pad_connections_preserved'],'Old pad connections split')
    merges=merge_counts(baseline_i,inspection,current)
    accepted=read_json('hardware/v4/evidence/phase4-17-review/engineering.json')
    require(merges==accepted['merged_pad_islands_by_net'],'Unapproved electrical merge')
    ca,cb=[read_json(d/'routing-context.json') for d in [goal,review]]
    for s in ['profile','pads','copper_graphics','zones','board_outline','reservations']:
        require(ca[s]==cb[s],'Actual pad/rule/RF context differs: '+s)
    require(read_json(goal/'layout.json')['fills']==read_json(review/'post-refill-layout.json')['fills'],
            'Actual saved filled polygons/holes differ')
    summary=read_json(review/'summary.json')
    require(summary['drc']['unconnected']==summary['drc']['errors']==summary['drc']['parity']==summary['erc']['errors']==0,
            'Complete zero-error ERC/DRC/parity/connectivity required')
    source=Path(p['accepted_F5_board']).parent
    warnings=checks_delta(source,review)
    require(warnings['drc']['warning_identity_multiset_equal'] and warnings['drc']['ignored_checks_equal']
            and warnings['erc']['warning_identity_multiset_equal'],'Isolated warning identities/rules differ')
    production_checks=None
    if c['production']:
        from .review_compare import warning_identity_rows
        production_checks=read_json(transaction/'production-checks.json')
        require(production_checks['drc']['unconnected']==production_checks['drc']['errors']==
                production_checks['drc']['parity']==production_checks['erc']['errors']==0,
                'Production-context checks incomplete')
        baseline=Path('hardware/v4/evidence/phase4-16-production-adoption')
        for kind in ['drc','erc']:
            require(warning_identity_rows(read_json(transaction/('production-'+kind+'.json')),kind)==
                    warning_identity_rows(read_json(baseline/('production-'+kind+'.json')),kind),
                    'Production warning identities differ: '+kind)
    reconcile(read_json(entry/'snapshot.json'),current,p)
    structural=serialized_proof(entry/'ups12v_v4.kicad_pcb',review/'ups12v_v4.kicad_pcb',
        p['accepted_routing_plan'],read_json(source/'expected-additions.json'),review/'serialized-diagnostic.json')
    require(read_json(transaction/'final-live-readback.json')['saved_live_exact'],'Final live reconciliation missing')
    installed=read_json(transaction/'installed-manifest.json');target_board=Path(c['target'])
    for name,wanted in installed['hashes'].items():require(digest(target_board.parent/name)==wanted,'Persisted source drift')
    sources={str((target_board.parent/name).resolve()):h for name,h in installed['hashes'].items()}
    proof=dict(verdict='PASS_FINAL_PRODUCTION' if c['production'] else 'PASS_COMPLETE_CANDIDATE',
        plan_hash=c['plan_hash'],implementations=implementations(),
        candidate_sources=sources|{str(Path(__file__).resolve()):digest(__file__),
            str(Path(__file__).with_name('f5_metadata.py').resolve()):digest(Path(__file__).with_name('f5_metadata.py'))},
        verifier_sha256=digest(__file__),
        checks=summary,production_context_checks=production_checks,warnings=warnings,connectivity=connectivity,merged_islands=merges,
        exact_native_goal=True,all473_pad_islands_exact=True,all_original_F0_and_arcs_preserved=True,
        F5_power_switching_bootstrap_feedback_polarity_and_current_paths_exact=True,
        PGND_filled_polygons_holes_and_RF_constraints_exact=True,serialized_preservation=structural,
        complete_live_preservation=True,remaining_unconnected=0,transaction=str(transaction.resolve()),
        independent_review=str(review.resolve()))
    write_json(output,proof)
    if c['production']:write_json(transaction/'accepted-installed-baseline.json',installed)
    print(proof['verdict']+':473pads/116islands/0opens/0physical/0parity/0ERC')
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['review','transaction','output']:p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args()
    try:prove(a.review,a.transaction,a.output)
    except (ToolError,OSError,ValueError,KeyError,TypeError) as e:
        print('STOP: '+str(e));raise SystemExit(2)
