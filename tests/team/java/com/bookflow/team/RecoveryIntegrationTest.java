package com.bookflow.team;
import com.bookflow.dto.IssueBookRequest;
import com.bookflow.service.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.jdbc.core.JdbcTemplate;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
@SpringBootTest(properties={"spring.datasource.url=jdbc:mysql://localhost:3308/bookflow_test?useSSL=false&connectionTimeZone=%2B05:00&forceConnectionTimeZoneToSession=true&allowPublicKeyRetrieval=true","spring.datasource.username=root","spring.datasource.password=SqeLocal2026","bookflow.mail.simulate=true"})
class RecoveryIntegrationTest {
 @Autowired IssueReturnService service; @Autowired JdbcTemplate jdbc; @MockBean AuditLogService audit;
 @Test void databaseAndBusinessDatesAgree(){assertEquals("+05:00",jdbc.queryForObject("SELECT @@session.time_zone",String.class));assertEquals(java.time.LocalDate.now().toString(),jdbc.queryForObject("SELECT CAST(CURRENT_DATE AS CHAR)",String.class));}
 @Test void failureRollsBackThenRetryWritesExactlyOnce(){
  String member="RECOVERY000001STU",isbn="9780000000099";
  jdbc.update("DELETE FROM transactions WHERE member_id=?",member);
  jdbc.update("INSERT INTO users(system_id,first_name,last_name,password_hash,role,email,status,failed_login_attempts) VALUES (?, 'Recovery','Test','unused','STU','recovery@example.test','ACTIVE',0) ON DUPLICATE KEY UPDATE status='ACTIVE'",member);
  jdbc.update("INSERT INTO books(isbn,title,author,category,total_copies,available,status) VALUES (?,'Recovery book','Test','TEXTBOOK',1,1,'AVAILABLE') ON DUPLICATE KEY UPDATE available=1",isbn);
  IssueBookRequest request=new IssueBookRequest();request.setMemberId(member);request.setIsbn(isbn);
  doThrow(new IllegalStateException("Controlled audit dependency outage")).when(audit).log(anyString(),any(),anyString());
  assertThrows(IllegalStateException.class,()->service.issueBook(request,"LIB000001LIB"));
  assertEquals(0,jdbc.queryForObject("SELECT COUNT(*) FROM transactions WHERE member_id=?",Integer.class,member));
  assertEquals(1,jdbc.queryForObject("SELECT available FROM books WHERE isbn=?",Integer.class,isbn));
  reset(audit);service.issueBook(request,"LIB000001LIB");
  assertEquals(1,jdbc.queryForObject("SELECT COUNT(*) FROM transactions WHERE member_id=?",Integer.class,member));
  assertEquals(0,jdbc.queryForObject("SELECT available FROM books WHERE isbn=?",Integer.class,isbn));
  assertThrows(RuntimeException.class,()->service.issueBook(request,"LIB000001LIB"));
  assertEquals(1,jdbc.queryForObject("SELECT COUNT(*) FROM transactions WHERE member_id=?",Integer.class,member));
 }
}
