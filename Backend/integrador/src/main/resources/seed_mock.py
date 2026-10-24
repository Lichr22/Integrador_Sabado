"""
Seed de datos mock para todas las entidades.
Requiere: pip install faker psycopg2-binary
"""

import uuid
import hashlib
import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2

fake = Faker("es_CO")

DB_URL = "postgresql://postgres.ualbogtnwadouwymjkxj:9tfHf5xGBCNAaDFS@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# ── 1. Categorias ──────────────────────────────────────────────────────────────
areas = ["TI", "Innovación", "Sostenibilidad", "Logística", "Marketing", "RRHH"]
categorias = []
for _ in range(6):
    cid = uuid.uuid4()
    categorias.append(cid)
    cur.execute(
        "INSERT INTO categorias (id, nombre, descripcion, area_responsable) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (str(cid), fake.bs().capitalize(), fake.sentence(), random.choice(areas))
    )

# ── 2. Prioridades ─────────────────────────────────────────────────────────────
prioridades_data = [("Baja", 1, 30), ("Media", 2, 15), ("Alta", 3, 7), ("Crítica", 4, 2)]
prioridades = []
for nombre, nivel, dias in prioridades_data:
    pid = uuid.uuid4()
    prioridades.append(pid)
    cur.execute(
        "INSERT INTO prioridades (id, nombre, nivel, dias_max_respuesta) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (str(pid), nombre, nivel, dias)
    )

# ── 3. Empresas ────────────────────────────────────────────────────────────────
sectores = ["Tecnología", "Salud", "Educación", "Finanzas", "Retail", "Manufactura"]
empresas = []
for _ in range(8):
    eid = uuid.uuid4()
    empresas.append(eid)
    cur.execute(
        "INSERT INTO empresas (id, nombre, nit, sector, contacto, correo, telefono, activa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (str(eid), fake.company(), fake.numerify("###.###.###-#"), random.choice(sectores),
         fake.name(), fake.company_email(), fake.numerify("3##-###-####"), random.choice([True, True, True, False]))
    )

# ── 4. Usuarios ────────────────────────────────────────────────────────────────
roles = ["admin", "usuario", "usuario", "usuario"]
usuarios = []
for _ in range(10):
    uid = uuid.uuid4()
    usuarios.append(uid)
    pwd_hash = hashlib.sha256(fake.password().encode()).hexdigest()
    cur.execute(
        "INSERT INTO usuarios (id, nombre, correo, contrasena_hash, activo, rol, fecha_registro) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (str(uid), fake.name(), fake.unique.email(), pwd_hash,
         True, random.choice(roles), fake.date_time_between(start_date="-1y"))
    )

# ── 5. Retos ───────────────────────────────────────────────────────────────────
estados_reto = ["abierto", "en_progreso", "cerrado"]
retos = []
for _ in range(12):
    rid = uuid.uuid4()
    retos.append(rid)
    inicio = fake.date_between(start_date="-6m", end_date="today")
    fin = inicio + timedelta(days=random.randint(15, 90))
    cur.execute(
        "INSERT INTO retos (id, nombre, descripcion, fecha_inicio, fecha_fin, estado, id_empresa, id_categoria, id_prioridad) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (str(rid), fake.catch_phrase(), fake.paragraph(), inicio, fin,
         random.choice(estados_reto), str(random.choice(empresas)),
         str(random.choice(categorias)), str(random.choice(prioridades)))
    )

# ── 6. Registros ───────────────────────────────────────────────────────────────
estados_reg = ["pendiente", "en_revision", "aprobado", "rechazado"]
for _ in range(20):
    cur.execute(
        "INSERT INTO registros (id, fecha_registro, observacion, estado, id_usuario, id_reto) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (str(uuid.uuid4()), fake.date_time_between(start_date="-3m"),
         fake.paragraph(), random.choice(estados_reg),
         str(random.choice(usuarios)), str(random.choice(retos)))
    )

conn.commit()
cur.close()
conn.close()
print("Datos mock insertados correctamente.")
