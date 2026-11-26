"""Contract checks: changed constraints must change valid values and all BVA neighbours."""
from pathlib import Path
import json
root=Path(__file__).parent
outputs={}
for suffix in ['', '-changed']:
 spec=json.loads((root/f'openapi{suffix}.json').read_text());cases=json.loads((root/f'generated{suffix}.json').read_text())
 assert len({c['id'] for c in cases})==len(cases),(suffix,'duplicate case IDs')
 outputs[suffix]=cases
 for path,ops in spec['paths'].items():
  for method,op in ops.items():
   schemas={p['name']:p['schema'] for p in op.get('parameters',[])}
   if 'requestBody' in op:schemas.update(op['requestBody']['content']['application/x-www-form-urlencoded']['schema']['properties'])
   defaults={name:next(c['data'][name] for c in cases if c['path']==path and c['method']==method and c['input']==name and c['partition']=='valid') for name in schemas}
   for name,s in schemas.items():
    selected=[c for c in cases if c['path']==path and c['method']==method and c['input']==name]
    assert selected,(suffix,path,method,name,'no generated cases')
    for case in selected:
     assert set(case['data'])==set(schemas),(suffix,case['id'],'wrong input set')
     assert all(case['data'][other]==defaults[other] for other in schemas if other!=name),(suffix,case['id'],'more than one field varied')
    valid=next(c['data'][name] for c in selected if c['partition']=='valid')
    if s['type']=='integer':
     assert {'valid','empty','wrong-type'}<={c['partition'] for c in selected},(suffix,path,name,'missing EP class')
     assert s.get('minimum',int(valid))<=int(valid)<=s.get('maximum',int(valid)),(suffix,path,name,valid)
     values={int(c['data'][name]) for c in selected if str(c['data'][name]).lstrip('-').isdigit()}
     for bound in ['minimum','maximum']:
      if bound in s:assert {s[bound]-1,s[bound],s[bound]+1}<=values,(suffix,path,name,bound)
    else:
     assert {'valid','empty','whitespace','unknown'}<={c['partition'] for c in selected},(suffix,path,name,'missing EP class')
     assert s.get('minLength',0)<=len(valid)<=s.get('maxLength',len(valid)),(suffix,path,name)
     lengths={len(c['data'][name]) for c in selected}
     for bound in ['minLength','maxLength']:
      if bound in s:assert {max(0,s[bound]-1),s[bound],s[bound]+1}<=lengths,(suffix,path,name,bound)

def values(suffix,path,method,name,prefix,include_valid=False):
 return {int(c['data'][name]) if str(c['data'][name]).lstrip('-').isdigit() else len(c['data'][name]) for c in outputs[suffix] if c['path']==path and c['method']==method and c['input']==name and (c['partition'].startswith(prefix) or include_valid and c['partition']=='valid')}
assert values('', '/librarian/issue','post','memberId','maxLength')=={24,25,26}
assert values('-changed','/librarian/issue','post','memberId','maxLength')=={19,20,21}
assert values('', '/librarian/return','post','txnId','minimum',True)=={0,1,2}
assert values('-changed','/librarian/return','post','txnId','minimum',True)=={1,2,3}
print('PASS: unique cases, one-field variation, EP classes, 3-point boundaries and both changed constraints verified')
