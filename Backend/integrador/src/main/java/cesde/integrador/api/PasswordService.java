package cesde.integrador.api;

import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.springframework.stereotype.Service;

@Service
public class PasswordService {
    private static final int ITERATIONS = 210_000;
    private static final int KEY_LENGTH_BITS = 192;
    private static final int LEGACY_KEY_LENGTH_BITS = 256;
    private static final int SALT_LENGTH_BYTES = 16;
    private final SecureRandom random = new SecureRandom();

    public String hash(String password) {
        byte[] salt = new byte[SALT_LENGTH_BYTES];
        random.nextBytes(salt);
        byte[] derived = derive(password, salt, ITERATIONS);
        return "2$" + ITERATIONS + "$" + Base64.getUrlEncoder().withoutPadding().encodeToString(salt)
                + "$" + Base64.getUrlEncoder().withoutPadding().encodeToString(derived);
    }

    public boolean matches(String password, String encoded) {
        try {
            String[] parts = encoded.split("\\$", -1);
            if (parts.length != 4) {
                return false;
            }
            boolean legacy = "pbkdf2".equals(parts[0]);
            if (!legacy && !"2".equals(parts[0])) {
                return false;
            }
            int iterations = Integer.parseInt(parts[1]);
            if (iterations < 100_000 || iterations > 1_000_000) {
                return false;
            }
            Base64.Decoder decoder = legacy ? Base64.getDecoder() : Base64.getUrlDecoder();
            byte[] salt = decoder.decode(parts[2]);
            byte[] expected = decoder.decode(parts[3]);
            int keyLengthBits = legacy ? LEGACY_KEY_LENGTH_BITS : KEY_LENGTH_BITS;
            if (salt.length != SALT_LENGTH_BYTES || expected.length != keyLengthBits / 8) {
                return false;
            }
            byte[] actual = derive(password, salt, iterations, keyLengthBits);
            return MessageDigest.isEqual(expected, actual);
        } catch (IllegalArgumentException exception) {
            return false;
        }
    }

    private static byte[] derive(String password, byte[] salt, int iterations) {
        return derive(password, salt, iterations, KEY_LENGTH_BITS);
    }

    private static byte[] derive(String password, byte[] salt, int iterations, int keyLengthBits) {
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLengthBits);
        try {
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                    .generateSecret(spec).getEncoded();
        } catch (Exception exception) {
            throw new IllegalStateException("Unable to derive password hash", exception);
        } finally {
            spec.clearPassword();
        }
    }
}
