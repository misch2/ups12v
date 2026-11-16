"""Safety negatives for scratch replacement; no native imports."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v4kicad.replacement import remaining, preserved, serialized_retained
from v4kicad.safety import ToolError


class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.track = dict(uuid='old', net='N', kind='track', layer='F.Cu', width=.3, start=[0, 0], end=[1, 0])
        self.g = dict(tracks={'old':self.track}, vias={}, pads={}, footprints={}, zones={})
        self.context = dict(snapshot=self.g, board_sha256='accepted')
        self.plan = dict(mode='scratch-track-replacement', baseline_sha256='accepted',
                         remove_tracks={'old':self.track}, tracks=[['N','F.Cu',.3,0,0,1,0]], vias=[])

    def test_exact_original_is_required(self):
        bad = copy.deepcopy(self.plan)
        bad['remove_tracks']['old']['width'] = .31
        with self.assertRaises(ToolError): remaining(self.context, bad)

    def test_no_vias_placement_net_or_layer_changes(self):
        for patch in [dict(vias=[['N',0,0,.6,.3]]), dict(placements={'U1':[1,1,0]}),
                      dict(tracks=[['X','F.Cu',.3,0,0,1,0]]), dict(tracks=[['N','B.Cu',.3,0,0,1,0]])]:
            with self.subTest(patch=patch):
                with self.assertRaises(ToolError): remaining(self.context, dict(self.plan, **patch))

    def test_retained_objects_and_exact_new_geometry(self):
        self.g['tracks']['keep'] = dict(self.track, uuid='keep',start=[1,0],end=[2,0])
        new = dict(self.track, uuid='new')
        after = dict(self.g, tracks={'new':new,'keep':self.g['tracks']['keep']})
        preserved(self.g, after, self.plan, {'new':new})
        for altered in [dict(after, vias={'unexpected':{}}),
                        dict(after, tracks={'new':dict(new, width=.300001),'keep':self.g['tracks']['keep']}),
                        dict(after, tracks={'new':new,'keep':dict(self.g['tracks']['keep'],width=.29)}),
                        dict(after, pads={'unexpected':{}})]:
            with self.assertRaises(ToolError): preserved(self.g, altered, self.plan, {'new':new})

    def test_only_enumerated_tracks_and_derived_fill_excluded(self):
        source = '(kicad_pcb (version 1) (generator pcbnew) (segment (uuid "old") (width .3)) (footprint (property "x" "a")) (zone (net 1) (filled_polygon (pts (xy 1 2)))))'
        target = source.replace('"old"', '"new"').replace('pcbnew)', 'other)').replace('(xy 1 2)', '(xy 3 4)')
        with tempfile.TemporaryDirectory() as tmp:
            a,b = Path(tmp)/'a',Path(tmp)/'b'
            a.write_text(source);b.write_text(target)
            self.assertEqual(serialized_retained(a,['old']), serialized_retained(b,['new']))
            b.write_text(target.replace('"x" "a"','"x" "b"'))
            self.assertNotEqual(serialized_retained(a,['old']), serialized_retained(b,['new']))
            b.write_text(target.replace('(net 1)','(net 2)'))
            self.assertNotEqual(serialized_retained(a,['old']), serialized_retained(b,['new']))

    def test_clearance_measures_copper_edges_instead_of_centerlines(self):
        from v4kicad.legacy_review import clearance
        n = dict(self.track, end=[2,0], width=.2)
        m = dict(self.track, uuid='other',net='M',start=[0,.6],end=[2,.6],width=.4)
        g = dict(self.g, tracks={'old':n,'other':m})
        result = clearance(g,[n],{})
        self.assertAlmostEqual(result['gap_mm'],.3)
        self.assertEqual(result['neighbour_uuid'],'other')
        self.assertAlmostEqual(result['location']['on_candidate'][1],.1)
        self.assertAlmostEqual(result['location']['on_neighbour'][1],.4)

    def test_add_only_serialized_comparison_excludes_exact_new_via_only(self):
        source='(kicad_pcb (version 1) (via (uuid "retained") (drill .3)))'
        added='(via (uuid "added") (drill .3))'
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            a.write_text(source);b.write_text(source[:-1]+added+')')
            self.assertNotEqual(serialized_retained(a),serialized_retained(b))
            self.assertEqual(serialized_retained(a),serialized_retained(b,['added']))
            b.write_text((source[:-1]+added+')').replace('(drill .3)','(drill .4)',1))
            self.assertNotEqual(serialized_retained(a),serialized_retained(b,['added']))

    def test_same_net_drills_reduce_effective_strip_width(self):
        from v4kicad.legacy_review import conducting_width
        from v4kicad.plan_validation import drill
        track=dict(self.track,start=[0,0],end=[2,0],width=1.2)
        holes=[drill('center','N',[1,0],[.4,.4]),drill('edge','N',[1,.7],[.4,.4])]
        result=conducting_width([track],holes)
        self.assertAlmostEqual(result['minimum_mm'],.7)
        self.assertEqual(set(result['drill_uuids']),{'center','edge'})

    def test_identical_collinear_union_uses_same_reference_samples(self):
        from v4kicad.legacy_review import reference_samples
        a = dict(self.track,start=[0,0],end=[1,0],width=.2)
        b = dict(a,uuid='b',start=[1,0],end=[2,0])
        merged = dict(a,end=[2,0])
        plane = dict(outline=[[-1,-1],[3,-1],[3,1],[-1,1]],holes=[])
        layout = dict(fills={'plane':dict(net='PGND',layers={'In1.Cu':[plane]})})
        split = reference_samples(self.g,[a,b],layout,{})
        whole = reference_samples(self.g,[merged],layout,{})
        self.assertEqual(split,whole)
        self.assertEqual(whole['samples'],whole['PGND_copper_samples'])
        plane['holes']=[[[.5,-.3],[.6,-.3],[.6,.3],[.5,.3]]]
        cut = reference_samples(self.g,[merged],layout,{})
        self.assertGreater(len(cut['missing_samples']),0)


if __name__ == '__main__': unittest.main()
