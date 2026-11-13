"""E4-REG-F01: simula la tabla `registros` (participaciones en retos) con datos sucios a propósito."""

import random
import uuid
from datetime import date, datetime, time, timedelta

import pandas as pd
from faker import Faker

ESTADOS = ["INSCRITO", "EN_PROCESO", "FINALIZADO", "CANCELADO"]
VARIANTES_ESTADO = ["inscrito", "EN PROCESO", " Finalizado "]

# Llaves foráneas fijas, generadas una sola vez con su propia semilla.
_ids = random.Random(2026)
IDS_USUARIO = [str(uuid.UUID(int=_ids.getrandbits(128), version=4)) for _ in range(120)]
IDS_RETO = [str(uuid.UUID(int=_ids.getrandbits(128), version=4)) for _ in range(30)]

SEMILLA = 42
COLUMNAS = ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto"]


def _indices(n, porcentaje, excluir=()):
    disponibles = [i for i in range(n) if i not in set(excluir)]
    return random.sample(disponibles, round(n * porcentaje))


def generar_registros(n=800):
    Faker.seed(SEMILLA)
    random.seed(SEMILLA)
    fake = Faker("es_CO")
    # Con end_date="now" cada ejecución usa otra hora y el archivo deja de ser reproducible;
    # se toma como "ahora" el inicio del día, así es igual en todas las ejecuciones del mismo día.
    hoy = datetime.combine(date.today(), time())
    inicio = hoy - timedelta(days=365)

    filas = []
    pares = set()
    while len(filas) < n:
        id_usuario, id_reto = random.choice(IDS_USUARIO), random.choice(IDS_RETO)
        # Los pares base son únicos; las inscripciones dobles se agregan después a propósito.
        if (id_usuario, id_reto) in pares:
            continue
        pares.add((id_usuario, id_reto))
        filas.append({
            # fake.uuid4() produce un UUID v4 igual que uuid.uuid4(), pero reproducible con la semilla.
            "id": fake.uuid4(),
            "fecha_registro": fake.date_time_between(start_date=inicio, end_date=hoy),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": id_usuario,
            "id_reto": id_reto,
        })

    # Datos sucios
    # 10% con el par usuario + reto repetido: el mismo usuario inscrito dos veces en el mismo reto
    repetidas = _indices(n, 0.10)
    originales = _indices(n, 0.10, excluir=repetidas)
    for repetida, original in zip(repetidas, originales):
        filas[repetida]["id_usuario"] = filas[original]["id_usuario"]
        filas[repetida]["id_reto"] = filas[original]["id_reto"]

    # Dos formatos de fecha: "2026-03-15 14:30:00" y "15/03/2026 14:30"
    dia_primero = set(_indices(n, 0.50))
    for i, fila in enumerate(filas):
        formato = "%d/%m/%Y %H:%M" if i in dia_primero else "%Y-%m-%d %H:%M:%S"
        fila["fecha_registro"] = fila["fecha_registro"].strftime(formato)

    for i in _indices(n, 0.20):
        filas[i]["observacion"] = None
    for i in _indices(n, 0.15):
        filas[i]["estado"] = random.choice(VARIANTES_ESTADO)

    duplicados = [dict(filas[i]) for i in _indices(n, 0.05)]
    df = pd.DataFrame(filas + duplicados, columns=COLUMNAS)
    df = df.sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generar_registros()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
