"""Two rule-specific source operators, each restoring the exact source in finally."""
from pathlib import Path
import subprocess,json,time,shutil
r=Path(__file__).resolve().parents[3];p=r/'src/main/java/com/bookflow/service/IssueReturnService.java';original=p.read_text();mvn=shutil.which('mvn') or str(r.parent/'.tools/apache-maven-3.9.9/bin/mvn.cmd');out=[]
operators=[('LOAN_LIMIT_OFF_BY_ONE','activeCount >= borrowLimit','activeCount > borrowLimit'),('FINE_ON_DUE_DATE','if (overdueDays > 0)','if (overdueDays >= 0)')]
try:
 for name,old,new in operators:
  assert original.count(old)==1
  p.write_text(original.replace(old,new))
  with (r/f'tests/team/evidence/mutant-{name}.log').open('w') as f:code=subprocess.call([mvn,'-B','-ntp','-Dtest=IssueReturnTest','test'],cwd=r,stdout=f,stderr=subprocess.STDOUT)
  out.append({'operator':name,'replacement':[old,new],'exitCode':code,'killed':code!=0})
finally:p.write_text(original)
(r/'tests/team/evidence/custom-mutants.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
