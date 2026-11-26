from pathlib import Path
r=Path(__file__).resolve().parents[3];p=r/'tests/team/scripts/build_report.py';s=p.read_text()
s=s.replace('Final project evidence report | 25 November 2026','Final project evidence report | 26 November 2026').replace("BookFlow | SQE evidence report | 25 Nov 2026","BookFlow | SQE evidence report | 26 Nov 2026")
s=s.replace("para('Local Sonar gate:","para('Analysis profile: Sonar way core. The observed zero issue counts apply to that profile and source scope; they do not contradict the independently detected functional/security defects.')\npara('Local Sonar gate:")
p.write_text(s,encoding='utf-8')
