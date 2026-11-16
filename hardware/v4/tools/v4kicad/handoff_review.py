"""Read-only handoff analysis of canonical native exports; no CAD bindings."""
import argparse
import math
from collections import Counter
from pathlib import Path
from .safety import read_json,write_json,require
from .plan_validation import check_plan
from .f0_plan import poly,F5_REFS


def scan(context, output):
    g=context['snapshot'];pads={(v['ref'],v['pin']):v for v in g['pads'].values()}
    result={}
    for pin,axis,sign in [('14',1,1),('21',0,1),('1',0,-1)]:
        pad=pads[('IC1',pin)];net=pad['net'];start=pad['position']
        print('Local fanout scan IC1.'+pin+' '+net,flush=True)
        rows=[]
        for dx in range(-12,13):
            for dy in range(-12,13):
                if dx==dy==0:continue
                end=[round(start[0]+dx*.1,6),round(start[1]+dy*.1,6)]
                adx,ady=abs(dx)*.1,abs(dy)*.1
                mid=[start[0]+math.copysign(max(0,adx-ady),dx),
                     start[1]+math.copysign(max(0,ady-adx),dy)]
                mid=[round(v,6) for v in mid];end=[round(v,6) for v in end]
                p=dict(failure=None,tracks=[],vias=[[net,*end,.5,.3]])
                poly(p,net,'F.Cu',.13,[start,mid,end])
                r=check_plan(g,p,context)
                blockers=sorted(set(v['against'] for v in r['errors']))
                rows.append(dict(via=end,plan=p,valid=r['valid'],blockers=blockers,errors=r['errors'],
                    only_track_changes=bool(blockers) and all(b in g['tracks'] for b in blockers)))
        legal=[r for r in rows if r['valid']]
        least=sorted([r for r in rows if r['only_track_changes']],
            key=lambda r:(len(r['blockers']),math.dist(r['via'],start)))[:12]
        nonpad=sorted([r for r in rows if r['blockers'] and all(b in g['tracks'] or b in g['vias'] for b in r['blockers'])],
            key=lambda r:(len(r['blockers']),math.dist(r['via'],start)))[:12]
        objects={u:(g['tracks']|g['vias'])[u] for r in [*least,*nonpad] for u in r['blockers']}
        result[net]=dict(pin=pin,pad=start,trace_width=.13,via_diameter=.5,drill=.3,
            candidates=len(rows),legal_local_fanouts=legal,least_track_only_obstructions=least,
            least_track_or_via_obstructions=nonpad,
            obstruction_objects=objects,
            blocker_frequency=dict(Counter(u for r in rows for u in r['blockers'])),
            caveat='Bounded two-leg screen, not proof of native interactive impossibility; no CAD edits')
    write_json(output,result)
    print({n:dict(candidates=r['candidates'],legal=len(r['legal_local_fanouts']),
        minimum_track_blockers=min([len(v['blockers']) for v in r['least_track_only_obstructions']],default=None))
        for n,r in result.items()})


def render(snapshot, output, layer, bounds, pin):
    """Coordinate-labelled close-up from exported physical copper geometry."""
    from PIL import Image,ImageDraw,ImageFont
    g=read_json(snapshot);x0,y0,x1,y1=bounds;scale=125;margin=65
    im=Image.new('RGB',(round((x1-x0)*scale)+2*margin,round((y1-y0)*scale)+2*margin),'white')
    draw=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    def point(p):return (margin+(p[0]-x0)*scale,margin+(p[1]-y0)*scale)
    colors={'VBUS':'#a67300','VIN1':'#555555','BATTERY':'#9d3030','PGND':'#c5dcc5',
        'REGN':'#c58b16','PROG':'#b96db1','CE_N':'#9b00c2','I2C_SDA':'#087d8c',
        'SW1':'#e66b00','SW2':'#ff2424'}
    for x in range(math.ceil(x0*2),math.floor(x1*2)+1):
        a=point([x/2,y0]);b=point([x/2,y1]);draw.line([a,b],fill='#eeeeee')
        draw.text((a[0]-12,margin-22),str(x/2),font=font,fill='black')
    for y in range(math.ceil(y0*2),math.floor(y1*2)+1):
        a=point([x0,y/2]);b=point([x1,y/2]);draw.line([a,b],fill='#eeeeee')
        draw.text((4,a[1]-8),str(y/2),font=font,fill='black')
    for t in g['tracks'].values():
        if t['layer']!=layer:continue
        draw.line([point(t['start']),point(t['end'])],fill=colors.get(t['net'],'#aaaaaa'),width=max(1,round(t['width']*scale)))
    for p in g['pads'].values():
        for polygon in p['polygons'].get(layer,[]):draw.polygon([point(v) for v in polygon],fill=colors.get(p['net'],'#cccccc'))
        x,y=p['position']
        if x0<=x<=x1 and y0<=y<=y1:
            label=p['pin'] if p['ref']=='IC1' else p['ref']+'.'+p['pin']
            if p['ref']=='IC1' and p['pin']==pin:col='blue'
            else:col='black'
            if p['polygons'].get(layer):draw.text((point([x,y])[0]+4,point([x,y])[1]+3),label,font=font,fill=col)
    for v in g['vias'].values():
        x,y=point(v['position']);r=v['copper_widths'][layer]*scale/2
        draw.ellipse([x-r,y-r,x+r,y+r],fill=colors.get(v['net'],'#aaaaaa'))
        r=v['drill']*scale/2;draw.ellipse([x-r,y-r,x+r,y+r],fill='white')
    p=next(v for v in g['pads'].values() if v['ref']=='IC1' and v['pin']==pin)
    x,y=point(p['position']);draw.ellipse([x-15,y-15,x+15,y+15],outline='blue',width=2)
    crop=im.crop((margin,margin,im.width-margin,im.height-margin))
    draw.rectangle((0,0,im.width,im.height),fill='white');im.paste(crop,(margin,margin))
    for x in range(math.ceil(x0*2),math.floor(x1*2)+1):
        draw.text((point([x/2,y0])[0]-12,margin-20),str(x/2),font=font,fill='black')
    for y in range(math.ceil(y0*2),math.floor(y1*2)+1):
        draw.text((4,point([x0,y/2])[1]-8),str(y/2),font=font,fill='black')
    draw.text((margin,5),'IC1.'+pin+' '+p['net']+' | '+layer,font=font,fill='black')
    draw.text((margin,25),'Coordinates mm; copper clearance 0.10 mm',font=font,fill='black')
    draw.text((margin,im.height-35),'Copper/pads/drills; plane fill omitted.',font=font,fill='black')
    im.save(output)


def remaining(drc, output):
    rows=[]
    for v in drc['unconnected_items']:
        refs={r for r in F5_REFS if any('of '+r+' ' in item['description'] for item in v['items'])}
        rows.append(dict(subsystem='F5' if refs else 'F0',items=v['items']))
    write_json(output,rows)
    return Counter(r['subsystem'] for r in rows)


def main():
    p=argparse.ArgumentParser();p.add_argument('--context',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();require(not a.output.exists(),'Fresh analysis output required')
    scan(read_json(a.context),a.output)


if __name__=='__main__':main()
