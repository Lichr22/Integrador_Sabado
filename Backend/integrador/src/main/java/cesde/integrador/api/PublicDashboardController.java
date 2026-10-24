package cesde.integrador.api;

import java.util.List;
import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/public")
public class PublicDashboardController {
    private final JdbcTemplate jdbc;
    private final CompanyChallengeAnalytics companyChallengeAnalytics;

    public PublicDashboardController(
            JdbcTemplate jdbc,
            CompanyChallengeAnalytics companyChallengeAnalytics) {
        this.jdbc = jdbc;
        this.companyChallengeAnalytics = companyChallengeAnalytics;
    }

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        List<Map<String, Object>> companies = jdbc.queryForList(
                "SELECT id, nombre FROM public.empresas ORDER BY nombre, id");
        List<Map<String, Object>> categories = jdbc.queryForList(
                "SELECT id, nombre FROM public.categorias ORDER BY nombre, id");
        List<Map<String, Object>> priorities = jdbc.queryForList(
                "SELECT id, nombre FROM public.prioridades ORDER BY nivel, id");
        List<Map<String, Object>> openChallenges = jdbc.queryForList("""
                SELECT id, nombre, descripcion, fecha_inicio, fecha_fin, estado,
                       id_empresa, id_categoria, id_prioridad
                FROM public.retos
                WHERE lower(trim(estado)) = 'abierto'
                ORDER BY fecha_fin, id
                LIMIT 3
                """);
        List<Map<String, Object>> recentRegistrations = jdbc.queryForList("""
                SELECT r.id, r.fecha_registro, r.estado, r.id_usuario, r.id_reto,
                       u.nombre AS usuario_nombre, t.nombre AS reto_nombre
                FROM public.registros r
                JOIN public.usuarios u ON u.id = r.id_usuario
                JOIN public.retos t ON t.id = r.id_reto
                ORDER BY r.fecha_registro DESC NULLS LAST, r.id
                LIMIT 5
                """);
        List<Map<String, Object>> weeklyActivity = jdbc.queryForList("""
                SELECT days.dia::date AS dia, count(r.id) AS cantidad
                FROM generate_series(
                    CURRENT_DATE - INTERVAL '6 days',
                    CURRENT_DATE,
                    INTERVAL '1 day'
                ) AS days(dia)
                LEFT JOIN public.registros r
                    ON r.fecha_registro >= days.dia
                   AND r.fecha_registro < days.dia + INTERVAL '1 day'
                GROUP BY days.dia
                ORDER BY days.dia
                """);
        List<Map<String, Object>> challengeCountsByCategory = jdbc.queryForList("""
                SELECT c.id AS categoria_id, count(r.id) AS cantidad
                FROM public.categorias c
                LEFT JOIN public.retos r ON r.id_categoria = c.id
                GROUP BY c.id
                """);
        List<Map<String, Object>> allChallenges = jdbc.queryForList(
                "SELECT id_empresa, estado FROM public.retos");
        Map<String, Object> companyChallengeAnalysis =
                companyChallengeAnalytics.analyze(companies, allChallenges);
        long activeUsers = count("SELECT count(*) FROM public.usuarios WHERE activo IS TRUE");
        long registrationCount = count("SELECT count(*) FROM public.registros");
        long openChallengeCount = count(
                "SELECT count(*) FROM public.retos WHERE lower(trim(estado)) = 'abierto'");

        return Map.ofEntries(
                Map.entry("empresas", companies),
                Map.entry("categorias", categories),
                Map.entry("prioridades", priorities),
                Map.entry("retos", openChallenges),
                Map.entry("registrosRecientes", recentRegistrations),
                Map.entry("actividadSemanal", weeklyActivity),
                Map.entry("retosPorCategoria", challengeCountsByCategory),
                Map.entry("analisisEmpresas", companyChallengeAnalysis),
                Map.entry("usuariosActivos", activeUsers),
                Map.entry("totalRegistros", registrationCount),
                Map.entry("retosAbiertos", openChallengeCount));
    }

    private long count(String sql) {
        Number result = jdbc.queryForObject(sql, Number.class);
        return result == null ? 0 : result.longValue();
    }
}
