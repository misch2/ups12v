"""Offline final preservation and bounded scratch-result summary."""
from pathlib import Path
import json,hashlib,collections,math
E=Path(__file__).resolve().parent;B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
base=json.loads((E/'c9-apply-phase4-7-batch1-final-ipc.json').read_text())
entry=json.loads((E/'c9-apply-phase4-7-c23-270-entry-ipc.json').read_text())
stop=json.loads((E/'c9-apply-phase4-7-c23-270-stop-ipc.json').read_text())
hashes={n:hashlib.sha256((B.parent/n).read_bytes()).hexdigest() for n in base['hashes']}
matches={n:base[n]==entry[n]==stop[n] for n in ['footprints','pads','tracks','vias','zones','shapes','texts']}
def drc(name):
 a=json.loads((E/name).read_text());errors=[v for v in a['violations'] if v['severity']=='error']
 return dict(unconnected=len(a['unconnected_items']),other_errors=len(errors),warnings=sum(v['severity']=='warning' for v in a['violations']),parity=a['schematic_parity'],error_rules=dict(collections.Counter(v['rule'] for v in errors)),non_PROG_errors=[v for v in errors if not any('PROG' in i['description'] for i in v['items'])])
plan=json.loads((E/'phase4-7-original-partial-clean-plan.json').read_text())
out=dict(entry_exact_match=base==entry,stop_exact_match=base==stop,object_matches=matches,production_hashes_unchanged=base['hashes']==entry['hashes']==stop['hashes']==hashes,hashes=hashes,
 production_counts={n:len(stop[n]) for n in ['footprints','pads','tracks','vias','zones']},
 c23_270_drc=drc('phase4-7-c23-270-drc.json'),original_partial_drc=drc('phase4-7-original-partial-clean-drc.json'),original_PROG_attempt_drc=drc('phase4-7-original-prog-obstruction-drc.json'),
 original_partial_route_lengths_mm={n:sum(math.hypot(t[5]-t[3],t[6]-t[4]) for t in plan['tracks'] if t[0]==n) for n in set(t[0] for t in plan['tracks'])},
 original_partial_vias=plan['vias'],original_PROG_grid_obstruction=json.loads((E/'phase4-7-original-PROG-obstruction.json').read_text()),
 production_mutations=0,near_IC1_C23_relocation_abandoned=True,Phase4_7_complete=False,
 stop_reason='No compliant PROG escape established with existing power/switching copper and configured clearances; concrete scratch via attempt fails native DRC in both placements. No claim of exhaustive continuous-routing impossibility.',
 no_assertion_or_IPC_instability_observed=True)
out['preservation_passed']=out['entry_exact_match'] and out['stop_exact_match'] and all(matches.values()) and out['production_hashes_unchanged']
assert out['preservation_passed']
(E/'phase4-7-c23-270-final-preservation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['preservation_passed','production_counts','production_mutations','Phase4_7_complete','original_PROG_grid_obstruction']}))
