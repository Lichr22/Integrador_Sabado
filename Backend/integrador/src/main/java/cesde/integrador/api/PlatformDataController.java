package cesde.integrador.api;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class PlatformDataController {
    private static final Map<String, TableSpec> TABLES = Map.of(
            "empresas", spec("nombre", "nit", "sector", "contacto", "correo", "telefono", "activa"),
            "categorias", spec("nombre", "descripcion", "area_responsable"),
            "prioridades", spec("nombre", "nivel", "dias_max_respuesta"),
            "usuarios", spec("nombre", "correo", "activo", "rol", "fecha_registro"),
            "retos", spec("nombre", "descripcion", "fecha_inicio", "fecha_fin", "estado",
                    "id_empresa", "id_categoria", "id_prioridad"),
            "registros", spec("fecha_registro", "observacion", "estado", "id_usuario", "id_reto"));

    private final JdbcTemplate jdbc;
    private final PasswordService passwords;

    public PlatformDataController(JdbcTemplate jdbc, PasswordService passwords) {
        this.jdbc = jdbc;
        this.passwords = passwords;
    }

    @GetMapping("/{resource}")
    public List<Map<String, Object>> findAll(@PathVariable String resource) {
        TableSpec table = table(resource);
        return jdbc.queryForList("SELECT " + table.selectColumns() + " FROM public." + resource + " ORDER BY id");
    }

    @GetMapping("/{resource}/{id}")
    public Map<String, Object> findById(@PathVariable String resource, @PathVariable String id) {
        TableSpec table = table(resource);
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT " + table.selectColumns() + " FROM public." + resource + " WHERE id = ?",
                parseUuid(id));
        if (rows.isEmpty()) {
            throw new ApiException(HttpStatus.NOT_FOUND, "No se encontró el registro solicitado");
        }
        return rows.get(0);
    }

    @PostMapping("/{resource}")
    public Map<String, Object> create(@PathVariable String resource, @RequestBody Map<String, Object> body) {
        TableSpec table = table(resource);
        Map<String, Object> values = normalize(resource, table, body, true);
        UUID id = body.containsKey("id") ? parseUuid(String.valueOf(body.get("id"))) : UUID.randomUUID();
        values.put("id", id);
        if ("usuarios".equals(resource)) {
            values.putIfAbsent("activo", true);
            values.putIfAbsent("rol", "Participante");
            values.putIfAbsent("fecha_registro", LocalDateTime.now());
        }
        insert(resource, table, values);
        return findById(resource, id.toString());
    }

    @PutMapping("/{resource}/{id}")
    public Map<String, Object> update(
            @PathVariable String resource,
            @PathVariable String id,
            @RequestBody Map<String, Object> body) {
        TableSpec table = table(resource);
        UUID recordId = parseUuid(id);
        Map<String, Object> values = normalize(resource, table, body, false);
        values.remove("id");
        if (values.isEmpty()) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "No se recibieron campos para actualizar");
        }
        List<String> columns = new ArrayList<>(values.keySet());
        String assignments = columns.stream().map(column -> column + " = ?").collect(Collectors.joining(", "));
        List<Object> parameters = new ArrayList<>(values.values());
        parameters.add(recordId);
        int changed = jdbc.update("UPDATE public." + resource + " SET " + assignments + " WHERE id = ?",
                parameters.toArray());
        if (changed == 0) {
            throw new ApiException(HttpStatus.NOT_FOUND, "No se encontró el registro solicitado");
        }
        return findById(resource, id);
    }

    @DeleteMapping("/{resource}/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String resource, @PathVariable String id) {
        table(resource);
        int changed = jdbc.update("DELETE FROM public." + resource + " WHERE id = ?", parseUuid(id));
        if (changed == 0) {
            throw new ApiException(HttpStatus.NOT_FOUND, "No se encontró el registro solicitado");
        }
    }

    private void insert(String resource, TableSpec table, Map<String, Object> values) {
        List<String> columns = new ArrayList<>(values.keySet());
        String columnList = String.join(", ", columns);
        String placeholders = columns.stream().map(column -> "?").collect(Collectors.joining(", "));
        jdbc.update("INSERT INTO public." + resource + " (" + columnList + ") VALUES (" + placeholders + ")",
                columns.stream().map(values::get).toArray());
    }

    private Map<String, Object> normalize(
            String resource, TableSpec table, Map<String, Object> body, boolean creating) {
        Map<String, Object> values = new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : body.entrySet()) {
            String column = entry.getKey();
            Object value = entry.getValue();
            if ("id".equals(column)) {
                values.put(column, parseUuid(String.valueOf(value)));
            } else if ("usuarios".equals(resource) && "contrasena".equals(column)) {
                if (value != null && !String.valueOf(value).isBlank()) {
                    String password = String.valueOf(value);
                    if (password.length() < 8) {
                        throw new ApiException(HttpStatus.BAD_REQUEST, "La contraseña debe tener al menos 8 caracteres");
                    }
                    values.put("contrasena_hash", passwords.hash(password));
                }
            } else {
                if (!table.columns().contains(column)) {
                    throw new ApiException(HttpStatus.BAD_REQUEST, "Campo no permitido: " + column);
                }
                values.put(column, convert(column, value));
            }
        }
        if (creating && values.isEmpty()) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "Se requiere al menos un campo para crear el registro");
        }
        return values;
    }

    private Object convert(String column, Object value) {
        if (value == null) {
            return null;
        }
        try {
            if ("id_empresa".equals(column) || "id_categoria".equals(column)
                    || "id_prioridad".equals(column) || "id_usuario".equals(column) || "id_reto".equals(column)) {
                return parseUuid(String.valueOf(value));
            }
            if ("nivel".equals(column) || "dias_max_respuesta".equals(column)) {
                return Short.valueOf(String.valueOf(value));
            }
            if ("activa".equals(column) || "activo".equals(column)) {
                return value instanceof Boolean ? value : Boolean.valueOf(String.valueOf(value));
            }
            if ("fecha_inicio".equals(column) || "fecha_fin".equals(column)) {
                return LocalDate.parse(String.valueOf(value));
            }
            if ("fecha_registro".equals(column)) {
                String text = String.valueOf(value);
                return text.length() == 10 ? LocalDate.parse(text).atStartOfDay() : LocalDateTime.parse(text);
            }
            return value;
        } catch (RuntimeException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "Valor inválido para el campo " + column);
        }
    }

    private TableSpec table(String name) {
        TableSpec table = TABLES.get(name);
        if (table == null) {
            throw new ApiException(HttpStatus.NOT_FOUND, "Recurso no encontrado");
        }
        return table;
    }

    private static UUID parseUuid(String value) {
        try {
            return UUID.fromString(value);
        } catch (IllegalArgumentException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "El identificador debe ser un UUID válido");
        }
    }

    private static TableSpec spec(String... columns) {
        return new TableSpec(Set.of(columns));
    }

    private record TableSpec(Set<String> columns) {
        private String selectColumns() {
            if (columns.contains("contrasena_hash")) {
                return "id, nombre, correo, activo, rol, fecha_registro";
            }
            return "id, " + String.join(", ", columns);
        }
    }
}
