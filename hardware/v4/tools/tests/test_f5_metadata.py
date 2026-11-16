import copy
import unittest
from v4kicad.safety import read_json,ToolError
from v4kicad.f5_metadata import default_units_only


class F5MetadataTests(unittest.TestCase):
    def test_default_cache_omission_and_negative_controls(self):
        root='hardware/v4/evidence/phase4-18-rehearsal-native/'
        d=read_json(root+'serialized-diagnostic.json');g=read_json(root+'snapshot.json')
        p=read_json('hardware/v4/evidence/phase4-17-final-candidate-v2/plan.json')['placements']
        self.assertEqual(len(default_units_only(d,g,p)['omitted_optional_single_A_unit_caches']),18)
        for kind in ['missing_pin','duplicate_pin','unit_B','new_metadata','outside_scope','shape']:
            bad=copy.deepcopy(d)
            n=bad['before_only'][0];u=next(x for x in n if isinstance(x,list) and x[0]=='units')[1]
            if kind=='missing_pin':u[2].pop()
            elif kind=='duplicate_pin':u[2].append(u[2][-1])
            elif kind=='unit_B':u[1][1]='"B"'
            elif kind=='new_metadata':bad['after_only'][0].append(['attr','dnp'])
            elif kind=='outside_scope':bad['before_only'].pop()
            else:next(x for x in bad['after_only'][0] if isinstance(x,list) and x[0]=='pad')[1]='"wrong"'
            with self.assertRaises(ToolError):default_units_only(bad,g,p)


if __name__=='__main__':unittest.main()
