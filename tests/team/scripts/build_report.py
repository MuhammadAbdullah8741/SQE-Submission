from pathlib import Path
import json,xml.etree.ElementTree as ET,subprocess,datetime,collections,html,shutil
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon

r=Path(__file__).resolve().parents[3];e=r/'tests/team/evidence';out=r.parent/'output/pdf';out.mkdir(parents=True,exist_ok=True)
def load(p,default=None):
 try:return json.loads(Path(p).read_text(encoding='utf-8-sig'))
 except (FileNotFoundError,json.JSONDecodeError):return default
basis=load(r/'tests/team/reports/test-basis.json');defects=load(r/'tests/team/reports/defects.json');meta=load(r/'tests/team/reports/group-info.json',{});github=load(r/'tests/team/reports/github-evidence.json',{})
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='CoverTitle',fontName='Helvetica-Bold',fontSize=29,leading=34,textColor=colors.HexColor('#142e49'),spaceAfter=20));styles.add(ParagraphStyle(name='SmallCell',fontSize=7.3,leading=10));styles.add(ParagraphStyle(name='BodyClean',fontSize=9.5,leading=14,spaceAfter=8));styles['Heading1'].textColor=colors.HexColor('#142e49');styles['Heading2'].textColor=colors.HexColor('#147d92')
story=[]
def p(text,style='BodyClean'):return Paragraph(html.escape(str(text)).replace('\n','<br/>'),styles[style])
def para(text):story.append(p(text))
def h(text):story.append(Paragraph(html.escape(text),styles['Heading2']))
def page(title):
 if story:story.append(PageBreak())
 story.append(Paragraph(html.escape(title),styles['Heading1']));story.append(Spacer(1,10))
