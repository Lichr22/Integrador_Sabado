"""E4-PRI-F01: simula la tabla `prioridades` con datos sucios a propósito."""

import random

import pandas as pd
from faker import Faker

# nombre -> nivel (1 = más urgente)
NIVELES = {"Urgente": 1, "Alta": 2, "Media": 3, "Baja": 4, "Planificada": 5}
# nivel -> días máximos de respuesta
DIAS = {1: 2, 2: 5, 3: 10, 4: 20, 5: 30}
PALABRAS_NIVEL = {1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco"}

SEMILLA = 42
# dias_max_respuesta es una columna EXTRA: no está en el modelo de Backend II.
COLUMNAS = ["id", "nombre", "nivel", "dias_max_respuesta"]


def _indices(n, porcentaje, excluir=()):
    disponibles = [i for i in range(n) if i not in set(excluir)]
    return random.sample(disponibles, round(n * porcentaje))


def generar_prioridades(n=200):
    Faker.seed(SEMILLA)
    random.seed(SEMILLA)
    fake = Faker("es_CO")

    # Solo hay 5 prioridades reales: llegan repetidas y mal escritas.
    filas = []
    for _ in range(n):
        nombre = random.choice(list(NIVELES.keys()))
        nivel = NIVELES[nombre]
        filas.append({
            # fake.uuid4() produce un UUID v4 igual que uuid.uuid4(), pero reproducible con la semilla.
            "id": fake.uuid4(),
            "nombre": nombre,
            "nivel": nivel,
            "dias_max_respuesta": DIAS[nivel],
        })

    # Datos sucios
    for i in _indices(n, 0.40):
        filas[i]["nombre"] = random.choice([str.upper, lambda texto: f" {texto.lower()} "])(filas[i]["nombre"])
    nivel_nulo = _indices(n, 0.07)
    for i in nivel_nulo:
        filas[i]["nivel"] = None
    for i in _indices(n, 0.25, excluir=nivel_nulo):
        nivel = filas[i]["nivel"]
        filas[i]["nivel"] = random.choice([str(nivel), PALABRAS_NIVEL[nivel]])
    dias_nulo = _indices(n, 0.05)
    for i in dias_nulo:
        filas[i]["dias_max_respuesta"] = None
    for i in _indices(n, 0.03, excluir=dias_nulo):
        filas[i]["dias_max_respuesta"] = 999

    duplicados = [dict(filas[i]) for i in _indices(n, 0.08)]
    df = pd.DataFrame(filas + duplicados, columns=COLUMNAS)
    df = df.sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generar_prioridades()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
