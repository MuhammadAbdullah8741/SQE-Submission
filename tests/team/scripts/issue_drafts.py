from pathlib import Path
import json
r=Path(__file__).resolve().parents[3];dest=r/'tests/team/reports/issue-drafts';dest.mkdir(exist_ok=True)
steps={
'D01':'Seed an eligible student and an ISBN with at least two copies. Issue once, then repeat the same member/ISBN request. Expected: reject the second active loan. Baseline: two records accepted.',
'D02':'Seed an existing transaction as LOST and submit its ID to the return action. Expected: reject without stock change. Baseline: accepted and stock incremented.',
'D03':'Seed an issued transaction and open the librarian dashboard. Expected: render loan dates. Baseline: LocalDate-to-Date ELException and incomplete page.',
'D04':'Submit an issue for a locked member, then correct the member ID on the returned page. Expected: dashboard data remains available. Baseline catch path omitted model population.',
'D05':'Request issue/precheck with a known ISBN and an empty, unknown or ineligible member ID. Expected: eligibility error. Observed: stock availability returned without checking member.',
'D06':'Request return/preview with txnId=0 or an unknown positive ID. Expected: client-facing 400/404. Observed: unhandled exception and HTTP 500.',
'D07':'Run axe on the authenticated librarian dashboard and Lighthouse before the screen fixes. Observe invalid theme ARIA, contrast, heading and landmark findings. Rerun after repair.',
'D08':'Resolve the Maven dependency tree and run tests/team/scripts/audit.py. Review the exact package versions and OSV advisory IDs. Advisory matches do not establish exploitability.',
'D09':'Review baseline configuration and Git history without copying secret values into the issue. Working tree now uses environment placeholders; historical values require owner rotation/revocation.',
'D10':'Source review: public registration exposes all roles, and UserService.register persists the client-supplied role. Expected public signup role: STU. No external exploitation was performed.'}
for d in json.loads((r/'tests/team/reports/defects.json').read_text()):
 lines=[d['id']+': '+d['title'],'','LOCAL DRAFT - no GitHub issue has been created.','Severity: '+d['severity'],'Priority: '+d['priority'],'Status: '+d['status'],'Risk: '+d['risk'],'Category: '+d['category'],'','Reproduction / review:',steps[d['id']],'','Evidence:',d['evidence'],'','Root cause:',d['rootCause'],'','Correction:',d['fix'],'','Triage:',d['triage']]
 (dest/(d['id']+'.txt')).write_text('\n'.join(lines),encoding='utf-8')
print('Prepared',len(steps),'reviewable issue drafts')
