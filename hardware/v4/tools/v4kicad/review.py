"""Render exported geometry only. No CAD/native imports or filesystem work on import."""
def render_u3(snapshot_path,layout_path,metrics_path,output,layer,loops=False):
    from PIL import Image,ImageDraw,ImageFont
    from .safety import read_json
    g=read_json(snapshot_path);layout=read_json(layout_path);m=read_json(metrics_path)
    x0,y0,x1,y1=layout['plane_samples']['bounds'];scale=70;top=78
    im=Image.new('RGB',(round((x1-x0)*scale),round((y1-y0)*scale)+top),'#fafafa')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',11);large=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    def pt(p):return ((p[0]-x0)*scale,(p[1]-y0)*scale+top)
    palette={'SYS':'#cf7700','MAIN_3V3':'#1565c0','/SW_NORMAL':'#e53935','/BST_NORMAL':'#9727b0',
             'PGND':'#348348','/MAIN_FB':'#202020','/NORMAL_SS':'#8f8500','/NORMAL_EN':'#168e9e'}
    if layer=='In1.Cu':
        rows=layout['plane_samples']['rows'];grid=Image.new('RGB',(len(rows[0]),len(rows)),'white')
        grid.putdata([(182,213,183) if c=='1' else (255,255,255) for row in rows for c in row])
        im.paste(grid.resize((im.width,im.height-top),Image.Resampling.NEAREST),(0,top))
    d=ImageDraw.Draw(im)
    for ref,polys in layout['courtyards'].items():
        for poly in polys:d.line([pt(v) for v in poly['outline']+[poly['outline'][0]]],fill='#c7c7c7',width=1)
    for t in g['tracks'].values():
        if t['layer']==layer:d.line([pt(t['start']),pt(t['end'])],fill=palette.get(t['net'],'#aaaaaa'),width=max(1,round(t['width']*scale)))
    for p in g['pads'].values():
        for poly in p['polygons'].get(layer,[]):d.polygon([pt(v) for v in poly],fill=palette.get(p['net'],'#bbb'))
        if layer=='F.Cu' and p['polygons'].get(layer) and x0<p['position'][0]<x1 and y0<p['position'][1]<y1:
            x,y=pt(p['position']);d.text((x+3,y+3),p['ref']+'.'+p['pin'],font=font,fill='#101010',stroke_width=1,stroke_fill='white')
    for v in g['vias'].values():
        x,y=pt(v['position']);r=v['copper_widths'][layer]*scale/2
        d.ellipse([x-r,y-r,x+r,y+r],fill=palette.get(v['net'],'#aaa'))
        r=v['drill']*scale/2;d.ellipse([x-r,y-r,x+r,y+r],fill='white')
    if layer=='In1.Cu':
        for name,r in m['plane_return_paths'].items():
            d.line([pt(q) for q in r['path']],fill={'C33':'#0055a0','C45':'#4060b0','FB_reference':'#191919'}[name],width=2)
        for fp in g['footprints'].values():
            if x0<fp['position'][0]<x1 and y0<fp['position'][1]<y1:
                d.text(pt(fp['position']),fp['ref'],font=font,fill='#333')
    if loops:
        for name,color in [('input','#804000'),('bootstrap','#800080'),('output_C33','#001580')]:
            path=m['loops'][name];d.line([pt(q) for q in path+[path[0]]],fill=color,width=2)
    d.rectangle([0,0,im.width,top],fill='white')
    d.text((8,5),'U3 scratch proposal | '+layer+(' | loop centerline overlays' if loops else ''),font=large,fill='black')
    d.text((8,32),'SYS orange | MAIN blue | SW red | BST purple | PGND green | FB black',font=font,fill='black')
    d.text((8,50),'Native saved/reloaded copper & courtyards; In1 uses native 0.1 mm fill sampling + drill cutouts. No field simulation.',font=font,fill='black')
    im.save(output)


def render(snapshot_path, output, layer, bounds):
    from PIL import Image, ImageDraw, ImageFont
    from .safety import read_json
    g = read_json(snapshot_path)
    x0,y0,x1,y1 = bounds; scale=60; top=40
    im=Image.new('RGB',(round((x1-x0)*scale),round((y1-y0)*scale)+top),'white')
    d=ImageDraw.Draw(im); font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    colors={'REGN':'#c08000','CE_N':'#b000c0','CE_BIAS':'#0040df','PGND':'#b5cfb5',
            'GND':'#71a071','SW2':'#f00000','SW1':'#f06000','BTST2':'#00a0b0','BATTERY':'#505050',
            'TS':'#208080','ILIM_HIZ':'#802020','PROG':'#d080c0','BATP':'#80a000'}
    def pt(p):return ((p[0]-x0)*scale,(p[1]-y0)*scale+top)
    for t in g['tracks'].values():
        if t['layer']!=layer:continue
        d.line([pt(t['start']),pt(t['end'])],fill=colors.get(t['net'],'#aaaaaa'),width=max(1,round(t['width']*scale)))
    for p in g['pads'].values():
        for poly in p['polygons'].get(layer,[]):d.polygon([pt(v) for v in poly],fill=colors.get(p['net'],'#dddddd'))
        if p['polygons'].get(layer) and x0<p['position'][0]<x1 and y0<p['position'][1]<y1:
            x,y=pt(p['position']);d.text((x+3,y+3),p['ref']+'.'+p['pin'],font=font,fill='black')
    for v in g['vias'].values():
        x,y=pt(v['position']);r=v['copper_widths'][layer]*scale/2
        d.ellipse([x-r,y-r,x+r,y+r],fill=colors.get(v['net'],'#999999'))
        r=v['drill']*scale/2;d.ellipse([x-r,y-r,x+r,y+r],fill='white')
    d.rectangle([0,0,im.width,top],fill='white');d.text((5,8),layer+' native exported pads/tracks/vias; no ground-fill silhouettes',font=font,fill='black')
    im.save(output)

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--output',required=True)
    p.add_argument('--layer',required=True);p.add_argument('--bounds',type=float,nargs=4,required=True)
    a=p.parse_args();render(a.snapshot,a.output,a.layer,a.bounds)
