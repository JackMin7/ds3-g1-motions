"""Validate the BVH/CSV catalog and optional motion files. No robot model needed."""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def load_catalog(root):
    manifest=json.loads((root/'manifest.json').read_text())
    rows=[json.loads(line) for name in manifest['catalog_files']
          for line in (root/name).read_text().splitlines() if line]
    assert len(rows)==manifest['motion_count']==3707
    assert len({r['key'] for r in rows})==len(rows)
    assert all(r['status']=='kept' and set(r['files'])=={'bvh','csv'} for r in rows)
    split=(root/'splits/kept.txt').read_text().splitlines()
    assert len(split)==len(set(split)) and set(split)=={r['key'] for r in rows}
    return manifest,rows


def read_bvh(path):
    import numpy as np
    text=path.read_text()
    header,motion=re.split(r'(?m)^MOTION\s*$',text,maxsplit=1)
    channels=sum(map(int,re.findall(r'\bCHANNELS\s+(\d+)',header)))
    names=re.findall(r'(?m)^\s*(?:ROOT|JOINT)\s+([^\r\n]+)',header)
    frames=int(re.search(r'Frames:\s*(\d+)',motion).group(1))
    time=re.search(r'Frame Time:\s*([^\r\n]+)',motion)
    dt=float(time.group(1));assert dt>0
    values=np.loadtxt(io.StringIO(motion[time.end():]),ndmin=2)
    assert values.shape==(frames,channels) and np.isfinite(values).all()
    return frames,1/dt,[n.strip() for n in names]


def verify(root,catalog_only=False):
    _,rows=load_catalog(root)
    for line in (root/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1);path=(root/name).resolve()
        assert path.is_relative_to(root.resolve()) and sha(path)==digest,name
    if catalog_only:
        print('CATALOG_OK',len(rows),'BVH/CSV pairs');return
    import numpy as np
    schema=json.loads((root/'data/schema.json').read_text())
    for i,row in enumerate(rows):
        paths={}
        for kind,info in row['files'].items():
            path=root/info['path'];assert not path.is_symlink()
            assert path.resolve().is_relative_to(root.resolve()),info['path']
            assert path.is_file() and path.stat().st_size==info['bytes'] and sha(path)==info['sha256'],info['path']
            paths[kind]=path
        frames,fps,names=read_bvh(paths['bvh'])
        csv=np.loadtxt(paths['csv'],delimiter=',',ndmin=2)
        assert csv.shape==(frames,36)==(row['frames'],36)
        assert np.isfinite(csv).all()
        assert np.max(np.abs(np.linalg.norm(csv[:,3:7],axis=1)-1))<1e-5
        assert abs(fps-row['fps'])<1e-4 and fps>0
        assert abs((frames-1)/fps-row['duration_seconds'])<1e-4
        assert names==schema['bvh']['joint_names']
        if (i+1)%500==0:print('VALIDATED',i+1,flush=True)
    print('DATA_OK',len(rows),'BVH/CSV pairs; hashes, finite values, frame counts, quaternions, skeleton names, timing')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--catalog-only',action='store_true')
    args=parser.parse_args();verify(args.root,args.catalog_only)
