# Nexo — Plataforma Web de Retos Empresariales

Aplicación **React + Vite** para administrar retos empresariales. El frontend consume la API REST del backend Spring Boot, que persiste los datos en Supabase.

## Ejecutar el proyecto

Requisitos: **Node.js 20.19+ o 22.12+**, npm y JDK 17 para el backend.

### 1. Configura y ejecuta el backend

En `Backend/integrador`, configura las variables de entorno usando los datos
actuales de conexión de tu proyecto Supabase. `.env.example` es una plantilla
de referencia: Spring Boot no la carga automáticamente.

En PowerShell, define estas variables en la misma terminal antes de arrancar
Maven:

```powershell
$env:SUPABASE_DB_URL = "jdbc:postgresql://<host>:5432/postgres?sslmode=require"
$env:SUPABASE_DB_USERNAME = "<usuario-de-base-de-datos>"
$env:SUPABASE_DB_PASSWORD = "<contraseña-actual-de-supabase>"
$env:APP_AUTH_TOKEN_SECRET = "<secreto-aleatorio-de-al-menos-32-caracteres>"
$env:FRONTEND_ORIGIN = "http://localhost:5173"
.\mvnw.cmd spring-boot:run
```

El backend se inicia en `http://localhost:8081` y no modifica el esquema
(`ddl-auto=none`). No subas secretos al repositorio.

### 2. Ejecuta el frontend

Desde `Frontend`, en otra terminal:

```bash
npm install
npm run dev
```

Abre `http://localhost:5173`. Vite reenvía `/api` al backend del puerto 8081.
Para apuntar a otro host, define `VITE_API_BASE_URL` en `Frontend/.env.local`.

Para compilar una versión de producción:

```bash
npm run build
npm run preview
```

## Características

- **Dashboard:** indicadores, retos destacados, distribución por categorías, inscripciones recientes y participación semanal, cargados desde la API.
- **6 módulos con CRUD:** Empresas, Retos, Categorías, Prioridades, Usuarios y Registros.
- Crear, consultar, editar y eliminar registros mediante formularios y tablas.
- Vista de tarjetas y de tabla para Retos; detalle del reto e inscripciones asociadas.
- Búsqueda, filtro por estado, ordenamiento, exportación a CSV y diseño responsive.
- **Persistencia en Supabase** mediante API REST Spring Boot.
- **Menú del avatar:** accesos a Iniciar sesión, Registrarse, Mi perfil y Cerrar sesión.
- **Autenticación del backend:** registro y login con contraseñas almacenadas mediante PBKDF2, token bearer con vencimiento y perfil autenticado.
- **Acceso sin sesión:** Dashboard disponible en modo lectura con datos públicos actualizados (incluye nombres de participantes e inscripciones recientes), mientras las acciones y módulos permanecen deshabilitados; “Sobre el proyecto” también está disponible. Perfil y CRUD requieren una sesión válida; el token se guarda en `sessionStorage`.
- **Mi perfil:** consulta y edición del nombre y correo de la cuenta autenticada.

## Acceder a las nuevas pantallas

1. Asegúrate de que el backend y Supabase estén disponibles.
2. Registra una cuenta desde **Registrarse**; la sesión se inicia automáticamente.
3. Cierra sesión y vuelve a ingresar para comprobar el login.
4. Desde el Dashboard, abre los módulos para consultar y administrar las entidades.

Rutas: `/#login`, `/#registro`, `/#perfil`. Se utilizan rutas hash, sin necesidad de instalar React Router.

> La sesión usa tokens bearer, no cookies. Protege el secreto de firma y las
> credenciales de Supabase; el backend valida que la cuenta siga activa en cada
> solicitud protegida.

## API

- `POST /api/auth/register`, `POST /api/auth/login` y `GET /api/auth/me`.
- `GET /api/public/dashboard` ofrece únicamente los datos necesarios para el Dashboard público; no expone correos ni hashes de contraseña.
- CRUD protegido con bearer token para `/api/empresas`, `/api/categorias`,
  `/api/prioridades`, `/api/usuarios`, `/api/retos` y `/api/registros`.
- Las contraseñas se reciben como `contrasena`; el backend almacena únicamente
  su hash PBKDF2. Nunca expone `contrasena_hash` en respuestas.

## Relaciones de datos

El esquema relacional está documentado en
[docs/database-schema.md](../docs/database-schema.md). El backend consulta y
actualiza estas tablas directamente.

| Relación | Cardinalidad |
|---|---|
| Empresa → Reto | 1:N |
| Categoría → Reto | 1:N |
| Prioridad → Reto | 1:N |
| Usuario → Registro | 1:N |
| Reto → Registro | 1:N |

- Los formularios usan las entidades relacionadas cargadas desde la API.
- Las claves foráneas de la base de datos protegen las relaciones.
- El formulario valida las fechas del reto y evita duplicar la inscripción de un usuario al mismo reto.

## Estructura del proyecto

```text
nexo-retos-spa/
├── index.html
├── package.json
├── vite.config.js
├── README.md
└── src/
    ├── assets/                          # Recursos estáticos del frontend
    ├── main.jsx                         # Montaje de React
    └── modules/
        ├── core/
        │   ├── styles/styles.css        # Estilos globales
        │   └── utils/formatters.js      # Utilidades compartidas
        ├── auth/
        │   ├── components/AuthComponents.jsx # Formularios y layout compartidos
        │   ├── pages/
        │       ├── Login.jsx
        │       ├── Registro.jsx
        │       └── Perfil.jsx
        │   └── styles/account.css       # Estilos de autenticación y perfil
        └── platform/
            ├── components/
            │   ├── PlatformApp.jsx     # Layout, rutas y estado compartido
            │   ├── EntityPage.jsx      # Tabla reutilizable para los módulos CRUD
            │   └── PlatformUi.jsx      # Componentes compartidos de plataforma
            ├── pages/
            │   ├── Dashboard.jsx
            │   ├── Reto.jsx
            │   ├── Empresa.jsx
            │   ├── Categoria.jsx
            │   ├── Prioridad.jsx
            │   ├── Usuario.jsx
            │   └── Registro.jsx
            ├── lib/data.js             # Navegación y configuración CRUD
            └── services/platformApi.js # Cliente REST y mapeo de datos
```

Cada pantalla tiene su propio componente: `Login.jsx`, `Registro.jsx`,
`Dashboard.jsx` y los componentes de módulo como `Reto.jsx`, `Empresa.jsx` y
`Usuario.jsx`. Los módulos CRUD reutilizan `EntityPage.jsx`; `PlatformApp.jsx`
conserva el layout, el enrutamiento privado y el estado compartido.

## Solución al error `Cannot find module '@tailwindcss/postcss'`

Este proyecto usa **CSS normal**, no Tailwind. Si hay un `postcss.config.mjs`
en una carpeta superior (por ejemplo `C:\Users\...\Downloads\`), Vite puede
intentar aplicar esa configuración a este proyecto y fallar porque no está
instalado `@tailwindcss/postcss`.

El archivo `vite.config.js` incluye `css.postcss.plugins: []` para indicar a
Vite que utilice una configuración PostCSS local vacía y **no busque
configuraciones ajenas en carpetas superiores**.

Si ya tenías el proyecto abierto, reemplaza `vite.config.js` por el del ZIP
corregido, detén el servidor con `Ctrl+C` y ejecuta `npm run dev` de nuevo.
No es necesario instalar Tailwind ni borrar archivos de otros proyectos.
