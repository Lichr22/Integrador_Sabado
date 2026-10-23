# Esquema de base de datos

Este documento registra el modelo relacional compartido para la plataforma de
retos empresariales. El SQL se proporciona **como referencia del esquema**; no
es una migración ni un script listo para ejecutar.

## Entidades y columnas

| Tabla | Columna | Tipo | Clave |
|---|---|---|---|
| `empresas` | `id` | `uuid` | PK |
| `empresas` | `nombre` | `character varying` | |
| `empresas` | `nit` | `character varying` | |
| `empresas` | `sector` | `character varying` | |
| `empresas` | `contacto` | `character varying` | |
| `empresas` | `correo` | `character varying` | |
| `empresas` | `telefono` | `character varying` | |
| `empresas` | `activa` | `boolean` | |
| `categorias` | `id` | `uuid` | PK |
| `categorias` | `nombre` | `character varying` | |
| `categorias` | `descripcion` | `text` | |
| `categorias` | `area_responsable` | `character varying` | |
| `prioridades` | `id` | `uuid` | PK |
| `prioridades` | `nombre` | `character varying` | |
| `prioridades` | `nivel` | `smallint` | |
| `prioridades` | `dias_max_respuesta` | `smallint` | |
| `usuarios` | `id` | `uuid` | PK |
| `usuarios` | `nombre` | `character varying` | |
| `usuarios` | `correo` | `character varying` | |
| `usuarios` | `contrasena_hash` | `character varying` | |
| `usuarios` | `activo` | `boolean` | |
| `usuarios` | `rol` | `character varying` | |
| `usuarios` | `fecha_registro` | `timestamp without time zone` | |
| `retos` | `id` | `uuid` | PK |
| `retos` | `nombre` | `character varying` | |
| `retos` | `descripcion` | `text` | |
| `retos` | `fecha_inicio` | `date` | |
| `retos` | `fecha_fin` | `date` | |
| `retos` | `estado` | `character varying` | |
| `retos` | `id_empresa` | `uuid` | FK → `empresas.id` |
| `retos` | `id_categoria` | `uuid` | FK → `categorias.id` |
| `retos` | `id_prioridad` | `uuid` | FK → `prioridades.id` |
| `registros` | `id` | `uuid` | PK |
| `registros` | `fecha_registro` | `timestamp without time zone` | |
| `registros` | `observacion` | `text` | |
| `registros` | `estado` | `character varying` | |
| `registros` | `id_usuario` | `uuid` | FK → `usuarios.id` |
| `registros` | `id_reto` | `uuid` | FK → `retos.id` |

No se especifican restricciones `NOT NULL`, valores por defecto ni reglas de
unicidad aparte de las claves primarias mostradas. No deben asumirse a partir de
este documento.

## Relaciones

- Una empresa puede estar asociada con varios retos; cada reto referencia una
  empresa mediante `retos.id_empresa`.
- Una categoría puede clasificar varios retos; cada reto referencia una
  categoría mediante `retos.id_categoria`.
- Una prioridad puede asignarse a varios retos; cada reto referencia una
  prioridad mediante `retos.id_prioridad`.
- Un usuario puede tener varios registros de participación; cada registro
  referencia un usuario mediante `registros.id_usuario`.
- Un reto puede tener varios registros de participación; cada registro
  referencia un reto mediante `registros.id_reto`.

```text
empresas   ──< retos >── categorias
                    └── prioridades

usuarios   ──< registros >── retos
```

## SQL de referencia

```sql
-- ADVERTENCIA: este esquema es solo de contexto y no está destinado
-- a ejecutarse directamente. El orden y las restricciones pueden requerir ajustes.

CREATE TABLE public.empresas (
  id uuid NOT NULL,
  nombre character varying,
  nit character varying,
  sector character varying,
  contacto character varying,
  correo character varying,
  telefono character varying,
  activa boolean,
  CONSTRAINT empresas_pkey PRIMARY KEY (id)
);

CREATE TABLE public.categorias (
  id uuid NOT NULL,
  nombre character varying,
  descripcion text,
  area_responsable character varying,
  CONSTRAINT categorias_pkey PRIMARY KEY (id)
);

CREATE TABLE public.prioridades (
  id uuid NOT NULL,
  nombre character varying,
  nivel smallint,
  dias_max_respuesta smallint,
  CONSTRAINT prioridades_pkey PRIMARY KEY (id)
);

CREATE TABLE public.usuarios (
  id uuid NOT NULL,
  nombre character varying,
  correo character varying,
  contrasena_hash character varying,
  activo boolean,
  rol character varying,
  fecha_registro timestamp without time zone,
  CONSTRAINT usuarios_pkey PRIMARY KEY (id)
);

CREATE TABLE public.retos (
  id uuid NOT NULL,
  nombre character varying,
  descripcion text,
  fecha_inicio date,
  fecha_fin date,
  estado character varying,
  id_empresa uuid,
  id_categoria uuid,
  id_prioridad uuid,
  CONSTRAINT retos_pkey PRIMARY KEY (id),
  CONSTRAINT retos_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresas(id),
  CONSTRAINT retos_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categorias(id),
  CONSTRAINT retos_id_prioridad_fkey FOREIGN KEY (id_prioridad) REFERENCES public.prioridades(id)
);

CREATE TABLE public.registros (
  id uuid NOT NULL,
  fecha_registro timestamp without time zone,
  observacion text,
  estado character varying,
  id_usuario uuid,
  id_reto uuid,
  CONSTRAINT registros_pkey PRIMARY KEY (id),
  CONSTRAINT registros_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id),
  CONSTRAINT registros_id_reto_fkey FOREIGN KEY (id_reto) REFERENCES public.retos(id)
);
```

## Alcance respecto al frontend

El frontend actual continúa usando datos ficticios en `localStorage`; esta
documentación no implica que exista una conexión a PostgreSQL ni una API. El
esquema sirve como referencia para una futura integración con el backend.
