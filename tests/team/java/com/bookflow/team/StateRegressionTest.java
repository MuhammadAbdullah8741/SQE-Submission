package com.bookflow.team;
import com.bookflow.model.*;
import com.bookflow.exception.BookFlowException;
import org.junit.jupiter.api.Test;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
class StateRegressionTest extends IssueReturnTest {
 @Test void lostTransactionMustNotReturn(){var t=transaction(0);t.setStatus(Transaction.TxnStatus.LOST);assertThrows(BookFlowException.class,()->service.returnBook(1L,"LIB"));verify(tx,never()).save(any());verify(books,never()).incrementStock(any());}
 @Test void duplicateIssueMustNotCreateSecondLoan(){var existing=transaction(0);when(tx.findByMemberSystemIdAndBookIsbnAndStatus(user.getSystemId(),book.getIsbn(),Transaction.TxnStatus.ISSUED)).thenReturn(Optional.of(existing));assertThrows(BookFlowException.class,()->service.issueBook(request(),"LIB"));verify(tx,never()).save(any());}
}
