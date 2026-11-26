from pathlib import Path
import re
r=Path(__file__).resolve().parents[3]
# JSTL formatDate accepts java.util.Date, not Java time objects. ISO text is unambiguous.
for p in (r/'src/main/webapp/WEB-INF/views').rglob('*.jsp'):
 s=p.read_text(encoding='utf-8');new=re.sub(r'<fmt:formatDate\s+value="(\$\{[^}]+\})"\s+pattern="[^"]+"\s*/>',r'<c:out value="\1"/>',s)
 if new!=s:p.write_text(new,encoding='utf-8')
p=r/'src/main/java/com/bookflow/controller/LibrarianController.java';s=p.read_text();s=s.replace('            return "librarian/dashboard";','            dashboard(principal, model);\n            return "librarian/dashboard";');p.write_text(s)
