package com.bookflow.team;

import com.bookflow.controller.AuthController;
import com.bookflow.controller.LibrarianController;
import com.bookflow.exception.BookFlowException;
import com.bookflow.model.Book;
import com.bookflow.model.User;
import com.bookflow.service.*;
import org.junit.jupiter.api.Test;
import org.springframework.ui.ExtendedModelMap;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class ControllerContractTest {
    private IssueReturnService issues = mock(IssueReturnService.class);
    private LibrarianController librarian = new LibrarianController(
        issues, mock(BookService.class), mock(FineService.class), mock(ReservationService.class));

    @Test
    void issuePrecheckUsesFullServiceEligibility() {
        Book book = Book.builder().isbn("9780000000001").title("Test Book").available(2).build();
        when(issues.precheckIssue("STU000001STU", book.getIsbn())).thenReturn(book);

        var body = librarian.precheckIssue("STU000001STU", book.getIsbn());

        assertEquals(true, body.get("available"));
        assertEquals("Test Book", body.get("bookTitle"));
        assertEquals(2, body.get("copiesLeft"));
    }

    @Test
    void issuePrecheckReturnsStructuredBusinessError() {
        when(issues.precheckIssue("UNKNOWN", "9780000000001"))
            .thenThrow(new BookFlowException("Member not found: UNKNOWN"));

        assertEquals("Member not found: UNKNOWN",
            librarian.precheckIssue("UNKNOWN", "9780000000001").get("error"));
    }

    @Test
    void returnPreviewMapsBoundarySuccessAndMissingRecord() {
        assertEquals(400, librarian.previewReturn(0L).getStatusCode().value());
        when(issues.previewOverdueDays(1L)).thenReturn(3L);
        assertEquals(3L, librarian.previewReturn(1L).getBody().get("overdueDays"));
        when(issues.previewOverdueDays(99L)).thenThrow(new BookFlowException("Transaction not found: 99"));
        assertEquals(404, librarian.previewReturn(99L).getStatusCode().value());
        assertEquals("Transaction not found: 99", librarian.previewReturn(99L).getBody().get("error"));
    }

    @Test
    void publicRegistrationPageExposesOnlyStudentRole() {
        AuthController controller = new AuthController(mock(UserService.class), mock(PasswordResetService.class));
        ExtendedModelMap model = new ExtendedModelMap();

        assertEquals("auth/register", controller.registerPage(model));
        assertEquals(List.of(User.Role.STU), model.get("roles"));
    }
}
