package cesde.integrador.api;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.server.ResponseStatusException;

@DisplayName("ApiErrorHandler: respuestas de error de la API")
class ApiErrorHandlerTests {
    private final ApiErrorHandler handler = new ApiErrorHandler();

    @Test
    @DisplayName("Conserva el código y el mensaje de un ResponseStatusException")
    void keepsStatusAndReason() {
        ResponseEntity<Map<String, String>> response =
                handler.handleStatus(new ApiException(HttpStatus.NOT_FOUND, "Empresa no encontrada"));

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        assertEquals("Empresa no encontrada", response.getBody().get("message"));
    }

    @Test
    @DisplayName("Usa un mensaje genérico cuando la excepción no trae motivo")
    void usesDefaultMessageWithoutReason() {
        ResponseEntity<Map<String, String>> response =
                handler.handleStatus(new ResponseStatusException(HttpStatus.BAD_REQUEST));

        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals("La solicitud no pudo completarse", response.getBody().get("message"));
    }

    @Test
    @DisplayName("Una violación de restricción de la base de datos responde 409")
    void constraintViolationIsConflict() {
        ResponseEntity<Map<String, String>> response =
                handler.handleConstraint(new DataIntegrityViolationException("fk_retos_empresa"));

        assertEquals(HttpStatus.CONFLICT, response.getStatusCode());
        assertEquals("El registro está relacionado con otros datos o incumple una restricción",
                response.getBody().get("message"));
    }
}
