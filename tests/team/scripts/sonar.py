import requests,json,time,subprocess,os,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[3];e=r/'tests/team/evidence';url='http://localhost:9000'
s=requests.Session();s.auth=('admin','admin')
for _ in range(60):
 try:
  if s.get(url+'/api/system/status',timeout=5).json().get('status')=='UP':break
 except requests.RequestException:pass
 time.sleep(3)
s.post(url+'/api/projects/create',data={'project':'bookflow-sqe','name':'BookFlow SQE'},timeout=30)
gates=s.get(url+'/api/qualitygates/list',timeout=30).json().get('qualitygates',[])
gate=next((g for g in gates if g['name']=='SQE circulation gate'),None)
if not gate:
 gate=s.post(url+'/api/qualitygates/create',data={'name':'SQE circulation gate'},timeout=30).json()
 for metric,threshold in [('bugs','0'),('vulnerabilities','0'),('duplicated_lines_density','5')]:
  response=s.post(url+'/api/qualitygates/create_condition',data={'gateName':'SQE circulation gate','metric':metric,'op':'GT','error':threshold},timeout=30);response.raise_for_status()
s.post(url+'/api/qualitygates/select',data={'projectKey':'bookflow-sqe','gateName':'SQE circulation gate'},timeout=30).raise_for_status()
token=s.post(url+'/api/user_tokens/generate',data={'name':'sqe-'+str(int(time.time()))},timeout=30).json()['token']
env=dict(os.environ,SONAR_TOKEN=token)
mvn=shutil.which('mvn') or str(r.parent/'.tools/apache-maven-3.9.9/bin/mvn.cmd')
with (e/'sonar-scan.log').open('w') as f:
 code=subprocess.call([mvn,'-B','-ntp','org.sonarsource.scanner.maven:sonar-maven-plugin:5.1.0.4751:sonar','-Dsonar.host.url='+url,'-Dsonar.projectKey=bookflow-sqe','-Dsonar.sources=src/main/java','-Dsonar.tests=tests/team/java','-Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml'],cwd=r,env=env,stdout=f,stderr=subprocess.STDOUT)
if code:raise SystemExit(code)
task={line.split('=',1)[0]:line.split('=',1)[1] for line in (r/'target/sonar/report-task.txt').read_text().splitlines() if '=' in line}
for _ in range(120):
 status=s.get(task['ceTaskUrl'],timeout=20).json()['task']['status']
 if status=='SUCCESS':break
 if status in ['FAILED','CANCELED']:raise SystemExit('Sonar processing '+status)
 time.sleep(3)
else:raise SystemExit('Sonar processing timeout')
for endpoint,params,name in [('measures/component',{'component':'bookflow-sqe','metricKeys':'ncloc,complexity,cognitive_complexity,duplicated_lines_density,code_smells,bugs,vulnerabilities,coverage,sqale_index,reliability_rating,security_rating,sqale_rating'},'sonar-metrics'),('issues/search',{'componentKeys':'bookflow-sqe','ps':500},'sonar-issues'),('qualitygates/project_status',{'projectKey':'bookflow-sqe'},'sonar-gate')]:
 response=s.get(url+'/api/'+endpoint,params=params,timeout=60);response.raise_for_status();(e/(name+'.json')).write_text(json.dumps(response.json(),indent=2))
print('Sonar evidence saved')
