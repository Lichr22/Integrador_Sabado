package cesde.integrador.api;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import jakarta.servlet.http.HttpServletRequest;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final JdbcTemplate jdbc;
    private final PasswordService passwords;
    private final AuthTokenService tokens;

    public AuthController(JdbcTemplate jdbc, PasswordService passwords, AuthTokenService tokens) {
        this.jdbc = jdbc;
        this.passwords = passwords;
        this.tokens = tokens;
    }

    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody Registration request) {
        String name = request.nombre() == null ? "" : request.nombre().trim();
        String email = normalizeEmail(request.correo());
        String password = request.contrasena() == null ? "" : request.contrasena();
        if (name.length() < 3) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "El nombre debe tener al menos 3 caracteres");
        }
        if (!email.matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "Ingresa un correo electrónico válido");
        }
        if (password.length() < 8) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "La contraseña debe tener al menos 8 caracteres");
        }
        if (emailExists(email)) {
            throw new ApiException(HttpStatus.CONFLICT, "Este correo ya está registrado");
        }

        UUID id = UUID.randomUUID();
        jdbc.update("""
                INSERT INTO public.usuarios (id, nombre, correo, contrasena_hash, activo, rol, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, id, name, email, passwords.hash(password), true, "Participante", LocalDateTime.now());
        Map<String, Object> user = findUser(id);
        return Map.of("token", tokens.issue(id), "user", user);
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody Login request) {
        String email = normalizeEmail(request.correo());
        String password = request.contrasena() == null ? "" : request.contrasena();
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT id, contrasena_hash, activo
                FROM public.usuarios
                WHERE lower(correo) = ?
                """, email);
        if (rows.isEmpty()) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "Correo o contraseña incorrectos");
        }
        Map<String, Object> credentials = rows.get(0);
        Object encoded = credentials.get("contrasena_hash");
        if (!(encoded instanceof String hash) || !passwords.matches(password, hash)) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "Correo o contraseña incorrectos");
        }
        if (!Boolean.TRUE.equals(credentials.get("activo"))) {
            throw new ApiException(HttpStatus.FORBIDDEN, "La cuenta está inactiva");
        }
        UUID id = (UUID) credentials.get("id");
        return Map.of("token", tokens.issue(id), "user", findUser(id));
    }

    @GetMapping("/me")
    public Map<String, Object> me(HttpServletRequest request) {
        UUID id = (UUID) request.getAttribute(ApiAuthInterceptor.USER_ID_ATTRIBUTE);
        return findUser(id);
    }

    private Map<String, Object> findUser(UUID id) {
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT id, nombre, correo, activo, rol, fecha_registro
                FROM public.usuarios
                WHERE id = ?
                """, id);
        if (rows.isEmpty()) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "La cuenta ya no existe");
        }
        return rows.get(0);
    }

    private boolean emailExists(String email) {
        Integer count = jdbc.queryForObject(
                "SELECT count(*) FROM public.usuarios WHERE lower(correo) = ?", Integer.class, email);
        return count != null && count > 0;
    }

    private static String normalizeEmail(String email) {
        return email == null ? "" : email.trim().toLowerCase(java.util.Locale.ROOT);
    }

    public record Login(String correo, String contrasena) {}
    public record Registration(String nombre, String correo, String contrasena) {}
}
