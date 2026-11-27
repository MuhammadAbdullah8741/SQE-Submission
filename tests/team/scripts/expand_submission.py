from pathlib import Path
import json
r=Path(__file__).resolve().parents[3]
p=r/'tests/team/scripts/build_report.py';s=p.read_text(encoding='utf-8')
s=s.replace('Supporting BookService/model paths and unrelated modules are not all covered;', 'Selected BookService stock operations and Book stock-state methods now have dedicated unit tests; unrelated CRUD/upload and other modules are not all covered;')
s=s.replace("['UC4 Overdue fine','One-day overdue return','Two days late; category default rate','Repeated overdue return; stale LOST loan']", "['UC4 Overdue fine','One-day overdue return','Two days late; category default rate','Repeated overdue return; stale LOST loan'],['UC5 Stock allocation','Issue from three copies','Last copy; two copies','Exhausted stock; unknown ISBN'],['UC6 Correct loan selection','Select first of two loans','Select second; retain returned history','Stale deleted loan; closed by another operator']")
s=s.replace('Four complete use cases support a two-person group at two per member. If the group has three members, two additional complete use cases are required. Ownership and group size were not supplied; this cannot be silently marked complete.', 'Six complete use cases now provide at least two per member for a group of up to three. Each has a main flow, two alternatives and two exceptions. Assign actual ownership after group details are supplied.')
s=s.replace("; additional use cases if three members", "")
p.write_text(s,encoding='utf-8')
p=r/'README-SQE.txt';s=p.read_text();s=s.replace('Four complete use cases support a pair; a three-person group requires two more complete use cases.', 'Six complete use cases support a group of up to three; assign two to each actual member.');p.write_text(s)
p=r/'tests/team/scripts/package_submission.py';s=p.read_text();s=s.replace("'extra use cases if three members',",'');p.write_text(s)
table=[
 {'id':'UC5','title':'Allocate available stock','preconditions':'Librarian session; active student; no fine; fixture stock set for case','main':'3 copies -> issue -> 2 copies and one ISSUED loan','alternatives':['1 copy -> issue -> 0 and book ISSUED','2 copies -> issue -> 1 and book AVAILABLE'],'exceptions':['0 copies -> explanatory rejection; no transaction','Unknown ISBN -> explanatory rejection; all stock unchanged'],'postconditions':'Exactly one copy consumed on success; no stock/loan change on rejection'},
 {'id':'UC6','title':'Return the correct loan record','preconditions':'Librarian session; synthetic issued loan options loaded','main':'Select first of two loans -> only first returned','alternatives':['Select second -> only second returned','Prior returned history plus active second -> preserve history and return second'],'exceptions':['Selected record deleted after form load -> reject, no stock credit','Selected record closed by another operator -> reject, no duplicate stock credit'],'postconditions':'Only selected eligible record changes; unrelated records preserved; no extra fine'}
]
(r/'tests/team/reports/additional-use-cases.json').write_text(json.dumps(table,indent=2))
