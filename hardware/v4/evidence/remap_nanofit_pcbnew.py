"""Native offline pcbnew remap, verified before replacing the saved board."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
import pcbnew
from verify_nanofit import parse
E=Path(__file__).resolve().parent
B=E.parent/'ups_v4/ups12v_v4.kicad_pcb'
C=E/'nanofit-native-remapped-candidate.kicad_pcb'
original=B.read_bytes()
board=pcbnew.LoadBoard(str(B))
desired={('J2','1'):'PGND',('J2','2'):'unconnected-(J2-Pin_2-Pad2)',('J2','3'):'SYS',('J8','1'):'PGND',('J8','2'):'unconnected-(J8-Pin_2-Pad2)',('J8','3'):'/F5_5V_OUT'}
changes=[]
for f in board.GetFootprints():
    for p in f.Pads():
        key=(f.GetReference(),p.GetNumber())
        if key not in desired:continue
        name=desired[key]
        net=board.FindNet(name)
        if not net:
            net=pcbnew.NETINFO_ITEM(board,name)
            board.Add(net)
        if p.GetNetname()!=name:changes.append({'ref':key[0],'pad':key[1],'before':p.GetNetname(),'after':name})
        p.SetNet(net)
assert pcbnew.SaveBoard(str(C),board)
reloaded=pcbnew.LoadBoard(str(C))
for f in reloaded.GetFootprints():
    for p in f.Pads():
        key=(f.GetReference(),p.GetNumber())
        if key in desired:assert p.GetNetname()==desired[key]
def without_nets(v):
    if isinstance(v,list):return [without_nets(x) for x in v if not(isinstance(x,list) and x and x[0]=='net')]
    return v
assert without_nets(parse(original.decode('utf-8')))==without_nets(parse(C.read_text())), 'Non-net serialized attribute changed'
report={'changes':changes,'native_save_reload':True,'every_non_net_attribute_preserved':True,'source_sha256':hashlib.sha256(original).hexdigest(),'candidate_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'production_applied':False}
if '--apply' in sys.argv:
    assert B.read_bytes()==original,'Production changed while preparing candidate'
    shutil.copyfile(B,E/'nanofit-before-native-remapping.kicad_pcb')
    assert pcbnew.SaveBoard(str(B),reloaded)
    assert B.read_bytes()==C.read_bytes()
    report['production_applied']=True
(E/'nanofit-native-remapping.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
