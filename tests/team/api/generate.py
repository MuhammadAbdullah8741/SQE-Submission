"""Read OpenAPI form/query schemas; emit EP and three-point boundary cases.
The API runner consumes the baseline output; the changed output demonstrates regeneration.
"""
import json,sys,copy
from pathlib import Path
root=Path(__file__).parent
def valid_example(schema):
 value=schema['example']
 if schema['type']=='integer':return max(schema.get('minimum',value),min(schema.get('maximum',value),value))
 value=str(value)
 if 'maxLength' in schema:value=value[:schema['maxLength']]
 return value.ljust(schema.get('minLength',0),'A')
def generate(spec):
 out=[]
 for path,methods in spec['paths'].items():
  for method,op in methods.items():
   schemas={p['name']:p['schema'] for p in op.get('parameters',[])}
   if 'requestBody' in op:schemas.update(op['requestBody']['content']['application/x-www-form-urlencoded']['schema']['properties'])
   defaults={k:valid_example(v) for k,v in schemas.items()}
   for name,s in schemas.items():
    vals=[('valid',defaults[name])]
    if s['type']=='string':
     vals += [('empty',''),('whitespace',' '),('unknown','UNKNOWN')]
     for bound in ['minLength','maxLength']:
      if bound in s:
       for delta in [-1,0,1]:vals.append((bound+str(delta), 'A'*max(0,s[bound]+delta)))
    else:
     vals += [('wrong-type','abc'),('empty','')]
     for bound in ['minimum','maximum']:
      if bound in s:
       for delta in [-1,0,1]:vals.append((bound+str(delta),s[bound]+delta))
    seen=set()
    for group,value in vals:
     key=json.dumps(value)
     if key in seen:continue
     seen.add(key);data={k:str(v) if schemas[k]['type']=='integer' else v for k,v in defaults.items()};data[name]=str(value) if s['type']=='integer' else value
     out.append({'id':f'{method}-{path.split("/")[-1]}-{name}-{group}','path':path,'method':method,'input':name,'partition':group,'data':data})
 return out
spec=json.loads((root/'openapi.json').read_text())
(root/'generated.json').write_text(json.dumps(generate(spec),indent=2))
changed=copy.deepcopy(spec)
changed['paths']['/librarian/issue']['post']['requestBody']['content']['application/x-www-form-urlencoded']['schema']['properties']['memberId']['maxLength']=20
changed['paths']['/librarian/return']['post']['parameters'][0]['schema']['minimum']=2
(root/'openapi-changed.json').write_text(json.dumps(changed,indent=2))
(root/'generated-changed.json').write_text(json.dumps(generate(changed),indent=2))
print('Generated',len(generate(spec)),'normal and',len(generate(changed)),'changed cases')
