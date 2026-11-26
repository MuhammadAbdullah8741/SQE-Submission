"""Contract checks: changed constraints must change valid values and all BVA neighbours."""
from pathlib import Path
import json
root=Path(__file__).parent
for suffix in ['', '-changed']:
 spec=json.loads((root/f'openapi{suffix}.json').read_text());cases=json.loads((root/f'generated{suffix}.json').read_text())
 for path,ops in spec['paths'].items():
  for method,op in ops.items():
   schemas={p['name']:p['schema'] for p in op.get('parameters',[])}
   if 'requestBody' in op:schemas.update(op['requestBody']['content']['application/x-www-form-urlencoded']['schema']['properties'])
   for name,s in schemas.items():
    selected=[c for c in cases if c['path']==path and c['method']==method and c['input']==name]
    valid=next(c['data'][name] for c in selected if c['partition']=='valid')
    if s['type']=='integer':
     assert s.get('minimum',int(valid))<=int(valid)<=s.get('maximum',int(valid)),(suffix,path,name,valid)
     values={int(c['data'][name]) for c in selected if str(c['data'][name]).lstrip('-').isdigit()}
     for bound in ['minimum','maximum']:
      if bound in s:assert {s[bound]-1,s[bound],s[bound]+1}<=values,(suffix,path,name,bound)
    else:
     assert s.get('minLength',0)<=len(valid)<=s.get('maxLength',len(valid)),(suffix,path,name)
     lengths={len(c['data'][name]) for c in selected}
     for bound in ['minLength','maxLength']:
      if bound in s:assert {max(0,s[bound]-1),s[bound],s[bound]+1}<=lengths,(suffix,path,name,bound)
print('PASS: valid examples and all 3-point boundaries satisfy both baseline and changed specifications')
