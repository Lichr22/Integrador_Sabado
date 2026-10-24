package cesde.integrador.api;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

@Component
public class CompanyChallengeAnalytics {
    private final ObjectMapper objectMapper = new ObjectMapper();
    private static final TypeReference<Map<String, Object>> RESULT_TYPE =
            new TypeReference<>() {};

    private final String pythonExecutable;

    public CompanyChallengeAnalytics(
            @Value("${app.analytics.python:python}") String pythonExecutable) {
        this.pythonExecutable = pythonExecutable;
    }

    public Map<String, Object> analyze(
            List<Map<String, Object>> companies,
            List<Map<String, Object>> challenges) {
        try {
            String script = new ClassPathResource("company_challenge_analysis.py")
                    .getContentAsString(StandardCharsets.UTF_8);
            String encodedScript = Base64.getEncoder()
                    .encodeToString(script.getBytes(StandardCharsets.UTF_8));
            String command = "import base64;exec(base64.b64decode('" + encodedScript + "'))";
            ProcessBuilder processBuilder = new ProcessBuilder(pythonExecutable, "-c", command);
            processBuilder.environment().put("PYTHONUTF8", "1");
            Process process = processBuilder.start();
            try (var input = process.getOutputStream()) {
                objectMapper.writeValue(input, Map.of("empresas", companies, "retos", challenges));
            }

            byte[] output = process.getInputStream().readAllBytes();
            byte[] error = process.getErrorStream().readAllBytes();
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                throw new IllegalStateException(
                        "El análisis Python terminó con error: "
                                + new String(error, StandardCharsets.UTF_8).trim());
            }
            return objectMapper.readValue(output, RESULT_TYPE);
        } catch (IOException error) {
            throw new IllegalStateException(
                    "No se pudo ejecutar el análisis Python. Configure app.analytics.python.",
                    error);
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("El análisis Python fue interrumpido.", error);
        }
    }
}
