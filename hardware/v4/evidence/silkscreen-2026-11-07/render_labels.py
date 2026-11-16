from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
E=Path(__file__).resolve().parent
tag=sys.argv[1] if len(sys.argv)>1 else 'planned'
shapes=json.loads((E/(tag+'-visual.json')).read_text())
S=28;origin=(28,28)
im=Image.new('RGB',(100*S,74*S),'#f8faf8');d=ImageDraw.Draw(im)
def point(v):return (round((v[0]-origin[0])*S),round((v[1]-origin[1])*S))
d.rectangle([point([30,30]),point([126,100])],fill='#edf2ed',outline='#506050',width=2)
for kind,col in [('fab','#b9c7bc'),('pad','#b99a63'),('silk','#788c7c'),('reference','#111b17')]:
    for shape in shapes:
        if shape['kind']!=kind:continue
        for poly in shape['polys']:
            if len(poly['outline'])>2:d.polygon([point(v) for v in poly['outline']],fill=col)
            for hole in poly['holes']:
                if len(hole)>2:d.polygon([point(v) for v in hole],fill='#edf2ed')
im.save(E/(tag+'.png'))
for region,(x1,y1,x2,y2) in {'power':(51,43,98,80),'left':(29,29,64,100),'right':(88,29,127,100)}.items():
    im.crop((*point([x1,y1]),*point([x2,y2]))).save(E/(tag+'-'+region+'.png'))
print(str(E/(tag+'.png')))
