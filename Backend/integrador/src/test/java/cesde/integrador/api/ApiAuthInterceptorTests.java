package cesde.integrador.api;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.ResultSetExtractor;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

@DisplayName("ApiAuthInterceptor: protección de rutas con token bearer")
class ApiAuthInterceptorTests {
    private AuthTokenService tokens;
    private JdbcTemplate jdbc;
    private ApiAuthInterceptor interceptor;
    private MockHttpServletRequest request;

    @BeforeEach
    void setUp() {
        tokens = mock(AuthTokenService.class);
        jdbc = mock(JdbcTemplate.class);
        interceptor = new ApiAuthInterceptor(tokens, jdbc);
        request = new MockHttpServletRequest();
    }

    @Test
    @DisplayName("Sin encabezado Authorization responde 401")
    void missingHeaderIsUnauthorized() {
        ApiException error = assertThrows(ApiException.class, this::preHandle);

        assertEquals(HttpStatus.UNAUTHORIZED, error.getStatusCode());
        assertEquals("Se requiere iniciar sesión", error.getReason());
        verifyNoInteractions(tokens, jdbc);
    }

    @Test
    @DisplayName("Un encabezado que no es Bearer responde 401")
    void nonBearerHeaderIsUnauthorized() {
        request.addHeader(HttpHeaders.AUTHORIZATION, "Basic dXN1YXJpbzpjbGF2ZQ==");

        ApiException error = assertThrows(ApiException.class, this::preHandle);

        assertEquals(HttpStatus.UNAUTHORIZED, error.getStatusCode());
        verifyNoInteractions(tokens, jdbc);
    }

    @Test
    @DisplayName("Un token inválido o vencido responde 401")
    void invalidTokenIsUnauthorized() {
        request.addHeader(HttpHeaders.AUTHORIZATION, "Bearer token-invalido");
        when(tokens.verify("token-invalido")).thenReturn(null);

        ApiException error = assertThrows(ApiException.class, this::preHandle);

        assertEquals("La sesión expiró o no es válida", error.getReason());
        verifyNoInteractions(jdbc);
    }

    @Test
    @DisplayName("Una cuenta inactiva responde 401")
    void inactiveAccountIsUnauthorized() {
        UUID userId = givenValidToken();
        givenAccountActive(userId, false);

        ApiException error = assertThrows(ApiException.class, this::preHandle);

        assertEquals("La cuenta ya no está activa", error.getReason());
    }

    @Test
    @DisplayName("Un token válido de una cuenta activa permite continuar y guarda el usuario")
    void validTokenOfActiveAccountPasses() {
        UUID userId = givenValidToken();
        givenAccountActive(userId, true);

        assertTrue(preHandle());
        assertEquals(userId, request.getAttribute(ApiAuthInterceptor.USER_ID_ATTRIBUTE));
    }

    private boolean preHandle() {
        return interceptor.preHandle(request, new MockHttpServletResponse(), new Object());
    }

    private UUID givenValidToken() {
        UUID userId = UUID.randomUUID();
        request.addHeader(HttpHeaders.AUTHORIZATION, "Bearer token-valido");
        when(tokens.verify("token-valido")).thenReturn(userId);
        return userId;
    }

    @SuppressWarnings("unchecked")
    private void givenAccountActive(UUID userId, boolean active) {
        when(jdbc.query(anyString(), any(ResultSetExtractor.class), eq(userId))).thenReturn(active);
    }
}
