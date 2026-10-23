package cesde.integrador.api;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class AuthTokenService {
    private static final long TOKEN_LIFETIME_SECONDS = 8 * 60 * 60;
    private final byte[] secret;

    public AuthTokenService(@Value("${app.auth.token-secret}") String secret) {
        this.secret = secret.getBytes(StandardCharsets.UTF_8);
        if (this.secret.length < 32) {
            throw new IllegalStateException("APP_AUTH_TOKEN_SECRET must contain at least 32 bytes");
        }
    }

    public String issue(UUID userId) {
        long expiresAt = System.currentTimeMillis() / 1000 + TOKEN_LIFETIME_SECONDS;
        String payload = encode(userId + ":" + expiresAt);
        return payload + "." + encode(sign(payload));
    }

    public UUID verify(String token) {
        try {
            String[] parts = token.split("\\.", -1);
            if (parts.length != 2 || !MessageDigest.isEqual(sign(parts[0]), decode(parts[1]))) {
                return null;
            }
            String[] claims = new String(decode(parts[0]), StandardCharsets.UTF_8).split(":", -1);
            if (claims.length != 2 || Long.parseLong(claims[1]) <= System.currentTimeMillis() / 1000) {
                return null;
            }
            return UUID.fromString(claims[0]);
        } catch (IllegalArgumentException exception) {
            return null;
        }
    }

    private byte[] sign(String payload) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret, "HmacSHA256"));
            return mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
        } catch (Exception exception) {
            throw new IllegalStateException("Unable to sign access token", exception);
        }
    }

    private static String encode(String value) {
        return encode(value.getBytes(StandardCharsets.UTF_8));
    }

    private static String encode(byte[] value) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(value);
    }

    private static byte[] decode(String value) {
        return Base64.getUrlDecoder().decode(value);
    }
}
