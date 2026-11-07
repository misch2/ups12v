"""Explicit, bounded Phase4.17 geometry proposals; exported data only."""
from .f5_scratch import BASELINE, transformed


def placement_plan():
    return dict(mode='F5-scratch-only', baseline_sha256=BASELINE, failure=None,
        placements={
            'U7': [102., 59., 0.], 'L3': [105., 64.2, 0.],
            'C69': [99.8, 59.5, -90.],
            'C60': [96.5, 59.5, -90.], 'C61': [96.5, 64.3, -90.],
            'C62': [104.3, 59.5, -90.], 'C63': [108.5, 58.5, 0.],
            'R60': [105.5, 55., 0.], 'R61': [105.5, 57., 180.],
            'R62': [98., 55., 90.], 'R63': [98., 51.9, 90.],
            'C64': [109.5, 63.75, -90.], 'C65': [113., 63.75, -90.],
            'C66': [110., 60., 0.],
            'Q10': [113., 56.5, 0.], 'U8': [117.1, 58.5, 180.],
            'C67': [117., 62., 90.], 'C68': [113., 52.5, 0.],
        }, tracks=[], vias=[])


def write_placement(context, output):
    from .safety import write_json
    p = placement_plan(); write_json(output, p)
    write_json(str(output)+'.geometry.json', transformed(context['snapshot'], p['placements']))


def local_plan():
    p = placement_plan()
    def line(net, width, points, layer='F.Cu'):
        p['tracks'].extend([[net, layer, width, *a, *b] for a, b in zip(points, points[1:])])
    def via(net, point, d=.5, h=.3): p['vias'].append([net, *point, d, h])
    line('SYS', .3, [[101.26,59.25],[100.4,59.25]])
    line('SYS', .5, [[100.4,59.25],[99.875,58.725]])
    line('SYS', 1., [[96.5,58.025],[99.1,58.025],[99.8,58.725]])
    line('SYS', 1., [[96.5,62.825],[94.3,62.825],[94.3,59.0],[95.275,58.025],[96.5,58.025]])
    line('PGND', .3, [[101.26,59.75],[100.85,59.75]])
    line('PGND', .45, [[100.85,59.75],[100.325,60.275],[99.8,60.275]])
    via('PGND',[100.5,60.1])
    line('PGND', 1., [[96.5,60.975],[99.8,60.975],[99.8,60.275]])
    for x in [97.7,98.7,99.8]: via('PGND',[x,60.975],.7,.4)
    line('PGND', 1., [[96.5,65.775],[98.4,65.775]])
    via('PGND',[98.4,65.775],.7,.4)
    line('/F5_SW', .3, [[102.74,59.75],[103.0,59.75],[103.2,60.0],[103.2,60.2]])
    line('/F5_SW', .6, [[103.2,60.2],[103.2,62.2]])
    line('/F5_SW', .5, [[104.3,60.275],[103.2,60.275]])
    line('/F5_BST', .28, [[102.74,59.25],[104.3,59.25],[104.3,58.725]])
    line('/F5_SS', .28, [[102.74,58.75],[103.35,58.7]])
    via('/F5_SS',[103.35,58.7])
    line('/F5_SS', .3, [[103.35,58.7],[106.6,58.7],[107.3,59.4]], 'B.Cu')
    via('/F5_SS',[107.3,59.4])
    line('/F5_SS', .3, [[107.3,59.4],[107.3,58.925],[107.725,58.5]])
    line('/F5_FB', .28, [[102.74,58.25],[103.19,57.8],[105.525,57.8],[106.325,57.0]])
    line('/F5_FB', .3, [[106.325,57.0],[106.325,55.]])
    line('PGND', .3, [[104.675,57.],[103.85,56.9]])
    via('PGND',[103.85,56.9])
    line('/F5_RAW', .3, [[104.675,55.],[104.,54.325]])
    via('/F5_RAW',[104.,54.325])
    line('/F5_RAW', .3, [[104.,54.325],[107.,54.325],[108.25,55.575],[108.25,59.95],[109.5,61.2]], 'B.Cu')
    via('/F5_RAW',[109.5,61.2])
    line('/F5_RAW', .3, [[109.5,61.2],[109.5,62.275]])
    line('/F5_EN', .3, [[98.,54.175],[98.,52.725]])
    line('/F5_EN', .3, [[101.26,58.75],[100.65,58.75],[100.65,56.2],[98.625,54.175],[98.,54.175]])
    line('SYS', .3, [[98.,55.825],[97.3,56.525],[96.5,58.025]])
    line('PGND', .3, [[98.,51.075],[98.,50.2]])
    via('PGND',[98.,50.2])
    line('PGND', .3, [[109.275,58.5],[109.275,57.7]])
    via('PGND',[109.275,57.7])
    line('/F5_RAW', 1.2, [[106.655,64.2],[107.575,64.2],[109.5,62.275],[113.,62.275]])
    line('/F5_RAW', .5, [[109.225,60.],[109.225,61.],[109.5,61.275],[109.5,62.275]])
    line('PGND', .35, [[110.775,60.],[110.775,59.2]])
    via('PGND',[110.775,59.2])
    for x in [109.5,113.]:
        line('PGND', .8, [[x,65.225],[x,66.4]])
        via('PGND',[x,66.4],.8,.4)
        line('PGND', .5, [[x,65.225],[x+1.,65.225]])
        via('PGND',[x+1.,65.225],.7,.4)
    line('/F5_RAW', .35, [[112.02,57.96],[112.68,57.96],[113.32,57.96]])
    line('/F5_RAW', .4, [[112.02,57.96],[112.02,58.8]])
    line('/F5_RAW', 1.2, [[112.02,58.8],[112.02,61.],[113.,61.98],[113.,62.275]])
    line('/F5_RAW', .35, [[113.,62.275],[114.55,62.275],[115.9625,60.8625],[115.9625,59.45]])
    line('/F5_RAW', .3, [[115.9625,60.8625],[116.6,61.225],[117.,61.225]])
    # Separate short ANODE pickup from source pin3, before the load-current trunk.
    line('/F5_RAW', .3, [[113.32,57.96],[113.32,58.8],[113.97,59.45],[115.9625,59.45]])
    # EN is tied to the anode net through an isolated B-side branch.
    line('/F5_RAW', .3, [[118.2375,57.55],[118.2375,56.8],[117.5,56.8]])
    via('/F5_RAW',[117.5,56.8])
    line('/F5_RAW', .3, [[117.5,56.8],[116.6,57.7],[116.6,60.825],[117.,61.225]], 'B.Cu')
    via('/F5_RAW',[117.,61.225])
    line('/F5_VCAP', .3, [[118.2375,59.45],[118.8,60.0125],[118.8,62.775],[117.,62.775]])
    line('/F5_GATE', .35, [[113.98,57.96],[114.6,57.96],[115.14,58.5],[115.9625,58.5]])
    line('/F5_5V_OUT', .3, [[115.9625,57.55],[115.4,57.55],[115.4,55.8],[114.2,54.6],[113.,54.6]])
    line('/F5_5V_OUT', 1.2, [[113.,56.19],[113.,55.],[112.225,54.225],[112.225,52.5]])
    for x in [112.02,112.68,113.32,113.98]:
        line('/F5_5V_OUT', .4, [[x,55.04],[x,56.19],[113.,56.19]]) if x != 113. else None
    line('PGND', .3, [[113.775,52.5],[114.7,52.5]])
    via('PGND',[114.7,52.5])
    line('PGND', .3, [[118.2375,58.5],[117.5,58.5]])
    via('PGND',[117.5,58.5])
    return p


