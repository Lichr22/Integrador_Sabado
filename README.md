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

El backend conserva el esquema existente (`spring.jpa.hibernate.ddl-auto=none`).
No guardes credenciales ni secretos en el repositorio. Las credenciales de
Supabase que se hayan compartido o versionado anteriormente deben rotarse; si
se publicaron en Git, evalúa también limpiar el historial.
