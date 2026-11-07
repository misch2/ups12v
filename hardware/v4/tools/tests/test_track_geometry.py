"""Arc regressions: never count a curved conductor as its chord."""
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from v4kicad.track_geometry import track_length,track_points,arc_geometry
from v4kicad.geometry import inventory_row
from v4kicad.safety import ToolError


class ArcGeometryTests(unittest.TestCase):
    def test_quarter_circle_length_and_bounded_chord_error(self):
        t=dict(geometry='arc',start=[1,0],mid=[math.sqrt(.5)]*2,end=[0,1])
        self.assertAlmostEqual(track_length(t),math.pi/2)
        points=track_points(t)
        self.assertGreater(len(points),2)
        self.assertEqual(points[0],t['start']);self.assertEqual(points[-1],t['end'])
        for a,b in zip(points,points[1:]):
            self.assertLessEqual(1-math.hypot((a[0]+b[0])/2,(a[1]+b[1])/2),.0001+1e-12)

    def test_major_and_clockwise_arcs(self):
        t=dict(geometry='arc',start=[1,0],mid=[-1,0],end=[0,1])
        self.assertAlmostEqual(track_length(t),3*math.pi/2)
        self.assertLess(arc_geometry(t)[3],0)
        t=dict(t,start=[0,1],end=[1,0])
        self.assertAlmostEqual(track_length(t),3*math.pi/2)
        self.assertGreater(arc_geometry(t)[3],0)

    def test_degenerate_and_bad_native_length_refused(self):
        with self.assertRaises(ToolError):
            track_length(dict(geometry='arc',start=[0,0],mid=[1,0],end=[2,0]))
        with self.assertRaises(ToolError):
            track_length(dict(geometry='arc',start=[1,0],mid=[0,1],end=[-1,0],native_length_mm=2))

    def test_native_arc_exports_mid_and_actual_copper(self):
        class Track:pass
        class Arc(Track):
            m_Uuid=SimpleNamespace(AsString=lambda:'arc')
            def GetNetname(self):return 'USB_DP'
            def GetLayer(self):return 0
            def GetWidth(self):return 200000
            def GetStart(self):return SimpleNamespace(x=1000000,y=0)
            def GetMid(self):return SimpleNamespace(x=0,y=1000000)
            def GetEnd(self):return SimpleNamespace(x=-1000000,y=0)
            def GetLength(self):return math.pi*1000000
            def TransformShapeToPolygon(self,*args):self.call=args
        api=SimpleNamespace(PCB_ARC=Arc,PCB_TRACK=Track,PCB_VIA=type('Via',(),{}),
                            SHAPE_POLY_SET=object,ERROR_OUTSIDE=1)
        arc=Arc()
        with patch('v4kicad.geometry.polygons',return_value=[[[0,0],[1,0],[0,1]]]):
            row=inventory_row(arc,SimpleNamespace(GetLayerName=lambda l:'F.Cu'),api)
        self.assertEqual(row['mid'],[0,1]);self.assertEqual(row['geometry'],'arc')
        self.assertAlmostEqual(track_length(row),math.pi)
        self.assertEqual(arc.call[1:],(0,0,100,1))
