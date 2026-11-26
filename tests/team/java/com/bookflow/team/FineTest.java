package com.bookflow.team;
import com.bookflow.model.*;
import com.bookflow.repository.*;
import com.bookflow.service.*;
import com.bookflow.util.PdfReceiptGenerator;
import com.bookflow.exception.BookFlowException;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.test.util.ReflectionTestUtils;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
class FineTest {
 FineRepository repo;ConfigRepository configs;AuditLogService audit;PdfReceiptGenerator pdf;FineService service;Fine fine;User user;
 @BeforeEach void setup(){repo=mock(FineRepository.class);configs=mock(ConfigRepository.class);audit=mock(AuditLogService.class);pdf=mock(PdfReceiptGenerator.class);service=new FineService(repo,configs,audit,pdf);ReflectionTestUtils.setField(service,"defaultDailyRateStr","5.00");ReflectionTestUtils.setField(service,"processingChargeStr","20.00");user=User.builder().systemId("TEST000001STU").build();fine=Fine.builder().fineId(1L).member(user).amount(new BigDecimal("10.00")).build();when(repo.findById(1L)).thenReturn(Optional.of(fine));when(repo.save(any())).thenAnswer(a->a.getArgument(0));}
 @Test void fallbackRate(){assertEquals(new BigDecimal("5.00"),service.getDailyRateForCategory(Book.BookCategory.NOVEL));}
 @Test void roundingAndReceiptIdentity(){when(configs.findById("fine.rate.textbook")).thenReturn(Optional.of(Config.builder().configValue("2.345").build()));var t=Transaction.builder().member(user).book(Book.builder().category(Book.BookCategory.TEXTBOOK).build()).build();assertEquals(new BigDecimal("7.04"),service.createFineForTransaction(t,3).getAmount());long before=System.currentTimeMillis();service.payFine(1L,"CASH","LIB");long suffix=Long.parseLong(fine.getReceiptNumber().substring(fine.getReceiptNumber().lastIndexOf('-')+1));assertTrue(suffix>=before&&suffix<=System.currentTimeMillis());verify(audit).log(eq("LIB"),eq(AuditLog.AuditAction.FINE_PAID),contains("TEST000001STU"));}
 @Test void waiverAuditIdentity(){service.waiveFine(1L,"Correction","ADM");verify(audit).log(eq("ADM"),eq(AuditLog.AuditAction.FINE_WAIVED),contains("TEST000001STU"));}
 @Test void configuredDefault(){when(configs.findById("fine.rate.default")).thenReturn(Optional.of(Config.builder().configValue("7.00").build()));assertEquals(new BigDecimal("7.00"),service.getDailyRateForCategory(Book.BookCategory.NOVEL));}
 @Test void categoryRate(){when(configs.findById("fine.rate.novel")).thenReturn(Optional.of(Config.builder().configValue("2.00").build()));assertEquals(new BigDecimal("2.00"),service.getDailyRateForCategory(Book.BookCategory.NOVEL));}
 @Test void fineAmountAndState(){var t=Transaction.builder().member(user).book(Book.builder().category(Book.BookCategory.TEXTBOOK).build()).build();Fine f=service.createFineForTransaction(t,3);assertEquals(new BigDecimal("15.00"),f.getAmount());assertSame(t,f.getTransaction());assertSame(user,f.getMember());assertEquals(3,f.getOverdueDays());assertEquals(new BigDecimal("5.00"),f.getDailyRate());assertEquals(BigDecimal.ZERO,f.getProcessingCharge());assertFalse(f.isPaid());assertFalse(f.isWaived());verify(repo).save(f);}
 @Test void payment(){assertSame(fine,service.payFine(1L,"CASH","LIB"));assertTrue(fine.isPaid());assertEquals(new BigDecimal("20.00"),fine.getProcessingCharge());assertEquals(new BigDecimal("30.00"),fine.getTotalAmount());assertEquals(LocalDate.now(),fine.getPaymentDate());assertEquals("CASH",fine.getPaymentMode());assertTrue(fine.getReceiptNumber().startsWith("RCPT-TEST000001STU-"));verify(repo).save(fine);verify(audit).log(eq("LIB"),eq(AuditLog.AuditAction.FINE_PAID),contains("30.00"));}
 @Test void waive(){assertSame(fine,service.waiveFine(1L,"Correction","ADM"));assertTrue(fine.isWaived());assertEquals("Correction",fine.getWaiverReason());assertEquals("ADM",fine.getWaivedBy());verify(repo).save(fine);verify(audit).log(eq("ADM"),eq(AuditLog.AuditAction.FINE_WAIVED),contains("Correction"));}
 @TestFactory Collection<DynamicTest> settlementMcc(){var all=new ArrayList<DynamicTest>();for(int b=0;b<4;b++){final int bits=b;all.add(DynamicTest.dynamicTest("paid-waived-MCC-"+b,()->{setup();fine.setPaid((bits&2)!=0);fine.setWaived((bits&1)!=0);assertEquals(bits==0,fine.isOutstanding());if(bits==0)assertNotNull(service.payFine(1L,"CASH","LIB"));else{assertThrows(BookFlowException.class,()->service.payFine(1L,"CASH","LIB"));assertThrows(BookFlowException.class,()->service.waiveFine(1L,"Reason","ADM"));verify(repo,never()).save(any());}}));}return all;}
 @Test void nullReason(){assertThrows(BookFlowException.class,()->service.waiveFine(1L,null,"ADM"));}
 @ParameterizedTest @ValueSource(strings={""," "}) void blankReason(String reason){assertThrows(BookFlowException.class,()->service.waiveFine(1L,reason,"ADM"));}
 @Test void missingFine(){assertThrows(BookFlowException.class,()->service.payFine(9L,"CASH","LIB"));assertThrows(BookFlowException.class,()->service.waiveFine(9L,"Reason","ADM"));assertThrows(BookFlowException.class,()->service.generateReceiptPdf(9L));}
 @Test void unpaidReceipt(){assertThrows(BookFlowException.class,()->service.generateReceiptPdf(1L));}
 @Test void paidReceipt(){fine.setPaid(true);byte[] bytes={1,2,3};when(pdf.generateFineReceipt(fine)).thenReturn(bytes);assertSame(bytes,service.generateReceiptPdf(1L));}
 @Test void nullProcessingCharge(){fine.setProcessingCharge(null);assertEquals(fine.getAmount(),fine.getTotalAmount());}
 @Test void queries(){var list=List.of(fine);when(repo.findByMemberAndPaidFalseAndWaivedFalse(user)).thenReturn(list);when(repo.findByMemberOrderByCreatedAtDesc(user)).thenReturn(list);when(repo.getTotalOutstandingByMember(user)).thenReturn(BigDecimal.TEN);when(repo.getTotalCollected()).thenReturn(BigDecimal.ONE);when(repo.findByTransactionTxnId(1L)).thenReturn(Optional.of(fine));assertSame(list,service.getOutstandingForMember(user));assertSame(list,service.getHistoryForMember(user));assertEquals(BigDecimal.TEN,service.getTotalOutstanding(user));assertEquals(BigDecimal.ONE,service.getTotalCollected());assertEquals(Optional.of(fine),service.findByTransaction(1L));}
}
