package cesde.integrador.api;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class PasswordServiceTests {
    private final PasswordService passwords = new PasswordService();

    @Test
    void hashFitsDatabaseColumnAndVerifiesPassword() {
        String encoded = passwords.hash("Nexo-Prueba!2026-10-17_Q7m");

        assertEquals(64, encoded.length());
        assertTrue(passwords.matches("Nexo-Prueba!2026-10-17_Q7m", encoded));
        assertFalse(passwords.matches("wrong-password", encoded));
    }
}
