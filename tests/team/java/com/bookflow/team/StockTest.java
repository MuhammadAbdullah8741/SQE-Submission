package com.bookflow.team;
import com.bookflow.model.Book;
import com.bookflow.repository.BookRepository;
import com.bookflow.service.BookService;
import com.bookflow.service.AuditLogService;
import com.bookflow.exception.BookFlowException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.test.util.ReflectionTestUtils;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class StockTest {
 @ParameterizedTest @ValueSource(ints={-1,0,1}) void availabilityBoundary(int count){Book b=Book.builder().available(count).build();assertEquals(count>0,b.hasAvailableCopies());}
 @ParameterizedTest @ValueSource(ints={0,1,2}) void decrementPreservesStockInvariant(int count){Book b=Book.builder().isbn("9780000000001").available(count).build();if(count==0){assertThrows(IllegalStateException.class,b::decrementAvailable);assertEquals(0,b.getAvailable());}else{b.decrementAvailable();assertEquals(count-1,b.getAvailable());assertEquals(count==1?Book.BookStatus.ISSUED:Book.BookStatus.AVAILABLE,b.getStatus());}}
 @Test void reservedZeroStockStaysReserved(){Book b=Book.builder().available(1).status(Book.BookStatus.RESERVED).build();b.decrementAvailable();assertEquals(0,b.getAvailable());assertEquals(Book.BookStatus.RESERVED,b.getStatus());}
 @Test void incrementReleasesUnavailableState(){Book b=Book.builder().available(0).status(Book.BookStatus.ISSUED).build();b.incrementAvailable();assertEquals(1,b.getAvailable());assertEquals(Book.BookStatus.AVAILABLE,b.getStatus());}
 @Test void persistenceCallbacksSynchronizeState(){Book b=Book.builder().available(0).build();ReflectionTestUtils.invokeMethod(b,"onCreate");assertNotNull(b.getAddedAt());assertNotNull(b.getUpdatedAt());assertEquals(Book.BookStatus.ISSUED,b.getStatus());b.setAvailable(2);ReflectionTestUtils.invokeMethod(b,"onUpdate");assertEquals(Book.BookStatus.AVAILABLE,b.getStatus());}
 @Test void serviceStockRoundTripPersistsSameBook(){BookRepository repo=mock(BookRepository.class);Book b=Book.builder().isbn("9780000000001").available(1).build();when(repo.findById(b.getIsbn())).thenReturn(Optional.of(b));BookService service=new BookService(repo,mock(AuditLogService.class));service.decrementStock(b.getIsbn());assertEquals(0,b.getAvailable());assertEquals(Book.BookStatus.ISSUED,b.getStatus());service.incrementStock(b.getIsbn());assertEquals(1,b.getAvailable());assertEquals(Book.BookStatus.AVAILABLE,b.getStatus());verify(repo,times(2)).save(b);}
 @Test void missingStockRecordDoesNotWrite(){BookRepository repo=mock(BookRepository.class);BookService service=new BookService(repo,mock(AuditLogService.class));assertThrows(BookFlowException.class,()->service.decrementStock("missing"));assertThrows(BookFlowException.class,()->service.incrementStock("missing"));verify(repo,never()).save(any());}
 @Test void exhaustedStockDoesNotSave(){BookRepository repo=mock(BookRepository.class);Book b=Book.builder().isbn("9780000000001").available(0).build();when(repo.findById(b.getIsbn())).thenReturn(Optional.of(b));BookService service=new BookService(repo,mock(AuditLogService.class));assertThrows(IllegalStateException.class,()->service.decrementStock(b.getIsbn()));verify(repo,never()).save(any());}
}
