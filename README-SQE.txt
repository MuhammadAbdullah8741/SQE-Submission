BOOKFLOW SQE SUBMISSION - START HERE

Working source: src/main/java and src/main/webapp.
Team-authored/AI-assisted tests: tests/team (upstream tests are not counted).
Upstream: https://github.com/Prash-Mayank/BookFlow
Team repository: https://github.com/MuhammadAbdullah8741/SQE-Submission
Baseline: 4312c97ba3767b7bb8ba19687a49368b49133390 (develop), tag sqe-upstream-baseline.
Licence: MIT copied from upstream main, commit 7a989e27b42f0a943ba40998169a50b1d34a8622.
Automation authorship: SQE automation (Codex); do not claim these commits as individual student work.

REQUIREMENTS
Java 17+ (tested Java 21), Maven 3.9+, Node 22+, Python 3.12+, Docker Desktop.
On the current machine Maven is ../.tools/apache-maven-3.9.9/bin/mvn.cmd.
Use mvn in the commands below if Maven is on PATH.

FIRST-TIME DATABASE SETUP (dedicated synthetic data only)
docker run -d --name sqe-mysql -p 127.0.0.1:3308:3306 -e MYSQL_ROOT_PASSWORD=SqeLocal2026 -e MYSQL_DATABASE=bookflow_test mysql:8.0
Wait for MySQL to accept connections.
docker cp src/main/resources/schema.sql sqe-mysql:/tmp/schema.sql
docker exec sqe-mysql sh -c 'sed s/bookflow_db/bookflow_test/g /tmp/schema.sql | MYSQL_PWD=$MYSQL_ROOT_PASSWORD mysql -uroot'
The seed script refuses any database other than bookflow_test. Never point it at real data.

INSTALL TEST TOOLS
npm ci
npx playwright install chromium
python -m pip install bcrypt requests reportlab pymupdf

BUILD AND START
docker start sqe-mysql
node tests/team/scripts/seed.cjs
mvn -B -ntp package
powershell -ExecutionPolicy Bypass -File tests/team/scripts/start.ps1
Open http://localhost:8081/bookflow/auth/login
Synthetic accounts: LIB000001LIB, STU000001STU, ADM000001ADM. Password: SqeTest123!
LOCK000001STU is intentionally locked. These credentials are local synthetic fixtures.
Email is simulated. No Gemini key is required for the selected workflows.
Stop the Java process with Ctrl+C before rebuilding the WAR on Windows.

RESET BETWEEN SUITES
node tests/team/scripts/seed.cjs
This deletes only the synthetic test database records. Run database-mutating suites sequentially.

TEST COMMANDS
mvn -B -ntp test
  Runs unit tests and real-MySQL RecoveryIntegrationTest. Database must be available.
python tests/team/scripts/gate.py coverage
mvn -B -ntp org.pitest:pitest-maven:mutationCoverage -Dmutators=ALL
python tests/team/scripts/custom_mutations.py
  Restores original source in finally. Recompile afterwards to restore compiled classes.
mvn -B -ntp test
python tests/team/scripts/gate.py mutation
python tests/team/api/generate.py
node tests/team/api/run.cjs
  Expected result: 52/52 generated API cases pass.
npx playwright test
node tests/team/scripts/lighthouse.mjs after
python tests/team/scripts/performance.py
  Requires Docker k6 image, running app and no concurrent login/reset tests. Four 65-second runs.

SONARQUBE
docker run -d --name sqe-sonar -p 127.0.0.1:9000:9000 -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community
python tests/team/scripts/sonar.py
python tests/team/scripts/gate.py sonar
Local isolated server uses its default bootstrap admin login. Script creates a token without printing it.
The observed profile was Sonar way core. Zero findings are not proof of absent defects.

PASSIVE ZAP
docker run -d --name sqe-zap -p 127.0.0.1:8090:8090 ghcr.io/zaproxy/zaproxy:stable zap.sh -daemon -host 0.0.0.0 -port 8090 -config api.disablekey=true -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true
Set ZAP mode to safe using http://localhost:8090/JSON/core/action/setMode/?mode=safe
PowerShell environment for browser tests:
  $env:BASE_URL='http://host.docker.internal:8081/bookflow'
  $env:ZAP_PROXY='http://127.0.0.1:8090'
  $env:A11Y_PHASE='after'
  npx playwright test
  python tests/team/scripts/zap_export.py
Clear BASE_URL/ZAP_PROXY afterwards if running without ZAP. No active scan is used.

DEPENDENCY AUDIT
mvn -B -ntp org.apache.maven.plugins:maven-dependency-plugin:3.7.1:tree "-DoutputType=json" "-DoutputFile=tests/team/evidence/dependencies.json"
python tests/team/scripts/audit.py
Uses the public OSV advisory database against exact resolved Maven versions. Reachability is not asserted.

REPORT AND EVIDENCE
python tests/team/scripts/analyse_mutants.py
python tests/team/scripts/build_report.py
Report output: ../output/pdf/Project_24i-3068_24i-3132_24i-3050_C.pdf
Browser HTML: tests/team/evidence/playwright-report/index.html
Coverage HTML: target/site/jacoco/index.html
Mutation HTML: target/pit-reports/index.html
Raw execution logs and machine-readable reports: tests/team/evidence.
One-time assembly/repair scripts (bootstrap.py, repair.py, fix_*.py, refine_tests.py) preserve provenance;
do not rerun them as normal setup. The checked-in sources already contain their changes.

OUTSTANDING EXTERNAL SUBMISSION REQUIREMENTS
Members: Aun Ulfat (24i-3068), M Umar (24i-3132), M Abdullah (24i-3050).
Confirm section registration. Set up a team-owned public GitHub repository.
Publish reviewed local issue drafts and two genuine PRs: failed regression before fix and passing fix.
Configure SQE quality gate / quality as a REQUIRED branch status check. YAML alone cannot prevent merging.
Each member must contribute and commit their own work; review AI-use disclosure and rehearse the viva.
Six complete use cases are assigned two per member: UC1-UC2 Aun, UC3-UC4 Umar, UC5-UC6 Abdullah.
Whole-project business-logic coverage is not 100%; selected IssueReturnService/FineService are 100%.

SECURITY / RELEASE STATUS
HOLD: dependency advisories and concurrent issue-write integrity still require production remediation.
Working configuration has no upstream plaintext secrets, but upstream .git history retains them.
Owners must revoke/rotate and review history before public publishing. Do not publish the archive blindly.
No external GitHub changes or course submission has been performed.

TIMEZONE REPRODUCIBILITY
The start script pins Java to Asia/Karachi and JDBC connectionTimeZone=+05:00 with
forceConnectionTimeZoneToSession=true. The SQL fixture connections also set time_zone=+05:00.
This prevents UTC/local midnight drift in CURRENT_DATE test fixtures.
Connector/J documentation: https://dev.mysql.com/doc/connector-j/en/connector-j-time-instants.html
