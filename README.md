# Integrador_Sabado — Nexo

Proyecto integrador de plataforma de retos empresariales:

- [Frontend React](./Frontend/README.md): autenticación, Dashboard y módulos CRUD.
- Backend Spring Boot en `Backend/integrador`: API REST conectada a Supabase.
- [Esquema de base de datos](./docs/database-schema.md).

## Inicio local

1. Configura `SUPABASE_DB_URL`, `SUPABASE_DB_USERNAME`,
   `SUPABASE_DB_PASSWORD` y `APP_AUTH_TOKEN_SECRET` en el entorno donde se
   ejecutará Spring Boot. Consulta `Backend/integrador/.env.example`; es una
   plantilla que Spring Boot no carga automáticamente.
2. En `Backend/integrador`, ejecuta `.\mvnw.cmd spring-boot:run` con JDK 17.
   La API escucha en `http://localhost:8081`.
3. En `Frontend`, ejecuta `npm install` y `npm run dev`; abre
   `http://localhost:5173`. Vite proxifica las llamadas `/api` al backend.

## Pruebas unitarias

Ninguna prueba unitaria se conecta a Supabase: las dependencias externas se
simulan con Mockito (Java) o `vi.fn()` (JavaScript).

| Parte | Comando | Resultados | Cobertura |
|---|---|---|---|
| Backend Java (JUnit 5 + Mockito) | `.\mvnw.cmd test` en `Backend/integrador` | `target/reports/surefire.html` | `target/site/jacoco/index.html` |
| Análisis Python (pytest) | `python -m pip install -r requirements-test.txt` y luego `python -m pytest` en `Backend/integrador` | `target/python-reports/pytest.html` | `target/python-reports/coverage/index.html` |
| Frontend React (Vitest + Testing Library) | `npm run test:coverage` en `Frontend` | `npm run test:report` (sirve `test-reports/`) | `coverage/index.html` |

`IntegradorApplicationTests` levanta el contexto completo de Spring y sí usa la
base de datos, por eso está marcada como `@Tag("integration")` y se excluye por
defecto. Para incluirla: `.\mvnw.cmd test "-DexcludedGroups="`.

En el frontend, `npm test` ejecuta Vitest en modo observación y `npm run test:ui`
abre la interfaz interactiva con resultados y cobertura.

El backend conserva el esquema existente (`spring.jpa.hibernate.ddl-auto=none`).
No guardes credenciales ni secretos en el repositorio. Las credenciales de
Supabase que se hayan compartido o versionado anteriormente deben rotarse; si
se publicaron en Git, evalúa también limpiar el historial.
