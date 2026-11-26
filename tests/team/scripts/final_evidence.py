from pathlib import Path
import json,xml.etree.ElementTree as ET,hashlib,subprocess,shutil
r=Path(__file__).resolve().parents[3];e=r/'tests/team/evidence'
def read(name):return json.loads((e/name).read_text(encoding='utf-8-sig'))
rows=[]
for path in (r/'target/surefire-reports').glob('TEST-*.xml'):
 root=ET.parse(path).getroot();rows.append({k:root.attrib.get(k) for k in ['name','tests','failures','errors','skipped','time']})
(e/'junit-summary.json').write_text(json.dumps(rows,indent=2))
dest=e/'coverage';shutil.copytree(r/'target/site/jacoco',dest,dirs_exist_ok=True)
shutil.copytree(r/'target/pit-reports',e/'mutation',dirs_exist_ok=True)
shutil.copytree(r/'target/surefire-reports',e/'junit',dirs_exist_ok=True)
summary=[]
for users in [1,5]:
 for run in [1,2]:
  data=read(f'k6-{users}-{run}.json')['metrics'];lat=data['http_req_duration{operation:precheck}'];lat=lat.get('values',lat);fail=data['unexpected_failures'];fail=fail.get('values',fail);req=data['http_reqs'];req=req.get('values',req)
  summary.append({'vus':users,'repeat':run,'p95_ms':lat['p(95)'],'requests_per_second_including_setup':req['rate'],'unexpected_failure_rate':fail.get('rate',fail.get('value')),'thresholds_pass':lat['p(95)']<500 and fail.get('rate',fail.get('value'))<0.01})
(e/'performance-summary.json').write_text(json.dumps(summary,indent=2))
sources={str(p.relative_to(r)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'src').rglob('*') if p.is_file()}
sources['target/bookflow.war']=hashlib.sha256((r/'target/bookflow.war').read_bytes()).hexdigest()
(e/'tested-build-sha256.json').write_text(json.dumps(sources,indent=2))
alerts=read('zap-passive.json')['alerts'];findings=[]
for title in sorted(set(a['alert'] for a in alerts)):
 group=[a for a in alerts if a['alert']==title];a=group[0]
 findings.append({'component':title,'observed_risk':a.get('risk'),'root_cause':'Observed response/session configuration permits the condition described by ZAP; manually review applicability.','risk_register':'R01','impact':a.get('description'),'fix':a.get('solution'),'evidence':list(dict.fromkeys(x.get('url') for x in group)),'deduplicated_instances':len(group)})
(e/'security-findings.json').write_text(json.dumps(findings,indent=2))
print(json.dumps({'unit_suites':rows,'performance':summary},indent=2))
