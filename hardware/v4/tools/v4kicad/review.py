"""Render exported geometry only. No CAD/native imports or filesystem work on import."""
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
