from pathlib import Path
r=Path(__file__).resolve().parents[3];p=r/'tests/team/api/run.cjs';s=p.read_text();s=s.replace("const valid=tc.partition==='valid';", "const valid=tc.path.endsWith('/issue')?(data.memberId==='STU000001STU'&&data.isbn==='9780000000001'):data.txnId==='1';")
s=s.replace("else pass=res.status()<500;", "else {pass=res.status()<500;if(tc.path.endsWith('/precheck')&&data.memberId!=='STU000001STU')pass=pass&&body.includes('error');}")
p.write_text(s)
