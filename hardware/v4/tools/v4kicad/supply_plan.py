"""Export-only Phase4.8B planning; CAD access belongs to isolated native workers."""
import argparse
import copy
from .route_plan import plan_routes
from .safety import read_json, write_json, require


def build(snapshot, batch):
    g = copy.deepcopy(snapshot)
    if batch == 'b1':
        require(any(v['net']=='SYS' and v['position']==[75.5,61.65]
                    for v in g['vias'].values()), 'Expected source SYS via is missing')
        g['pads']['existing-sys-via'] = dict(ref='@SYS', pin='1', net='SYS',
            position=[75.5, 61.65], drill_size=[0, 0], polygons={})
    result = dict(failure=None, tracks=[], vias=[], metrics=[])
    groups = {
        'b1': [
            (.8, [42, 59, 78, 89], ['SYS', '@SYS', '1', 'C32', '1']),
            (.6, [53, 82, 64, 89], ['MAIN_3V3', 'C45', '1', 'C70', '1']),
            (.28, [61, 81, 66, 86], ['MAIN_3V3', 'C70', '1', 'U5', '3']),
        ],
        'b2': [
            (.3, [116, 77, 120.5, 85], ['USB_VBUS', 'J7', 'A9', 'J7', 'B4']),
            (.3, [116, 77, 120.5, 85], ['USB_VBUS', 'J7', 'A4', 'J7', 'B9']),
            (.3, [115, 77, 120.5, 85], ['USB_VBUS', 'J7', 'A9', 'J7', 'A4']),
            (.6, [102, 77, 120, 86], ['USB_VBUS', 'J7', 'A9', 'U4', '1']),
            (.6, [101, 79, 107, 82], ['USB_VBUS', 'U4', '1', 'C27', '1']),
            (.3, [116, 82, 121, 89], ['USB_VBUS', 'J7', 'B9', 'C28', '1']),
            (.8, [103, 84, 108, 89], ['USB3V3', 'U4', '3', 'C35', '1']),
            (.5, [104, 86, 112, 90], ['USB3V3', 'C35', '1', 'C40', '1']),
            (.3, [108, 86, 114, 91], ['USB3V3', 'C40', '1', 'R35', '1']),
            (.6, [66, 80, 107, 90], ['USB3V3', 'C35', '1', 'C71', '1']),
        ],
        'b3': [
            (.28, [63, 81, 69, 84], ['USB3V3', 'C71', '1', 'U5', '6']),
            (.28, [63, 80, 69, 83], ['MCU3V3', 'U5', '2', 'U5', '7']),
            (.28, [64, 79, 69, 83], ['MCU3V3', 'U5', '7', 'C36', '1']),
            (.2, [62, 81, 67, 85], ['MAIN_3V3', 'U5', '3', 'U5', '5']),
            (.2, [59, 78, 66, 85], ['MAIN_3V3', 'C70', '1', 'R23', '1']),
            (.2, [59, 79, 63, 84], ['MUX_PR1', 'R23', '2', 'R24', '1']),
            (.2, [59, 79, 66, 85], ['MUX_PR1', 'R24', '1', 'U5', '4']),
        ],
    }
    require(batch in groups, 'Unspecified batch')
    def append(plan):
        for row in plan['tracks']:
            n, layer, w, x1, y1, x2, y2 = row
            g['tracks']['planned-' + str(len(g['tracks']))] = dict(
                net=n, layer=layer, width=w, start=[x1, y1], end=[x2, y2])
        for row in plan['vias']:
            n, x, y, d, drill = row
            g['vias']['planned-' + str(len(g['vias']))] = dict(
                net=n, position=[x, y], drill=drill,
                copper_widths={l: d for l in ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']})
        for key in ['tracks', 'vias', 'metrics']:
            result[key].extend(plan[key])
    if batch == 'b1':
        result['tracks'].append(['PGND', 'F.Cu', .4, 62.75, 85.275, 62.75, 85.85])
        result['vias'].append(['PGND', 62.75, 85.85, .6, .3])
        result['review_bounds'] = [42, 60, 72, 89]
    if batch == 'b2':
        result['tracks'].append(['PGND', 'F.Cu', 1.2, 105.85, 83, 112.15, 83])
        for x,y in [(110.9,82),(110.9,84),(113,82),(113,84),(105.25,83),(106.45,83)]:
            result['vias'].append(['PGND',x,y,.7,.3])
        for x1,y1,x2,y2 in [(101.55,80.7,100.9,80.7),(106.95,88,107.5,88),
                             (110.48,88,110.48,88.65),(113.01,89.5,113.65,89.5),
                             (120.48,87.4,121.1,87.4),(68.675,82.75,69.25,82.75)]:
            result['tracks'].append(['PGND','F.Cu',.4,x1,y1,x2,y2])
            result['vias'].append(['PGND',x2,y2,.6,.3])
        result['review_bounds'] = [99, 76, 124, 92]
    if batch == 'b3':
        for x1,y1,x2,y2 in [(64.26,81.25,64.65,81),(67.5,79.05,67.5,78.5),
                             (61.51,82,61.51,81.4)]:
            result['tracks'].append(['PGND','F.Cu',.28,x1,y1,x2,y2])
            result['vias'].append(['PGND',x2,y2,.5,.3])
        result['review_bounds'] = [58, 77, 71, 88]
    # Ground returns are obstacles for power routes, including same-batch additions.
    initial = copy.deepcopy(result)
    result['tracks'], result['vias'], result['metrics'] = [], [], []
    append(initial)
    for width, bounds, connection in groups[batch]:
        append(plan_routes(g, [connection], bounds, width,
                           source_layer='B.Cu' if connection[1] == '@SYS' else 'F.Cu'))
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--snapshot', required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    result = build(read_json(a.snapshot), a.batch)
    write_json(a.output, result)
    print(dict(tracks=len(result['tracks']), vias=len(result['vias']), metrics=result['metrics']))


if __name__ == '__main__':
    main()
