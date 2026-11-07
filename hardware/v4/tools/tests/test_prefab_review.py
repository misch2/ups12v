import unittest
from v4kicad.prefab_review import ring


class PrefabRingTests(unittest.TestCase):
    def pad(self,shape,size,hole,offset=None):
        xy=lambda p:dict(xNm=str(round(p[0]*1e6)),yNm=str(round(p[1]*1e6)))
        return dict(padStack=dict(drill=dict(diameter=xy(hole)),copperLayers=[dict(shape=shape,size=xy(size),offset=xy(offset or [0,0]))]))

    def test_usb_pth_at_multilayer_absolute_floor(self):
        self.assertAlmostEqual(ring(self.pad('PSS_CIRCLE',[.7,.7],[.4,.4])),.15)

    def test_slot_checks_both_axes(self):
        self.assertAlmostEqual(ring(self.pad('PSS_OVAL',[.9,2.4],[.6,2.1])),.15)
        self.assertAlmostEqual(ring(self.pad('PSS_OVAL',[.9,2.2],[.6,2.1])),.05)

    def test_offset_is_not_silently_accepted(self):
        self.assertIsNone(ring(self.pad('PSS_CIRCLE',[.7,.7],[.4,.4],[.02,0])))

    def test_custom_is_unevaluated(self):
        self.assertIsNone(ring(self.pad('PSS_CUSTOM',[.7,.7],[.4,.4])))
