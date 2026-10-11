"""Read-only native saved-board checks and structural preservation comparison."""
from pathlib import Path
import sys,json,collections
sys.dont_write_bytecode=True
import pcbnew
from verify_nanofit import parse,many,one,ref
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
b=pcbnew.LoadBoard(str(B))
old=parse((E/'nanofit-native-entry.kicad_pcb').read_text())
new=parse(B.read_text())
of={ref(f):f for f in many(old,'footprint')}
nf={ref(f):f for f in many(new,'footprint')}
unrelated=[r for r in of if r not in ('J1','J2','J3','J8') and of[r]!=nf[r]]
assert not unrelated,unrelated
def keyed(n,k):return {one(x,'uuid')[1]:x for x in many(n,k)}
ot,nt=keyed(old,'segment'),keyed(new,'segment')
preserved=set(ot)&set(nt)
assert all(ot[k]==nt[k] for k in preserved)
assert many(old,'via')==many(new,'via')
for kind in ('gr_line','gr_rect','gr_poly','gr_arc','gr_text'):
    assert many(old,kind)==many(new,kind),kind
def zone_definition(z):return [v for v in z if not(isinstance(v,list) and v[0] in ('filled_polygon','fill_segments'))]
assert [zone_definition(z) for z in many(old,'zone')]==[zone_definition(z) for z in many(new,'zone')]
connectors=[]
for f in b.GetFootprints():
    r=f.GetReference()
    if r not in ('J1','J2','J3','J8'):continue
    pads=[]
    for p in f.Pads():
        pos=p.GetFPRelativePosition()
        d=p.GetDrillSize()
        pads.append({'number':p.GetNumber(),'net':p.GetNetname(),'local_mm':[pcbnew.ToMM(pos.x),pcbnew.ToMM(pos.y)],'drill_mm':[pcbnew.ToMM(d.x),pcbnew.ToMM(d.y)],'drill_shape':int(p.GetDrillShape()),'pad_angle':p.GetOrientationDegrees()})
        if not p.GetNumber():
            assert p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH
            assert pos.x==7180000
            if pos.y==0:
                assert (d.x,d.y)==(1600000,1750000)
                assert p.GetDrillShape()==pcbnew.PAD_DRILL_SHAPE_OBLONG
            else:
                assert pos.y==(2500000 if r in ('J1','J3') else 5000000)
                assert (d.x,d.y)==(1600000,1600000)
                assert p.GetDrillShape()==pcbnew.PAD_DRILL_SHAPE_CIRCLE
        else:assert (d.x,d.y)==(1200000,1200000)
    assert f.GetOrientationDegrees()==90
    for flag in ('attr','exclude_from_pos_files','exclude_from_bom','dnp'):
        assert many(of[r],flag)==many(nf[r],flag),(r,flag)
    for prop in ('PopulationGroup','DNP','Variant'):
        assert [p[2] for p in many(of[r],'property') if p[1]==prop]==[p[2] for p in many(nf[r],'property') if p[1]==prop]
    connectors.append({'reference':r,'library_id':str(f.GetFPID().GetLibItemName()),'rotation':f.GetOrientationDegrees(),'pads':pads})
expected={'J2':{'1':'PGND','2':'unconnected-(J2-Pin_2-Pad2)','3':'SYS'},'J8':{'1':'PGND','2':'unconnected-(J8-Pin_2-Pad2)','3':'/F5_5V_OUT'}}
for c in connectors:
    if c['reference'] in expected:assert {p['number']:p['net'] for p in c['pads'] if p['number']}==expected[c['reference']]
report={'status':'PASS: native saved-board geometry, remapping and bounded preservation','unchanged_unrelated_footprints':len(of)-4,'unrelated_footprint_changes':unrelated,'unchanged_tracks':len(preserved),'removed_tracks':sorted(set(ot)-set(nt)),'added_tracks':sorted(set(nt)-set(ot)),'all_vias_unchanged':len(many(old,'via')),'board_graphics_outline_and_zone_definitions_including_RF_keepout_unchanged':True,'population_and_instance_flags_preserved':True,'connectors':connectors}
(E/'nanofit-final-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('connectors','removed_tracks','added_tracks')}))
