package cesde.integrador.api;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@DisplayName("AuthTokenService: emisión y validación de tokens")
class AuthTokenServiceTests {
    private static final String SECRET = "secreto-de-pruebas-con-mas-de-32-bytes";
    private final AuthTokenService tokens = new AuthTokenService(SECRET);

    @Test
    @DisplayName("Rechaza secretos de menos de 32 bytes")
    void rejectsShortSecret() {
        assertThrows(IllegalStateException.class, () -> new AuthTokenService("corto"));
    }

    @Test
    @DisplayName("Un token emitido se valida y devuelve el mismo usuario")
    void issuedTokenVerifiesToSameUser() {
        UUID userId = UUID.randomUUID();

        String token = tokens.issue(userId);

        assertNotNull(token);
        assertEquals(userId, tokens.verify(token));
    }

    @Test
    @DisplayName("Un token firmado con otro secreto no es válido")
    void tokenFromAnotherSecretIsRejected() {
        AuthTokenService other = new AuthTokenService("otro-secreto-distinto-con-mas-de-32-bytes");

        assertNull(tokens.verify(other.issue(UUID.randomUUID())));
    }

    @Test
    @DisplayName("Un token con el contenido alterado no es válido")
    void tamperedPayloadIsRejected() {
        String signature = tokens.issue(UUID.randomUUID()).split("\\.")[1];
        String forgedPayload = encode(UUID.randomUUID() + ":" + (now() + 3600));

        assertNull(tokens.verify(forgedPayload + "." + signature));
    }

    @Test
    @DisplayName("Un token vencido no es válido")
    void expiredTokenIsRejected() throws Exception {
        String payload = encode(UUID.randomUUID() + ":" + (now() - 1));

        assertNull(tokens.verify(payload + "." + sign(payload)));
    }

    @Test
    @DisplayName("Un token bien firmado pero con datos incompletos no es válido")
    void signedTokenWithInvalidClaimsIsRejected() throws Exception {
        String payload = encode("sin-fecha-de-vencimiento");

        assertNull(tokens.verify(payload + "." + sign(payload)));
    }

    @ParameterizedTest(name = "Rechaza el token \"{0}\"")
    @DisplayName("Rechaza tokens con formato inválido")
    @ValueSource(strings = {"", "sin-punto", "a.b.c", "***.***"})
    void malformedTokensAreRejected(String token) {
        assertNull(tokens.verify(token));
    }

    private static long now() {
        return System.currentTimeMillis() / 1000;
    }

    private static String encode(String value) {
        return encode(value.getBytes(StandardCharsets.UTF_8));
    }

    private static String encode(byte[] value) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(value);
    }

    private static String sign(String payload) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(SECRET.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        return encode(mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
    }
}
