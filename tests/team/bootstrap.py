from pathlib import Path
import re,json
r=Path(__file__).resolve().parents[2]
p=r/'pom.xml'
s=p.read_text()
s=s.replace('<finalName>bookflow</finalName>','<finalName>bookflow</finalName>\n<testSourceDirectory>tests/team/java</testSourceDirectory>')
s=s.replace('<plugins>','''<plugins>
<plugin><groupId>org.jacoco</groupId><artifactId>jacoco-maven-plugin</artifactId><version>0.8.12</version><executions><execution><goals><goal>prepare-agent</goal></goals></execution><execution><id>report</id><phase>test</phase><goals><goal>report</goal></goals></execution></executions></plugin>
<plugin><groupId>org.pitest</groupId><artifactId>pitest-maven</artifactId><version>1.17.3</version><configuration><targetClasses><param>com.bookflow.service.IssueReturnService</param><param>com.bookflow.service.FineService</param></targetClasses><targetTests><param>com.bookflow.team.*Test</param></targetTests><excludedTestClasses><param>*IntegrationTest</param></excludedTestClasses><threads>2</threads><outputFormats><param>XML</param><param>HTML</param></outputFormats><timestampedReports>false</timestampedReports></configuration><dependencies><dependency><groupId>org.pitest</groupId><artifactId>pitest-junit5-plugin</artifactId><version>1.2.1</version></dependency></dependencies></plugin>
''',1)
p.write_text(s)
for d in ['java/com/bookflow/team','evidence','browser','api','scripts','reports','performance','security']:(r/'tests/team'/d).mkdir(parents=True,exist_ok=True)
props=r/'src/main/resources/application.properties'
s=props.read_text()
s=re.sub(r'^spring.datasource.password=.*','spring.datasource.password=${DB_PASSWORD:SqeLocal2026}',s,flags=re.M)
s=re.sub(r'^spring.mail.password=.*','spring.mail.password=${SMTP_PASSWORD:}',s,flags=re.M)
s=re.sub(r'^spring.mail.username=.*','spring.mail.username=${SMTP_USERNAME:}',s,flags=re.M)
s=s.replace('bookflow.mail.simulate=false','bookflow.mail.simulate=true')
props.write_text(s)
(r/'package.json').write_text(json.dumps({'name':'bookflow-sqe-tests','private':True,'scripts':{'test':'playwright test'},'devDependencies':{'@playwright/test':'1.56.1','@axe-core/playwright':'4.11.0','lighthouse':'12.8.2','mysql2':'3.15.3'}},indent=2))
(r/'tests/team/evidence/baseline.json').write_text(json.dumps({'upstream':'https://github.com/Prash-Mayank/BookFlow','commit':'4312c97ba3767b7bb8ba19687a49368b49133390','branch':'develop','scope':['issue book','return book'],'licence':'MIT file present on upstream main, absent on develop; copy retained with provenance'},indent=2))
