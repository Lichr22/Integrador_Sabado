package cesde.integrador.api;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@DisplayName("PasswordService: hash y verificación de contraseñas")
class PasswordServiceTests {
    private final PasswordService passwords = new PasswordService();

    @Test
    @DisplayName("El hash cabe en la columna de la base de datos y verifica la contraseña")
    void hashFitsDatabaseColumnAndVerifiesPassword() {
        String encoded = passwords.hash("Nexo-Prueba!2026-10-17_Q7m");

        assertEquals(64, encoded.length());
        assertTrue(passwords.matches("Nexo-Prueba!2026-10-17_Q7m", encoded));
        assertFalse(passwords.matches("wrong-password", encoded));
    }

    @Test
    @DisplayName("La misma contraseña genera hashes distintos por usar sal aleatoria")
    void samePasswordProducesDifferentHashes() {
        String first = passwords.hash("clave-repetida");
        String second = passwords.hash("clave-repetida");

        assertNotEquals(first, second);
        assertTrue(passwords.matches("clave-repetida", first));
        assertTrue(passwords.matches("clave-repetida", second));
    }

    @Test
    @DisplayName("El hash usa el formato versión$iteraciones$sal$clave")
    void hashUsesExpectedFormat() {
        String[] parts = passwords.hash("formato").split("\\$");

        assertEquals(4, parts.length);
        assertEquals("2", parts[0]);
        assertEquals("210000", parts[1]);
    }

    @ParameterizedTest(name = "Rechaza el valor almacenado \"{0}\"")
    @DisplayName("Rechaza hashes con formato inválido")
    @ValueSource(strings = {
            "",
            "texto-plano",
            "2$210000$sal",
            "3$210000$AAAAAAAAAAAAAAAAAAAAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "2$abc$AAAAAAAAAAAAAAAAAAAAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "2$99999$AAAAAAAAAAAAAAAAAAAAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "2$1000001$AAAAAAAAAAAAAAAAAAAAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "2$210000$AAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "2$210000$***$***"
    })
    void rejectsMalformedHashes(String encoded) {
        assertFalse(passwords.matches("cualquier-clave", encoded));
    }
}
