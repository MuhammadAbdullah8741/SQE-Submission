"""OSV public vulnerability database audit of resolved Maven dependencies."""
import requests,json,xml.etree.ElementTree as ET
from pathlib import Path
r=Path(__file__).resolve().parents[3];e=r/'tests/team/evidence'
deps=json.loads((e/'dependencies.json').read_text())
def walk(n):
 yield n
 for c in n.get('children',[]):yield from walk(c)
packages={n['groupId']+':'+n['artifactId']:n['version'] for n in walk(deps) if n.get('groupId')!='com.bookflow'}
queries=[{'package':{'ecosystem':'Maven','name':n},'version':v} for n,v in packages.items()]
response=requests.post('https://api.osv.dev/v1/querybatch',json={'queries':queries},timeout=120);response.raise_for_status()
rows=[{**q,'vulnerabilities':result.get('vulns',[])} for q,result in zip(queries,response.json()['results'])]
(e/'dependency-audit.json').write_text(json.dumps({'tool':'OSV public API, open-source OSV database','packages':rows},indent=2))
print(len(rows),'packages checked;',sum(bool(r['vulnerabilities']) for r in rows),'with advisories')
