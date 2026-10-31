"""E4-RET-F01: simula la tabla `retos` con datos sucios a propósito."""

import random
from datetime import timedelta

import pandas as pd
from faker import Faker

ESTADOS = ["ABIERTO", "EN_CURSO", "EN_REVISION", "CERRADO"]
VARIANTES_ESTADO = ["en_curso", "EN CURSO", " Cerrado "]

# Llaves foráneas fijas para que varios retos compartan empresa, categoría y prioridad.
IDS_EMPRESA = [
    "3f1c9a52-6e1b-4d7a-9b0e-2a4c8d1f5e01",
    "8a2d4b6c-1f3e-4a5b-8c7d-9e0f1a2b3c02",
    "c4e6f8a0-2b4d-4f6a-8c0e-1a3b5c7d9e03",
    "5b7d9f1a-3c5e-4a7b-9d1f-2b4c6d8e0f04",
    "e9f1a3b5-7c9d-4e1f-a3b5-c7d9e1f3a505",
    "1d3f5a7b-9c1e-4b3d-8f5a-7b9c1d3e5f06",
    "7a9c1e3f-5b7d-4c9e-b1f3-a5c7e9b1d307",
    "2c4e6a8b-0d2f-4e4a-9b6c-8d0e2f4a6b08",
]
IDS_CATEGORIA = [
    "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c01",
    "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d02",
    "c3d4e5f6-a7b8-4c9d-8e1f-2a3b4c5d6e03",
    "d4e5f6a7-b8c9-4d0e-9f2a-3b4c5d6e7f04",
    "e5f6a7b8-c9d0-4e1f-a3b4-c5d6e7f8a905",
    "f6a7b8c9-d0e1-4f2a-b4c5-d6e7f8a9b006",
    "0a1b2c3d-4e5f-4a6b-8c7d-8e9f0a1b2c07",
    "1b2c3d4e-5f6a-4b7c-9d8e-9f0a1b2c3d08",
    "2c3d4e5f-6a7b-4c8d-ae9f-0a1b2c3d4e09",
    "3d4e5f6a-7b8c-4d9e-bf0a-1b2c3d4e5f10",
]
IDS_PRIORIDAD = [
    "9e8d7c6b-5a4f-4e3d-8c2b-1a0f9e8d7c01",
    "8d7c6b5a-4f3e-4d2c-9b1a-0f9e8d7c6b02",
    "7c6b5a4f-3e2d-4c1b-a0f9-e8d7c6b5a403",
]

SEMILLA = 42
COLUMNAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
    "estado", "id_empresa", "id_categoria", "id_prioridad",
]


def _indices(n, porcentaje, excluir=()):
    disponibles = [i for i in range(n) if i not in set(excluir)]
    return random.sample(disponibles, round(n * porcentaje))


def generar_retos(n=500):
    Faker.seed(SEMILLA)
    random.seed(SEMILLA)
    fake = Faker("es_CO")

    filas = []
    for _ in range(n):
        # En Faker "+3m" son 3 minutos; "+3M" son los 3 meses que pide el criterio.
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3M")
        filas.append({
            # fake.uuid4() produce un UUID v4 igual que uuid.uuid4(), pero reproducible con la semilla.
            "id": fake.uuid4(),
            "nombre": fake.sentence(nb_words=6).rstrip("."),
            "descripcion": fake.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })

    # Datos sucios
    for i in _indices(n, 0.10):
        filas[i]["nombre"] = f"  {filas[i]['nombre']}   "
    for i in _indices(n, 0.12):
        filas[i]["descripcion"] = None
    fin_nulo = _indices(n, 0.08)
    for i in fin_nulo:
        filas[i]["fecha_fin"] = None
    for i in _indices(n, 0.05, excluir=fin_nulo):
        filas[i]["fecha_fin"] = filas[i]["fecha_inicio"] - timedelta(days=random.randint(1, 30))
    for i in _indices(n, 0.15):
        filas[i]["estado"] = random.choice(VARIANTES_ESTADO)

    # Dos formatos de fecha mezclados en fecha_inicio: "2026-03-02" y "02/03/2026"
    dia_primero = set(_indices(n, 0.50))
    for i, fila in enumerate(filas):
        formato = "%d/%m/%Y" if i in dia_primero else "%Y-%m-%d"
        fila["fecha_inicio"] = fila["fecha_inicio"].strftime(formato)
        if fila["fecha_fin"] is not None:
            fila["fecha_fin"] = fila["fecha_fin"].isoformat()

    duplicados = [dict(filas[i]) for i in _indices(n, 0.05)]
    df = pd.DataFrame(filas + duplicados, columns=COLUMNAS)
    df = df.sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