def complete_plan():
    p = local_plan()
    def line(net, layer, width, points):
        p['tracks'].extend([[net, layer, width, *a, *b] for a,b in zip(points,points[1:])])
    # One B bridge crosses the fixed In2 BATTERY trunk without touching F0 copper.
    for x in [76.2,85.8]:
        for y in [47.5,48.5]: p['vias'].append(['SYS',x,y,.8,.4])
        line('SYS','B.Cu',1.5,[[x,47.5],[x,48.5]])
        line('SYS','In2.Cu',1.5,[[x,47.5],[x,48.5]])
    line('SYS','B.Cu',1.5,[[76.2,47.5],[85.8,47.5]])
    line('SYS', 'In2.Cu', 1.5, [[85.8,47.5],[88.5,50.2],
        [88.5,57.025],[94.3,62.825]])
    for y in [61.825,62.825]: p['vias'].append(['SYS',94.3,y,.8,.4])
    line('SYS','F.Cu',1.,[[94.3,61.825],[94.3,62.825]])
    line('SYS','In2.Cu',1.5,[[94.3,61.825],[94.3,62.825]])
    line('/F5_5V_OUT','F.Cu',1.2,[[112.225,52.5],[112.225,50.5]])
    for y in [50.5,49.5]: p['vias'].append(['/F5_5V_OUT',112.225,y,.8,.4])
    line('/F5_5V_OUT','F.Cu',1.2,[[112.225,50.5],[112.225,49.5]])
    line('/F5_5V_OUT','In2.Cu',2.,[[112.225,50.5],[112.225,47.775],
        [107.045,42.595],[96.215,42.595],[94.,40.38]])
    line('/F5_5V_OUT','In2.Cu',.6,[[112.225,47.775],[115.,45.]])
    p['vias'].append(['/F5_5V_OUT',115.,45.,.5,.3])
    line('/F5_5V_OUT','F.Cu',.5,[[115.,45.],[115.5,44.5]])
    return p


if __name__ == '__main__':
    import argparse
    from .safety import read_json
    p = argparse.ArgumentParser(); p.add_argument('--context', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--local', action='store_true')
    p.add_argument('--complete', action='store_true')
    a = p.parse_args()
    if a.local or a.complete:
        from .safety import write_json
        write_json(a.output, complete_plan() if a.complete else local_plan())
    else: write_placement(read_json(a.context), a.output)
