\
import importlib.util, tempfile, unittest, zipfile
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Validators'/'validate_build_pack_routing.py'
spec=importlib.util.spec_from_file_location('routing_validator',P); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
class TestBuildPackRouting(unittest.TestCase):
    def make(self,names):
        p=Path(tempfile.mkdtemp())/'x.zip'
        with zipfile.ZipFile(p,'w') as z:
            for n in names: z.writestr(n,'x')
        return p
    def test_flat_canonical_passes(self): self.assertEqual([],mod.validate(self.make(['00_Governance/a.md','Documentation/Build_Records/0038/x.json'])))
    def test_wrapper_rejected(self): self.assertIn('BUILD_WRAPPER_FOLDER',mod.validate(self.make(['Certiaura_Build_0038/00_Governance/a.md'])))
    def test_unknown_root_rejected(self): self.assertTrue(any(x.startswith('UNAUTHORISED_ROOT') for x in mod.validate(self.make(['Other/a.md','Documentation/x.md']))))
    def test_cache_rejected(self): self.assertTrue(any(x.startswith('CACHE_FILE') for x in mod.validate(self.make(['13_Project_Genesis/Tests/__pycache__/x.pyc','Documentation/x.md']))))
if __name__=='__main__': unittest.main()
