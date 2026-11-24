"""Show one paired motion's catalog entry. This is not a player."""
import argparse
import json
from pathlib import Path
from validate_dataset import load_catalog

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--key',required=True)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
args=parser.parse_args()
_,rows=load_catalog(args.root)
row=next((r for r in rows if r['key']==args.key),None)
if row is None:parser.error('Unknown key in the current kept set')
print(json.dumps(row,ensure_ascii=False,indent=2))
for kind,info in row['files'].items():
    print(kind,':','present' if (args.root/info['path']).is_file() else 'missing from this checkout')
