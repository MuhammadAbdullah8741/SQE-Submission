import xml.etree.ElementTree as E,json,csv
from pathlib import Path
r=Path(__file__).resolve().parents[3];e=r/'tests/team/evidence'
before=E.parse(e/'pit-expanded-before.xml').findall('mutation');after=E.parse(r/'target/pit-reports/mutations.xml').findall('mutation')
def key(m):return tuple(m.findtext(k) for k in ['mutatedClass','mutatedMethod','lineNumber','mutator','description'])
lookup={key(m):m.attrib['status'] for m in after};rows=[]
for i,m in enumerate([m for m in before if m.attrib['status']=='SURVIVED'],1):
 d=m.findtext('description');status=lookup.get(key(m),'not matched')
 if 'FineBuilder' in d:reason='Equivalent: Lombok builder defaults already set zero processing charge / false paid / false waived.'
 elif 'TransactionBuilder::status' in d:reason='Equivalent: Transaction builder default is already ISSUED.'
 elif 'Math::max' in d:reason='Equivalent: negative and zero overdue both bypass fine and use on-time audit text; local overdue variable is not returned.'
 elif 'setScale' in d:reason='Weak assertion: add fractional category rate 2.345 and assert rounded 7.04 for 3 days.'
 elif 'currentTimeMillis' in d:reason='Weak assertion: assert receipt timestamp falls between test start and end.'
 else:reason='Weak assertion: assert exact record identity/status in errors and audit messages instead of only a generic substring.'
 rows.append({'id':'M%02d'%i,'class':m.findtext('mutatedClass'),'method':m.findtext('mutatedMethod'),'line':m.findtext('lineNumber'),'operator':d,'classification':'equivalent' if reason.startswith('Equivalent') else 'weak assertion','analysis':reason,'after':status})
(e/'survivor-analysis.json').write_text(json.dumps(rows,indent=2))
with (e/'survivor-analysis.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print(len(rows),'survivors analysed;',sum(x['after']=='KILLED' for x in rows),'killed after strengthening')
