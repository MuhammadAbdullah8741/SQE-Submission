from pathlib import Path
import json
r=Path(__file__).resolve().parents[3]
p=r/'.gitignore';s=p.read_text();s+='\n.sonar/\n!tests/team/evidence/*.log\ntests/team/evidence/app*.log\n';p.write_text(s)
p=r/'pom.xml';s=p.read_text();s=s.replace('<threads>2</threads>','<threads>2</threads><mutators><mutator>ALL</mutator></mutators>');p.write_text(s)
src=r/'tests/team/evidence/app.log'
if src.exists():
 lines=src.read_text(encoding='utf-8',errors='replace').splitlines();selected=[l for l in lines if 'Cannot convert' in l or 'ELException' in l]
 (r/'tests/team/evidence/dashboard-date-error.txt').write_text('\n'.join(selected[:12]),encoding='utf-8')
p=r/'tests/team/scripts/build_report.py';s=p.read_text();needle="page('20. Root-cause analyses and prevention')"
insert="""page('19b. Findings: causes and corrections')
table(['Finding / severity / risk','Root cause','Correction / triage'],[[x['id']+' / '+x['severity']+' / '+x['risk'],x['rootCause'],x['fix']] for x in defects if x['id'] in ['D05','D06','D07','D08','D09','D10']],[100,185,220])
para('Per-ZAP-category observed risk, response evidence, likely impact and proposed correction are retained in security-findings.json. Dependency observations identify each affected package/version and advisory in dependency-audit.json; applicability and upgrade paths require review. Successful performance runs create no performance defect; their residual risk is that a local read workload does not establish production write capacity.')
"""
s=s.replace(needle,insert+needle);p.write_text(s,encoding='utf-8')