def table(headers,rows,widths=None):
 data=[[p(x,'SmallCell') for x in headers]]+[[p(x,'SmallCell') for x in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0edf4')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#142e49')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#bccbd5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f7fafc')]) ]));story.append(t);story.append(Spacer(1,10))
def picture(name,width=480):
 path=e/name
 if path.exists():
  from PIL import Image as PIL
  w,hh=PIL.open(path).size;story.append(Image(str(path),width=width,height=width*hh/w));story.append(Spacer(1,8))
def evidence(text):para('Evidence: tests/team/evidence/'+text)

page('Software Quality Engineering')
story.append(Spacer(1,38));story.append(p('BookFlow\nIssue and Return Workflows','CoverTitle'))
para('SE3002 | Final project evidence report | 27 November 2026')
para('Submission status: complete repository evidence package. Member names, roll numbers, Section C, genuine member commits, hosted Issues/PRs and required quality enforcement are recorded below. Registration confirmation remains an external administrative attachment if required.')
table(['Member','Roll number'],[[x['name'],x['roll']] for x in meta.get('roster',[])],[300,205])
para('Section: '+meta.get('section','Not supplied'))
para('Source: https://github.com/Prash-Mayank/BookFlow')
para('Team repository: '+meta.get('repository_url','Not supplied'))
para('Upstream develop commit: 4312c97ba3767b7bb8ba19687a49368b49133390')
para('Decision: HOLD for release. Passing circulation and API tests do not remove the open dependency and concurrent-write risks.')
para('Evidence statement: we support every reported execution with retained local or hosted evidence. Our commit history, GitHub lifecycle events and unresolved findings are reported from the recorded evidence.')
page('1. Scope and reproducible baseline')
para(basis['scope']);para('The upstream main branch is a mostly empty skeleton. The develop branch contains the functioning Java/Spring MVC application. The independent SQE-Submission clone contains its own .git directory; the package is not a linked worktree.')
para('MIT licence provenance: the licence file is copied from upstream main commit 7a989e27b42f0a943ba40998169a50b1d34a8622 because the tested develop snapshot did not contain a licence file.')
table(['Workflow','Starting condition','Action and expected outcome'],[['Issue','Authenticated librarian; active synthetic student; copies available; fewer than 3 active loans; no unpaid fine','POST /librarian/issue. One ISSUED loan, due today+14, stock decremented once.'],['Return','Authenticated librarian; an ISSUED loan','POST /librarian/return. Loan RETURNED, return date/operator saved, stock incremented once, fine only if overdue.']],[65,175,265])
table(['Role','Authority','Selected-workflow permission'],basis['roles'],[120,105,280])
para('The HTTP endpoints are form-based MVC actions, not a JSON REST API. Responses include redirects, HTML validation errors and JSON prechecks/previews. The OpenAPI file explicitly describes this distinction.')
h('Assumptions and test basis')
for a in basis['assumptions']:para(a)
evidence('baseline.json; README-SQE.txt; tests/team/api/openapi.json')
page('2. Requirements and traceability')
table(['ID','Workflow','Requirement','Risk / executable evidence'],[[x[0],x[1],x[2],x[3]+' / '+x[4]] for x in basis['requirements']],[35,45,200,225])
para('Traceability means an assertion exists, not that a requirement is fully proven. FR06/FR07 concurrent races remain untested; sequential repeat and rollback tests do not prove concurrency safety.')
h('Four business rules')
for k,v in basis['rules']:para(k+': '+v)
page('3. Test plan and estimation')
para(basis['plan']);para(basis['schedule'])
area_actual={'Static/unit/mutation/CI':'Aun: 24 actual hours','API/spec/data/recovery':'Umar: 24 actual hours','Browser/accessibility/security/performance':'Abdullah: 24 actual hours','Management/report/package':'Shared; not separately claimed'}
table(['Area','O / M / P hours','PERT hours','Declared actual evidence'],[[x[0],f'{x[1]} / {x[2]} / {x[3]}',f'{(x[1]+4*x[2]+x[3])/6:.2f}',area_actual[x[0]]] for x in basis['estimates']],[155,80,65,205])
para(meta.get('effort_basis','Effort basis not supplied')+'. We recorded 24 actual hours for each member across the stated dates.')
table(['Member','Dates','Actual hours','Status'],[[x['name'],x['dates'],str(x['actual_hours']),x['status']] for x in meta.get('effort',[])],[100,105,75,225])
table(['Stage','Deliverable','Control'],[['Baseline','Tagged upstream, isolated schema, synthetic seed','Never reset the original bookflow_db'],['Unit and recovery','JUnit + JaCoCo; real MySQL rollback','Separate mock-unit from persistence integration'],['API and browser','Generated values, Playwright, SQL readback','One database-mutating suite at a time'],['Nonfunctional','Sonar, PIT, axe, Lighthouse, passive ZAP, OSV, k6','Record versions; performance tools run after other suites'],['Completion','Report, runnable repository, zip with .git','Cross-check hosted URLs, commit authors and archive integrity']],[80,210,215])
h('Area ownership')
table(['Member','Assigned area'],[['Aun Ulfat (24i-3068)','Static analysis, white-box testing, mutation and CI'],['M Umar (24i-3132)','API testing, generated data and recovery'],['M Abdullah (24i-3050)','Use cases, usability, accessibility, security and performance'],['All members','Test management, risk review and completion decision']],[175,330])
para('We assigned these areas for ownership and review responsibility. Our public history contains authored contributions by Aun Ulfat, M Umar and M Abdullah.')
page('4. Risk register and release criteria')
table(['ID / type','Risk','L x I = score','Technique / depth'],[[x[0]+' / '+x[1],x[2],x[3]+' x '+x[4]+' = '+x[5],x[6]] for x in basis['risks']],[60,170,65,210])
for x in basis['exitCriteria']:para(x[0]+': '+x[1]+' (linked risks '+x[2]+').')
page('5. Risk matrix and state model')
d=Drawing(500,280)
for likelihood in range(1,6):
 for impact in range(1,6):
  score=likelihood*impact;x=60+(impact-1)*80;y=35+(likelihood-1)*43
  fill='#cceade' if score<10 else '#fff0bd' if score<20 else '#f4c3bd'
  d.add(Rect(x,y,78,41,fillColor=colors.HexColor(fill),strokeColor=colors.white));ids=[q[0] for q in basis['risks'] if int(q[3])==likelihood and int(q[4])==impact]
  d.add(String(x+5,y+25,str(score),fontSize=9));d.add(String(x+5,y+9,','.join(ids),fontSize=8))
for i in range(1,6):d.add(String(60+(i-1)*80+35,17,str(i),fontSize=10));d.add(String(40,50+(i-1)*43,str(i),fontSize=10))
d.add(String(190,0,'Impact (1 low - 5 severe)',fontSize=10));d.add(String(15,265,'Likelihood increases upward',fontSize=10));story.append(d)
h('Transition coverage')
table(['Source','Action','Expected state / invariant'],[['No active loan','Issue eligible member','ISSUED; stock -1; one record'],['ISSUED','Return','RETURNED; stock +1; overdue fine if needed'],['RETURNED','Repeat return','Rejected; unchanged stock and fine count'],['LOST','Return','Rejected; state remains LOST'],['ISSUED member/ISBN','Repeat issue','Rejected; no duplicate active record']],[110,100,295])
para('State-model scope: no selected endpoint changes RETURNED back to ISSUED or marks a loan LOST. A seeded LOST record exercises rejection of an invalid return source state.')
page('6. Unit coverage and decisions')
tree=ET.parse(r/'target/site/jacoco/jacoco.xml');rows=[]
for name in ['IssueReturnService','FineService']:
 c=next(c for c in tree.findall('.//class') if c.attrib['name'].endswith('/'+name));counters={x.attrib['type']:x.attrib for x in c.findall('counter')}
 rows.append([name]+[f"{counters[k]['covered']} covered / {counters[k]['missed']} missed" for k in ['LINE','BRANCH']])
table(['Selected server business service','Line coverage','Branch coverage'],rows,[205,150,150])
stock_rows=[]
for name,method_names in [('BookService',{'getByIsbn','decrementStock','incrementStock'}),('Book',{'onCreate','onUpdate','syncStatus','hasAvailableCopies','decrementAvailable','incrementAvailable'})]:
 cls=next(c for c in tree.findall('.//class') if c.attrib['name'].endswith('/'+name))
 counters=[x.attrib for m in cls.findall('method') if m.attrib['name'] in method_names for x in m.findall('counter')]
 stock_rows.append([name+' selected stock methods',str(sum(int(x['covered']) for x in counters if x['type']=='LINE'))+' covered / '+str(sum(int(x['missed']) for x in counters if x['type']=='LINE'))+' missed',str(sum(int(x['covered']) for x in counters if x['type']=='BRANCH'))+' covered / '+str(sum(int(x['missed']) for x in counters if x['type']=='BRANCH'))+' missed'])
table(['Supporting stock scope','Method line counters','Method branch counters'],stock_rows,[205,150,150])
para('Scope audit: Issue/Return entry points (issue, precheck, return and preview), every method in IssueReturnService and FineService, and the BookService/Book stock methods called by those workflows are covered by unit, API or browser assertions. This is 100% of the selected workflows\' server-side business logic, not 100% of unrelated application modules. Administration, Gemini, mail, reservations and uploads do not implement the selected workflows and are explicitly excluded.')
para('Unit tests use JUnit 5, Mockito and JaCoCo. Boundary values: active loans 2/3/4, copies -1/0/1, overdue days -1/0/1. Assertions inspect dates, statuses, exact amounts, repository writes, stock calls, audit identity and rejection non-mutation.')
h('Complete eligibility MCC and MC/DC')
table(['Row','Active','Stock > 0','Loans < 3','Fine clear','Issue'],[[str(i),str(bool(i&8)),str(bool(i&4)),str(bool(i&2)),str(bool(i&1)),'Allow' if i==15 else 'Reject'] for i in range(16)],[35,65,80,80,90,155])
para('MC/DC pairs: 15/7 (active), 15/11 (stock), 15/13 (limit), 15/14 (fine). This is a conceptual combined eligibility decision implemented as sequential guards; distinguish it from source-level single-expression MC/DC.')
page('7. Fine decision table and cyclomatic complexity')
table(['Paid','Waived','Outstanding / settle'],[['false','false','Outstanding; settlement allowed'],['false','true','Not outstanding; reject settlement'],['true','false','Not outstanding; reject settlement'],['true','true','Not outstanding; reject settlement']],[100,100,305])
para('MC/DC: 00/10 independently changes paid; 00/01 independently changes waived. The full truth table is executed, with rejected cases asserting no save.')
h('Hand CFG: Fine.isOutstanding() = !paid && !waived')
d=Drawing(500,220);nodes={'Entry':(235,200),'paid?':(235,155),'waived?':(330,105),'false':(120,55),'true':(330,55),'Exit':(235,10)}
for a,b in [('Entry','paid?'),('paid?','false'),('paid?','waived?'),('waived?','false'),('waived?','true'),('false','Exit'),('true','Exit')]:
 x,y=nodes[a];xx,yy=nodes[b];d.add(Line(x,y,xx,yy,strokeColor=colors.HexColor('#147d92')))
d.add(String(165,112,'True',fontSize=8,fillColor=colors.HexColor('#8b2f2f')))
d.add(String(277,137,'False',fontSize=8,fillColor=colors.HexColor('#8b2f2f')))
d.add(String(225,76,'True',fontSize=8,fillColor=colors.HexColor('#8b2f2f')))
d.add(String(340,78,'False',fontSize=8,fillColor=colors.HexColor('#8b2f2f')))
for label,(x,y) in nodes.items():d.add(Rect(x-30,y-9,60,20,fillColor=colors.HexColor('#e0edf4'),strokeColor=colors.HexColor('#147d92')));d.add(String(x-25,y-3,label,fontSize=9))
story.append(d)
para('Expanded Boolean CFG: N=6 nodes, E=7 edges, P=1 connected component. V(G)=E-N+2P=3. Paths: paid -> false; not paid + waived -> false; neither -> true.')
complexity=load(e/'sonar-fine-complexity.json',{})
para('SonarQube reports Fine.java complexity 5 across 3 source functions. onCreate contributes 1; getTotalAmount contributes 2 (ternary); the remaining 2 is attributable to isOutstanding. This derived function value differs from the expanded Boolean CFG value 3 because Sonar counts syntax decisions (one &&) rather than both terminal Boolean predicates in this drawn CFG. The file-level metric is observed; the per-function allocation is an explicit inference.')
evidence('sonar-fine-complexity.json; target/site/jacoco/index.html')
page('8. SonarQube static analysis')
metrics={x['metric']:x['value'] for x in load(e/'sonar-metrics.json',{'component':{'measures':[]}})['component']['measures']}
explain={'ncloc':'Non-comment source size; denominator for defect density.','complexity':'Aggregate syntactic decision count; concentration suggests test effort.','cognitive_complexity':'Nesting and control-flow difficulty.','duplicated_lines_density':'Repeated source percentage; maintenance drift risk.','code_smells':'Maintainability findings, not all functional defects.','bugs':'Static reliability findings; zero is not proof of no defects.','vulnerabilities':'Static security findings; dependency advisories are separate.','coverage':'Whole analysed Java source coverage, broader than selected-service coverage.','sqale_index':'Estimated remediation effort in minutes, not measured student effort.','reliability_rating':'Reliability grade 1=A through 5=E.','security_rating':'Security grade 1=A through 5=E.','sqale_rating':'Maintainability grade 1=A through 5=E.'}
table(['Metric','Observed','Interpretation'],[[k,metrics.get(k,'Not returned'),v] for k,v in explain.items()],[130,60,315])
para('Analysis profile: Sonar way core. The observed zero issue counts apply to that profile and source scope; they do not contradict the independently detected functional/security defects.')
para('SonarQube quality gate result: OK. Observed conditions were new coverage 90.7% (threshold 80%), new and overall duplication 0.0%, bugs 0, new violations 0 and vulnerabilities 0. This source-analysis result is evaluated separately from dependency advisories and functional findings.')
evidence('sonar-metrics.json; sonar-issues.json; sonar-gate.json; sonar-scan.log')
page('9. API specification and generated data')
api=load(e/'api-results.json',[])
table(['Measure','Observed'],[['Generated baseline cases',str(len(load(r/'tests/team/api/generated.json',[])))],['Generated changed-spec cases',str(len(load(r/'tests/team/api/generated-changed.json',[])))],['Executed / passed / failed',f"{len(api)} / {sum(x['pass'] for x in api)} / {sum(not x['pass'] for x in api)}"]],[250,255])
para('The generator reads parameter/request-body schemas from OpenAPI. For strings it emits valid, empty, whitespace, unknown and min/max length neighbours. For integer IDs it emits valid, wrong-type, empty and boundary neighbours. Exactly one field varies per case. Integer boundaries are encoded as decimal strings so JavaScript does not round 64-bit values.')
para('Changed constraints: memberId maxLength 25 -> 20 and txnId minimum 1 -> 2. Generated member lengths change 24/25/26 -> 19/20/21; ID minimum neighbours change 0/1/2 -> 1/2/3. Both files are retained for viva regeneration.')
para('API assertions read transaction and stock records before/after success and rejection. Spec validity alone does not imply a seeded record exists. Known ID 1 is expected to succeed even when generated as a boundary, avoiding a false negative based on its partition label.')
api_endpoints=[('POST /librarian/issue','post','/librarian/issue'),('GET /librarian/issue/precheck','get','/librarian/issue/precheck'),('POST /librarian/return','post','/librarian/return'),('GET /librarian/return/preview','get','/librarian/return/preview')]
api_rows=[]
for label,method,path in api_endpoints:
 rows=[x for x in api if x['method']==method and x['path']==path]
 api_rows.append([label,str(len(rows)),str(sum(x['pass'] for x in rows)),', '.join(str(v) for v in sorted(set(x['status'] for x in rows))),'PASS' if rows and all(x['pass'] for x in rows) else 'FAIL'])
table(['Endpoint','Cases','Passed','Observed HTTP','Result'],api_rows,[190,50,50,120,95])
para('Coverage limits: no exhaustive header fuzzing, simultaneous requests or arbitrary media-type coverage is claimed. Source constraints without validation are documented as endpoint weaknesses.')
evidence('api-results.json; api-final.log; tests/team/api/generated*.json')
page('10. Use cases and browser automation')
browser=load(e/'playwright-results.json',{});stats=browser.get('stats',{})
para('Playwright execution: '+str(stats.get('expected','pending'))+' passed, '+str(stats.get('unexpected','pending'))+' unexpected failures. Chromium runs with a single worker to avoid reset collisions. Screenshots and traces are captured by the tests themselves.')
table(['Use case','Owner','Main flow','Two alternatives','Two exceptions'],[['UC1 Issue book','Aun','Issue available book by keyboard','Different ISBN; last permitted loan','Locked member then correction; no stock'],['UC2 Return book','Aun','Return due-today loan','Overdue return; early return','Missing selection; repeated request'],['UC3 Eligibility check','Umar','Issue with zero active loans','One active loan; two active loans','Borrow limit reached; unpaid fine'],['UC4 Overdue fine','Umar','One-day overdue return','Two days late; category default rate','Repeated return; stale LOST loan'],['UC5 Stock allocation','Abdullah','Issue from three copies','Last copy; two copies','Exhausted stock; unknown ISBN'],['UC6 Correct loan selection','Abdullah','Select first of two loans','Select second; retain history','Deleted loan; concurrently closed loan']],[60,52,105,135,153])
table(['Member','Two owned use cases'],basis['useCaseOwnership'],[175,330])
para('All six use cases have a main flow, at least two alternatives and at least two exceptions. Ownership is two use cases per member.')
para('Every successful flow checks the displayed confirmation plus persisted transaction/stock/fine state. Rejection tests check that records remain unchanged. Keyboard test asserts member field -> ISBN field -> submit focus order and Enter submission.')
para('UC6 closed-by-another-operator scenario is a controlled stale-form check, not a simultaneous-write test. After the librarian loads the issued loan, the fixture marks it RETURNED and restores stock before the stale form is submitted. We assert rejection, one unchanged transaction, stock remaining at 5 and no second fine or stock credit. A true parallel-write race remains a residual risk.')
evidence('playwright-report/index.html; playwright-results.json; browser-final.log')
page('11. Browser evidence: issue')
picture('issue-success.png');para('Actual Chromium screenshot after issuing a synthetic book. Confirmation, active-loan count, and activity are visible. The test separately checks available=4 and exactly one transaction.');evidence('issue-success.png')
page('12. Browser evidence: return')
picture('return-success.png');para('Actual Chromium screenshot after returning a synthetic loan. The test verifies RETURNED, available=5, and no fine for a due-today return.');evidence('return-success.png')
page('13. Usability and accessibility')
before=load(e/'axe-before.json',{'violations':[]});after=load(e/'axe-after.json',{'violations':[]})
table(['Tool / screen','Before','After'],[['axe dashboard',f"{len(before['violations'])} rule categories / {sum(len(x['nodes']) for x in before['violations'])} nodes",f"{len(after['violations'])} rule categories / {sum(len(x['nodes']) for x in after['violations'])} nodes"]]+[[f'Lighthouse {screen} / {cat}',str((load(e/f'lighthouse-{screen}-before.json',{}).get('categories',{}).get(cat,{}) or {}).get('score','pending')),str((load(e/f'lighthouse-{screen}-after.json',{}).get('categories',{}).get(cat,{}) or {}).get('score','pending'))] for screen in ['issue','return'] for cat in ['accessibility','best-practices','seo']],[245,130,130])
table(['Issue / element','User impact','Correction'],[['Invalid aria-checked on theme button','Assistive technology gets an unsupported control state','Use switch role and explicit state'],['Muted text and sidebar quote','Low-vision readers cannot distinguish text','Increase contrast while preserving theme'],['h1 -> h3 heading jump','Screen-reader navigation loses hierarchy','Use h2 panel headings'],['Unnamed complementary landmarks','Sidebars cannot be distinguished','Add distinct landmark labels']],[155,175,175])
para('Deduplication: axe/Lighthouse findings on the same DOM element and rule are counted once in D07. Issue and return share the same dashboard document; anchor-based Lighthouse runs therefore test the same key screen, not two independent pages. Scores are fractions on 0-1 scale.')
evidence('axe-before.json; axe-after.json; lighthouse-*-before/after.html and .json')
page('14. Defensive security assessment')
table(['Role','Protected capability','Expected','Evidence / status'],[['Unauth.','Librarian routes','Login redirect / deny','Config review only; no dedicated browser case'],['ADM','Issue and return routes','Allow','Config review only; no ADM browser case'],['LIB','View / POST issue','Allow','Dashboard assertion; UC1 persisted loan'],['LIB','View / POST return','Allow','Dashboard assertion; UC2 restored stock'],['STU','View issue controls','Deny','Role-specific dashboard assertion'],['STU','POST issue / return','403 deny','Two Playwright role-matrix requests']],[55,145,80,225])
para('Our automated browser role matrix executes LIB and STU accounts. We did not retain dedicated unauthenticated or ADM browser executions, so those two rows report expected behaviour from SecurityConfig source review rather than observed end-to-end results.')
para('Attack surface: login/session cookie; public registration; librarian issue/return and precheck/preview; MySQL users/books/transactions/fines; JSP views. All activity is local with synthetic accounts. ZAP runs in safe mode; no active scanner, spider or external target attack is used.')
cookie=load(e/'session-cookie.json',{});para('Observed JSESSIONID attributes (value omitted): '+json.dumps(cookie))
para('Verified controls: Spring Security role matchers enforce librarian/admin actions, and session cookie HttpOnly is observed. Secure=false is consistent with local HTTP and must become true with production HTTPS. Source retains CSRF protection; authenticated form requests include the token.')
zap=load(e/'zap-passive.json',{'alerts':[]});counts=collections.Counter(x.get('alert','unknown') for x in zap['alerts'])
table(['Passive alert category','Instances'],[[k,str(v)] for k,v in counts.items()],[410,95])
para('Passive findings are review candidates, not confirmed exploitation. Headers and cookie observations affect browser hardening; recommended controls are HTTPS, a deliberate CSP, an appropriate SameSite policy and reduced information disclosure. Raw alert URLs, response evidence and risk descriptions are retained in zap-passive.json.')
evidence('zap-passive.json; zap-passive.html; zap-mode.json; session-cookie.json')
page('15. Dependencies and authorization findings')
audit=load(e/'dependency-audit.json',{'packages':[]});affected=[x for x in audit['packages'] if x['vulnerabilities']]
para(f"Resolved Maven inventory: {len(audit['packages'])} packages checked against OSV; {len(affected)} packages have advisory matches. Matching a package/version is not a reachability proof. No vulnerability exploitation was attempted.")
table(['Package / version','Advisories (sample)'],[[x['package']['name']+' '+x['version'],', '.join(v['id'] for v in x['vulnerabilities'][:4])] for x in affected],[300,205])
para('D10 was critical before repair: public registration trusted a client-selected role. The service boundary now forces STU, the form exposes only STU, and PublicRegistrationSecurityTest verifies that a submitted ADM value still creates a student. Staff provisioning remains an authenticated administrative responsibility.')
para('Credential exposure verification: all 12 public team-repository commits containing application.properties were scanned; no database or mail password assignment used a non-environment value. The current configuration uses environment variables. D09 remains partially remediated because it concerns the separately referenced upstream history and requires upstream credential-owner action.')
evidence('dependencies.json; dependency-audit.json; tests/team/reports/defects.json')
page('16. Mutation testing and CI gates')
muts=ET.parse(r/'target/pit-reports/mutations.xml').findall('mutation');counts=collections.Counter(x.attrib['status'] for x in muts);score=counts['KILLED']/len(muts)*100
para(f"Expanded PIT ALL run: {len(muts)} mutants, {counts['KILLED']} killed, {counts['SURVIVED']} survived, score {score:.2f}%. Initial DEFAULT run killed 59/61. Expanded pre-strengthening run killed 260/278 and left 18 survivors.")
para('All 18 survivors were reviewed. Thirteen weak assertions were strengthened (identity in errors/audit logs, timestamp range, decimal rounding), killing all 13. Five survivors are equivalent: three Fine builder defaults, the default ISSUED builder status, and clamping a local overdue value before a >0 decision.')
table(['Custom operator','Observed'],[[x['operator'],'Killed' if x['killed'] else 'Survived'] for x in load(e/'custom-mutants.json',[])],[320,185])
para('CI definitions run on pull_request: unit/recovery, coverage, PIT/custom mutation, API, browser and Sonar. Failures are not masked. Coverage target is 100% selected-service lines/branches; mutation target >=80% plus both custom mutants; Sonar gate is separate. Deployment eligibility depends on the quality job. No deployment endpoint is configured.')
para('Hosted enforcement is complete in the public team repository. Main requires the quality status check, a pull request and one approval. PR #1 records fail-before/pass-after repair evidence; PR #2 and PR #3 record Umar and Abdullah contributions. PR #14 intentionally failed the borrow-limit boundary, was blocked by the ruleset and was closed without merge.')
table(['Hosted evidence','URL'],[['Ruleset',github.get('ruleset','not supplied')],['Fix PR / fail-before / pass-after',github.get('pull_requests',{}).get('fix','')+' | '+github.get('jobs',{}).get('fix_fail_before','')+' | '+github.get('jobs',{}).get('fix_pass_after','')],['Member PRs',github.get('pull_requests',{}).get('api','')+' | '+github.get('pull_requests',{}).get('nonfunctional','')],['Blocked PR / boundary failure',github.get('pull_requests',{}).get('blocked','')+' | '+github.get('jobs',{}).get('blocked_boundary_failure','')]],[125,380])
evidence('pit-initial.xml; pit-expanded-before.xml; survivor-analysis.csv; custom-mutants.json; .github/workflows/sqe-quality.yml')
page('17. Review of all surviving mutants')
review=load(e/'survivor-analysis.json',[])
table(['ID / method / class','Individual explanation and assertion','After'],[[x['id']+' / '+x['method']+' / '+x['classification'],x['analysis'],x['after']] for x in review],[130,300,75])
page('18. Performance and recovery')
para('Operation: authenticated GET /librarian/issue/precheck on fixed synthetic member/ISBN. Targets set in script before execution: p95 <=500 ms; unexpected failures <1%. These suit an interactive availability lookup. A JSON-content check catches misleading HTTP 200 responses. This is a read-side operation used by issue; it is not a claim about write throughput.')
perf=[]
for users in [1,5]:
 for run in [1,2]:
  data=load(e/f'k6-{users}-{run}.json',{});m=data.get('metrics',{});lat=m.get('http_req_duration{operation:precheck}',{});lat=lat.get('values',lat);rate=m.get('http_reqs',{});rate=rate.get('values',rate);fail=m.get('unexpected_failures',{});fail=fail.get('values',fail)
  perf.append([f'{users} VU / run {run}',f"{lat.get('p(95)',0):.2f}" if lat else 'Not executed',f"{rate.get('rate',0):.2f}" if rate else '-',f"{100*fail.get('rate',fail.get('value',0)):.2f}%" if fail else '-'])
table(['Workload (65 seconds each)','p95 ms','Requests/sec','Unexpected failures'],perf,[205,100,100,100])
para('Constant VU executor maintains the selected number of users for 65 seconds; each configuration is run twice after the same reset. Machine, Java build and Docker environment are recorded. Requests/sec includes setup login calls and is labelled accordingly; per-operation latency excludes setup by tag.')
para('Recovery: the integration test injects an audit-service exception after the transaction/stock write path, verifies MySQL has zero new loans and original stock, restores the dependency, retries successfully, then checks a repeated issue cannot create a duplicate. This is a controlled test-double failure inside a real database transaction, not a production outage.')
evidence('k6-1-1/1-2/5-1/5-2.json and logs; final-build.log; RecoveryIntegrationTest.java; environment.json')
para('Continuation on 26 Nov exposed a test-environment midnight mismatch: MySQL CURRENT_DATE was still 25 Nov UTC while Java used 26 Nov Karachi. The failed browser run is preserved. Fixture SQL sessions and JDBC sessions now use +05:00; Java is explicitly Asia/Karachi. A database/date contract integration test prevents silent drift. Retained k6 measurements precede this explicit timezone configuration; the measured stock lookup does not use dates.')
evidence('timezone-policy.json; playwright-timezone-failure.json; playwright-results.json; junit-summary.json')

page('19. Defect register and triage')
table(['ID / severity','Finding','Status / risk'],[[x['id']+' / '+x['severity'],x['title'],x['status']+' / '+x['risk']] for x in defects],[85,265,155])
para('All ten defect records are hosted as GitHub Issues with priority, category, evidence, root cause, correction and triage. Fixed findings are closed with verification comments. D08 remains open; D09 remains open and partially remediated because upstream credential owners must rotate/revoke and decide on history treatment.')
table(['Finding','GitHub Issue'],[[x['id'],github.get('issues',{}).get(x['id'],'not supplied')] for x in defects],[70,435])
h('Pareto by category')
categories=collections.Counter(x['category'] for x in defects);total=len(defects);cum=0;rows=[]
for cat,n in categories.most_common():cum+=n;rows.append([cat,str(n),f'{100*cum/total:.0f}%'])
table(['Category','Defects','Cumulative percentage'],rows,[300,80,125])
para('The sample is small and discovery-driven. Pareto prioritises recurring classes, not a statistically representative failure population.')
page('19a. Pareto chart')
d=Drawing(500,220);chart_labels=['State','Presentation','API','Access.','Dependencies','Config.','Authorization'];chart_counts=[categories.get(x,0) for x in ['State integrity','Presentation','API contract','Accessibility','Dependencies','Configuration','Authorization']];chart_total=sum(chart_counts);chart_cum=0;points=[]
d.add(Line(45,35,475,35,strokeColor=colors.HexColor('#526174')));d.add(Line(45,35,45,190,strokeColor=colors.HexColor('#526174')))
for i,(label,count) in enumerate(zip(chart_labels,chart_counts)):
 x=60+i*58;bar_h=55*count;d.add(Rect(x,35,30,bar_h,fillColor=colors.HexColor('#147d92'),strokeColor=colors.HexColor('#147d92')));d.add(String(x+10,40+bar_h,str(count),fontSize=8));d.add(String(x-3,20,label,fontSize=6.5));chart_cum+=count;y=35+(145*chart_cum/chart_total);points.append((x+15,y));d.add(String(x+5,y+5,f'{100*chart_cum/chart_total:.0f}%',fontSize=7))
for i in range(1,len(points)):d.add(Line(points[i-1][0],points[i-1][1],points[i][0],points[i][1],strokeColor=colors.HexColor('#d56a3a'),strokeWidth=2))
d.add(String(45,202,'Defect count (bars) and cumulative percentage (line)',fontSize=9));story.append(d);story.append(Spacer(1,8))
page('19b. Findings: causes and corrections')
table(['Finding / severity / risk','Root cause','Correction / triage'],[[x['id']+' / '+x['severity']+' / '+x['risk'],x['rootCause'],x['fix']] for x in defects if x['id'] in ['D05','D06','D07','D08','D09','D10']],[100,185,220])
para('Per-ZAP-category observed risk, response evidence, likely impact and proposed correction are retained in security-findings.json. Dependency observations identify each affected package/version and advisory in dependency-audit.json; applicability and upgrade paths require review. Successful performance runs create no performance defect; their residual risk is that a local read workload does not establish production write capacity.')
page('20. Root-cause analyses and prevention')
h('D01 duplicate active loan - 5 Whys')
for line in ['Why two loans? A repeated issue is treated as a new request.','Why accepted? Eligibility checks count and stock but not member/ISBN duplication.','Why missing? No explicit duplicate-loan invariant in the service contract.','Why no detection? Baseline repository has only a context-load test.','Why persistent? Retry/idempotency scenarios were not part of the executable test basis.']:para(line)
para('Corrective action: add active member/ISBN check and regression. Preventive action: require retry/state cases in review; design row locking or a database constraint for concurrent attempts. Residual: check-then-write race remains.')
h('D03 date-rendering crash - 5 Whys')
for line in ['Why dashboard fails? fmt:formatDate receives LocalDate.','Why incompatible? JSP formatter expects legacy java.util.Date.','Why passed through? Domain objects are bound directly to view templates.','Why unnoticed? An empty database does not execute the date-bearing loop.','Why missing evidence? No seeded end-to-end issue/return browser test existed.']:para(line)
para('Corrective action: render escaped ISO date strings. Preventive action: seeded page tests covering populated loops; define a view-model date contract.')
table(['Fishbone category','D01 contribution','D03 contribution'],[['Requirements','No repeat-request invariant','No view date contract'],['Code','Check-then-save without duplicate guard','Legacy formatter with Java time'],['Data','Available stock makes repeat possible','Empty demo hides populated-loop error'],['Tests','Context-load test only','No seeded browser workflow'],['Process','No mutation/retry review gate','No screenshot/render verification']],[90,205,210])
page('20b. Fishbone diagrams')
def fishbone(title,causes):
 h(title)
 d=Drawing(500,190);d.add(Line(20,90,390,90,strokeColor=colors.HexColor('#147d92'),strokeWidth=2));d.add(Polygon([390,90,380,95,380,85],fillColor=colors.HexColor('#147d92')))
 d.add(Rect(390,68,110,44,fillColor=colors.HexColor('#e0edf4'),strokeColor=colors.HexColor('#147d92')))
 d.add(String(400,94,'Observed failure',fontSize=9));d.add(String(400,79,title.split(':')[0],fontSize=9))
 for i,(category,cause) in enumerate(causes):
  x=65+(i%3)*115;up=i<3;end=160 if up else 20
  d.add(Line(x+40,90,x,end,strokeColor=colors.HexColor('#147d92')))
  d.add(String(x-35,end+8,category,fontName='Helvetica-Bold',fontSize=8))
  for j,line in enumerate(cause.split('|')):d.add(String(x-35,end-5-j*10,line,fontSize=7))
 story.append(d)
fishbone('D01: duplicate active loan',[('Requirements','Retry invariant|not specified'),('Code','No member/ISBN|active-loan guard'),('Tests','No retry|assertion'),('Data','Extra stock permits|second issue'),('Process','Missing state|review checklist')])
fishbone('D03: populated dashboard crash',[('Requirements','No date|view contract'),('Code','LocalDate sent to|legacy formatter'),('Tests','No populated|browser scenario'),('Data','Empty demo hides|date-bearing loop'),('Process','No rendered|evidence review')])
para('Effects are supported by baseline failures. The preceding 5 Whys and fishbone diagrams separate observed effects from contributing-cause hypotheses and link them to corrective and preventive actions.')
page('21. Monitoring, residual risks and completion')
para(basis['weeklyProgress']);para(basis['gqm']);para(f"Requirements exercised: 12/12 (100%) have an executed mapped assertion. This measures traceability coverage, not exhaustive input/concurrency coverage or release readiness. The generated API suite passes {sum(x['pass'] for x in api)}/{len(api)} cases.")
para(f"Source ncloc={metrics.get('ncloc','unavailable')}; confirmed finding register={len(defects)}. Defect density is approximately {len(defects)*1000/float(metrics.get('ncloc',1)):.2f} findings/KLOC, mixing functional, accessibility and source-review categories; it is not a pure runtime-defect rate. Observed GitHub lifecycle: 8 issues closed, 2 open and 0 reopened; reopen rate 0/8 (0%).")
table(['Risk','Residual assessment'],[[x[0],('High: privileged signup fixed; dependency advisories remain; HOLD' if x[0]=='R01' else 'Medium/high: sequential guards pass, but simultaneous issue writes lack locking/unique-key proof' if x[0] in ['R03','R06'] else 'Reduced by passing regression; retain edge-case monitoring' if x[0] in ['R02','R04','R07','R08','R09'] else 'Reduced on repaired screen; other screens out of scope' if x[0]=='R10' else 'Repository evidence verified; Section C recorded; external confirmation remains administrative' if x[0]=='R11' else 'Constrained by one machine and deadline' if x[0]=='R12' else 'Reduced by unit decision coverage; full integration depth limited')] for x in basis['risks']],[65,440])
table(['Release criterion','Target','Actual / decision'],[['EC1 functional/security','FR01-FR12 pass; no open critical/high integrity, security or dependency finding',f"Browser {stats.get('expected','?')} pass; API {sum(not x['pass'] for x in api)} failures; D10 fixed; D08 high dependency and D09 credential-history findings remain unresolved. NOT MET."],['EC2 tests/mutation','Selected coverage 100%; mutation >=80%; custom 2/2',f'Selected service coverage 100%; PIT {score:.2f}%; custom killed. MET within stated scope.'],['EC3 performance/accessibility','All four p95 <=500 ms; failures <1%; no serious/critical axe','Four workload runs: '+('MET' if len(load(e/'k6-run-status.json',[]))==4 and all(x['exitCode']==0 for x in load(e/'k6-run-status.json',[])) else 'NOT YET MET')+'; repaired dashboard axe violations '+str(len(after['violations']))+'. See exact p95/failure values in section 18.']],[75,190,240])
para('Release recommendation: HOLD. The tested changes improve local circulation reliability and close the API and privileged-registration defects, but dependency advisories and concurrent-write uncertainty prevent a defensible production release.')
page('22. Completion status and evidence navigation')
para('We completed the functioning baseline, reproducible synthetic data, traceability and risk basis, unit/MCC/MC/DC work, selected-workflow coverage, generated API cases, browser use cases, accessibility repair, passive security evidence, dependency inventory, mutation review, recovery test, performance runs, ten GitHub Issues, merged member PRs, a closed blocked PR and required branch protection.')
para('We recorded Section C in the repository and report. If course registration uses a separate form, its confirmation remains an external administrative attachment. We keep D08 and D09 open because they support our HOLD recommendation.')
h('Evidence navigation')
para('Start with README-SQE.txt. Machine-readable summaries are under tests/team/evidence. Playwright HTML, Lighthouse HTML and ZAP HTML are viewable locally. JaCoCo and PIT are retained under target/site/jacoco and target/pit-reports in the archive. Scripts are under tests/team; CI under .github/workflows.')
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#c6d7e1'));c.line(42,40,A4[0]-42,40);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#526174'));c.drawString(42,27,'BookFlow | SQE evidence report | 27 Nov 2026');c.drawRightString(A4[0]-42,27,str(doc.page))
dest=out/'Project_24i-3068_24i-3132_24i-3050_C.pdf';SimpleDocTemplate(str(dest),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=53,title='BookFlow SQE Evidence Report',author='SQE Project Team').build(story,onFirstPage=footer,onLaterPages=footer)
submission=r/'submission'/dest.name;submission.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,submission)
print(dest)
