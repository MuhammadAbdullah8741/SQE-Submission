package com.bookflow.team;

import com.bookflow.dto.RegistrationRequest;
import com.bookflow.model.AuditLog;
import com.bookflow.model.User;
import com.bookflow.repository.UserRepository;
import com.bookflow.service.AuditLogService;
import com.bookflow.service.UserService;
import com.bookflow.util.SystemIdGenerator;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class PublicRegistrationSecurityTest {
    @Test
    void publicRequestCannotSelfAssignAdministratorRole() {
        UserRepository users = mock(UserRepository.class);
        SystemIdGenerator ids = mock(SystemIdGenerator.class);
        AuditLogService audit = mock(AuditLogService.class);
        UserService service = new UserService(users, ids, audit);
        when(ids.generate("Aun", User.Role.STU)).thenReturn("AUN000001STU");
        when(users.save(any(User.class))).thenAnswer(call -> call.getArgument(0));

        RegistrationRequest request = new RegistrationRequest();
        request.setFirstName("Aun");
        request.setLastName("Alfat");
        request.setEmail("student@example.test");
        request.setPhone("9876543210");
        request.setPassword("student1");
        request.setConfirmPassword("student1");
        request.setRole(User.Role.ADM);
        request.setAgreedToTerms(true);

        User created = service.register(request);

        assertEquals(User.Role.STU, created.getRole());
        assertEquals("AUN000001STU", created.getSystemId());
        verify(ids).generate("Aun", User.Role.STU);
        verify(audit).log("AUN000001STU", AuditLog.AuditAction.MEMBER_CREATED,
            "New Student account registered: AUN000001STU");
    }
}
