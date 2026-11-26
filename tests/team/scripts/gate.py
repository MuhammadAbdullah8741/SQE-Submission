from pathlib import Path
import json,sys,xml.etree.ElementTree as E
r=Path(__file__).resolve().parents[3];mode=sys.argv[1]
if mode=='coverage':
 tree=E.parse(r/'target/site/jacoco/jacoco.xml');selected=['IssueReturnService','FineService']
 for name in selected:
  c=next(c for c in tree.findall('.//class') if c.attrib['name'].endswith('/'+name))
  for counter in c.findall('counter'):
   if counter.attrib['type'] in ['LINE','BRANCH']:assert int(counter.attrib['missed'])==0,(name,counter.attrib)
 stock_scope={'com/bookflow/model/Book':{'onCreate','onUpdate','syncStatus','hasAvailableCopies','decrementAvailable','incrementAvailable'},'com/bookflow/service/BookService':{'getByIsbn','decrementStock','incrementStock'}}
 for class_name,method_names in stock_scope.items():
  cls=next(c for c in tree.findall('.//class') if c.attrib['name']==class_name)
  methods={m.attrib['name']:m for m in cls.findall('method')}
  for method_name in method_names:
   for counter in methods[method_name].findall('counter'):
    if counter.attrib['type'] in ['LINE','BRANCH']:assert int(counter.attrib['missed'])==0,(class_name,method_name,counter.attrib)
elif mode=='mutation':
 muts=E.parse(r/'target/pit-reports/mutations.xml').findall('.//mutation');effective=[m for m in muts if m.attrib.get('status') not in ['NO_COVERAGE']]
 score=sum(m.attrib.get('detected')=='true' for m in muts)/len(muts)
 assert score>=0.80,('PIT score below 80%',score)
 assert all(m['killed'] for m in json.loads((r/'tests/team/evidence/custom-mutants.json').read_text()))
elif mode=='sonar':
 result=json.loads((r/'tests/team/evidence/sonar-gate.json').read_text());assert result['projectStatus']['status']=='OK',result
print(mode,'gate passed')
