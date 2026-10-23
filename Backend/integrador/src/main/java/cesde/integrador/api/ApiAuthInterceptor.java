package cesde.integrador.api;

import java.util.UUID;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class ApiAuthInterceptor implements HandlerInterceptor {
    public static final String USER_ID_ATTRIBUTE = "authenticatedUserId";
    private final AuthTokenService tokens;
    private final JdbcTemplate jdbc;

    public ApiAuthInterceptor(AuthTokenService tokens, JdbcTemplate jdbc) {
        this.tokens = tokens;
        this.jdbc = jdbc;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String authorization = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new ApiException(org.springframework.http.HttpStatus.UNAUTHORIZED, "Se requiere iniciar sesión");
        }
        UUID userId = tokens.verify(authorization.substring(7).trim());
        if (userId == null) {
            throw new ApiException(org.springframework.http.HttpStatus.UNAUTHORIZED, "La sesión expiró o no es válida");
        }
        Boolean active = jdbc.query(
                "SELECT activo FROM public.usuarios WHERE id = ?",
                resultSet -> resultSet.next() && resultSet.getBoolean("activo"),
                userId);
        if (!Boolean.TRUE.equals(active)) {
            throw new ApiException(org.springframework.http.HttpStatus.UNAUTHORIZED, "La cuenta ya no está activa");
        }
        request.setAttribute(USER_ID_ATTRIBUTE, userId);
        return true;
    }
}
