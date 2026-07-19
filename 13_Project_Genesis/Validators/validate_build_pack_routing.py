\
from __future__ import annotations
import json, sys, zipfile
from pathlib import Path, PurePosixPath

ALLOWED_ROOTS={'00_Governance','01_Knowledge_Systems','02_Peptides','03_Biology','04_Conditions','05_Monitoring','06_Evidence','07_Goals','08_Product_Passports','09_Cost_Intelligence','10_Marketplace','11_Academy','12_Reports','13_Project_Genesis','Assets','Database','Documentation','Images','Schemas','Scripts','Standards','Templates'}

def validate(path):
    errors=[]; seen=set()
    with zipfile.ZipFile(path) as zf:
        files=[x.filename for x in zf.infolist() if not x.is_dir()]
        roots={PurePosixPath(x).parts[0] for x in files if PurePosixPath(x).parts}
        if len(roots)==1 and next(iter(roots),'') not in ALLOWED_ROOTS: errors.append('BUILD_WRAPPER_FOLDER')
        for name in files:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts: errors.append(f'UNSAFE_PATH:{name}')
            elif not p.parts or p.parts[0] not in ALLOWED_ROOTS: errors.append(f'UNAUTHORISED_ROOT:{name}')
            if '__pycache__' in p.parts or name.endswith('.pyc'): errors.append(f'CACHE_FILE:{name}')
            key=name.lower()
            if key in seen: errors.append(f'DUPLICATE_OR_CASE_COLLISION:{name}')
            seen.add(key)
    return errors

def main():
    errors=validate(Path(sys.argv[1])); print(json.dumps({'valid':not errors,'errors':errors},indent=2)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
