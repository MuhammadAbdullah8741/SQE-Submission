"""Four sequential, isolated 65-second k6 runs; retain failed thresholds as evidence."""
from pathlib import Path
import subprocess,json,platform,time
r=Path(__file__).resolve().parents[3];e=r/'tests/team/evidence'
env={'recorded_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'platform':platform.platform(),'processor':platform.processor(),'duration_seconds':65,'operation':'authenticated availability precheck','targets':{'p95_ms':500,'unexpected_failure_rate':0.01}}
for key,args in [('java',['java','-version']),('docker',['docker','version']),('node',['node','--version']),('k6',['docker','run','--rm','grafana/k6:latest','version'])]:
 env[key]=subprocess.run(args,capture_output=True,text=True).stdout+subprocess.run(args,capture_output=True,text=True).stderr
(e/'environment.json').write_text(json.dumps(env,indent=2))
results=[]
for users in [1,5]:
 for repeat in [1,2]:
  subprocess.run(['node','tests/team/scripts/seed.cjs'],cwd=r,check=True)
  print(f'Starting {users} VU run {repeat} (65 seconds)',flush=True)
  with (e/f'k6-{users}-{repeat}.log').open('w') as f:
   p=subprocess.run(['docker','run','--rm','-e',f'VUS={users}','-v',f'{r}:/work','grafana/k6:latest','run','--summary-export',f'/work/tests/team/evidence/k6-{users}-{repeat}.json','/work/tests/team/performance/workload.js'],cwd=r,stdout=f,stderr=subprocess.STDOUT)
  results.append({'vus':users,'run':repeat,'exitCode':p.returncode})
  (e/'k6-run-status.json').write_text(json.dumps(results,indent=2))
  print('Completed',results[-1],flush=True)
