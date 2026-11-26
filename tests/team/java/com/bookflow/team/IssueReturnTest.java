package com.bookflow.team;
import com.bookflow.dto.IssueBookRequest;
import com.bookflow.exception.BookFlowException;
import com.bookflow.model.*;
import com.bookflow.repository.*;
import com.bookflow.service.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.test.util.ReflectionTestUtils;
import java.time.LocalDate;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class IssueReturnTest {
 TransactionRepository tx; UserRepository users; FineRepository fines; BookService books; FineService fineService; AuditLogService audit; IssueReturnService service; User user; Book book;
 @BeforeEach void setup(){
  tx=mock(TransactionRepository.class);users=mock(UserRepository.class);fines=mock(FineRepository.class);books=mock(BookService.class);fineService=mock(FineService.class);audit=mock(AuditLogService.class);
  service=new IssueReturnService(tx,users,fines,books,fineService,audit);
  ReflectionTestUtils.setField(service,"borrowLimit",3);ReflectionTestUtils.setField(service,"borrowDurationDays",14);
  user=User.builder().systemId("TEST000001STU").status(User.UserStatus.ACTIVE).build();
  book=Book.builder().isbn("9780000000001").title("Synthetic Book").available(2).totalCopies(2).category(Book.BookCategory.TEXTBOOK).build();
  when(users.findById(user.getSystemId())).thenReturn(Optional.of(user));when(books.getByIsbn(book.getIsbn())).thenReturn(book);
 }
 IssueBookRequest request(){var r=new IssueBookRequest();r.setMemberId(user.getSystemId());r.setIsbn(book.getIsbn());return r;}
 @Test void issueWritesDatesAndStock(){var result=service.issueBook(request(),"LIB");assertSame(user,result.getMember());assertSame(book,result.getBook());assertEquals(LocalDate.now(),result.getIssueDate());assertEquals(LocalDate.now().plusDays(14),result.getDueDate());assertEquals(Transaction.TxnStatus.ISSUED,result.getStatus());assertEquals("LIB",result.getIssuedBy());verify(tx).save(result);verify(books).decrementStock(book.getIsbn());verify(audit).log(eq("LIB"),eq(AuditLog.AuditAction.BOOK_ISSUED),contains("due"));}
 @Test void precheckUsesFullEligibilityWithoutWriting(){assertSame(book,service.precheckIssue(user.getSystemId(),book.getIsbn()));verify(tx,never()).save(any());verify(books,never()).decrementStock(anyString());verifyNoInteractions(audit);}
 @Test void missingMember(){when(users.findById(anyString())).thenReturn(Optional.empty());assertEquals("Member not found: "+user.getSystemId(),assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB")).getMessage());verifyNoInteractions(tx,fines);}
 @Test void messagesIdentifyRecords(){user.setStatus(User.UserStatus.LOCKED);assertTrue(assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB")).getMessage().contains("LOCKED"));user.setStatus(User.UserStatus.ACTIVE);book.setAvailable(0);assertEquals("No copies available for: Synthetic Book",assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB")).getMessage());book.setAvailable(2);service.issueBook(request(),"LIB");verify(audit).log("LIB",AuditLog.AuditAction.BOOK_ISSUED,"Issued 'Synthetic Book' to TEST000001STU, due "+LocalDate.now().plusDays(14));transaction(1);service.returnBook(1L,"LIB");verify(audit).log("LIB",AuditLog.AuditAction.BOOK_RETURNED,"Returned 'Synthetic Book' from TEST000001STU (1 days overdue)");}
 @Test void missingBook(){when(books.getByIsbn(anyString())).thenThrow(new BookFlowException("missing"));assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB"));verify(tx,never()).save(any());}
 @ParameterizedTest @ValueSource(ints={2,3,4}) void borrowBoundary(int count){when(tx.countByMemberAndStatus(user,Transaction.TxnStatus.ISSUED)).thenReturn((long)count);if(count<3){assertNotNull(service.issueBook(request(),"LIB"));}else{assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB"));verify(tx,never()).save(any());}}
 @ParameterizedTest @ValueSource(ints={-1,0,1}) void stockBoundary(int available){book.setAvailable(available);if(available>0)assertNotNull(service.issueBook(request(),"LIB"));else {assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB"));verify(tx,never()).save(any());}}
 // Complete 2^4 MCC for the effective eligibility decision. Each row starts fresh.
 @TestFactory Collection<DynamicTest> eligibilityMcc(){var tests=new ArrayList<DynamicTest>();for(int bits=0;bits<16;bits++){final int b=bits;tests.add(DynamicTest.dynamicTest("MCC-"+b,()->{setup();boolean active=(b&8)!=0,stock=(b&4)!=0,under=(b&2)!=0,clear=(b&1)!=0;user.setStatus(active?User.UserStatus.ACTIVE:User.UserStatus.LOCKED);book.setAvailable(stock?1:0);when(tx.countByMemberAndStatus(user,Transaction.TxnStatus.ISSUED)).thenReturn(under?2L:3L);when(fines.existsByMemberAndPaidFalseAndWaivedFalse(user)).thenReturn(!clear);if(b==15)assertNotNull(service.issueBook(request(),"LIB"));else{assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB"));verify(tx,never()).save(any());verify(books,never()).decrementStock(anyString());}}));}return tests;}
 @ParameterizedTest @ValueSource(ints={0,1}) void auditMatchesFineState(int days){transaction(days);service.returnBook(1L,"LIB");verify(audit).log(eq("LIB"),eq(AuditLog.AuditAction.BOOK_RETURNED),contains(days>0?"(1 days overdue)":"(on time)"));}
 Transaction transaction(int overdue){var t=Transaction.builder().txnId(1L).member(user).book(book).status(Transaction.TxnStatus.ISSUED).dueDate(LocalDate.now().minusDays(overdue)).build();when(tx.findById(1L)).thenReturn(Optional.of(t));return t;}
 @ParameterizedTest @ValueSource(ints={-1,0,1,14}) void returnBoundary(int overdue){var t=transaction(overdue);assertSame(t,service.returnBook(1L,"LIB"));assertEquals(Transaction.TxnStatus.RETURNED,t.getStatus());assertEquals(LocalDate.now(),t.getReturnDate());assertEquals("LIB",t.getReturnedBy());verify(tx).save(t);verify(books).incrementStock(book.getIsbn());if(overdue>0)verify(fineService).createFineForTransaction(t,overdue);else verifyNoInteractions(fineService);verify(audit).log(eq("LIB"),eq(AuditLog.AuditAction.BOOK_RETURNED),contains("Returned"));}
 @Test void repeatReturnRejected(){var t=transaction(0);t.setStatus(Transaction.TxnStatus.RETURNED);assertThrows(BookFlowException.class,()->service.returnBook(1L,"LIB"));verify(tx,never()).save(any());verifyNoInteractions(fineService);}
 @Test void unknownTransactionRejected(){assertThrows(BookFlowException.class,()->service.returnBook(42L,"LIB"));}
 @ParameterizedTest @ValueSource(ints={-1,0,1}) void previewBoundary(int days){transaction(days);assertEquals(Math.max(0,days),service.previewOverdueDays(1L));verify(tx,never()).save(any());}
 @Test void previewMissing(){assertThrows(BookFlowException.class,()->service.previewOverdueDays(42L));}
 @Test void readDelegation(){var list=List.of(transaction(0));when(tx.findActiveByMember("S")).thenReturn(list);when(tx.findAllOverdue()).thenReturn(list);when(tx.findAllCurrentlyIssued()).thenReturn(list);when(tx.findAllByMemberId("S")).thenReturn(list);when(tx.countByIssueDate(LocalDate.now())).thenReturn(7L);assertSame(list,service.getActiveTransactionsForMember("S"));assertSame(list,service.getAllOverdue());assertSame(list,service.getAllCurrentlyIssued());assertSame(list,service.getHistoryForMember("S"));assertEquals(7,service.countIssuedToday());}
 @Test void lostTransactionMustNotReturn(){var t=transaction(0);t.setStatus(Transaction.TxnStatus.LOST);assertThrows(BookFlowException.class,()->service.returnBook(1L,"LIB"));verify(tx,never()).save(any());verify(books,never()).incrementStock(any());}
 @Test void duplicateIssueMustNotCreateSecondLoan(){var existing=transaction(0);when(tx.findByMemberSystemIdAndBookIsbnAndStatus(user.getSystemId(),book.getIsbn(),Transaction.TxnStatus.ISSUED)).thenReturn(Optional.of(existing));assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB"));verify(tx,never()).save(any());}

}
