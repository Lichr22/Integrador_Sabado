"""E4-CAT-F01: simula la tabla `categorias` con datos sucios a propósito."""

import random
import unicodedata

import pandas as pd
from faker import Faker

CATEGORIAS = [
    "Logística", "Tecnología", "Innovación", "Sostenibilidad", "Finanzas",
    "Mercadeo", "Recursos Humanos", "Producción", "Calidad", "Educación",
]
# area_responsable es una columna EXTRA: no está en el modelo de Backend II.
AREAS = ["Operaciones", "Tecnología", "Comercial", "Talento Humano", "Financiera", "Dirección"]

SEMILLA = 42
COLUMNAS = ["id", "nombre", "descripcion", "area_responsable"]


def _sin_tildes(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")


# Variantes de escritura: 'Logistica', 'LOGISTICA', ' logistica ', 'logística'
VARIANTES_NOMBRE = [
    _sin_tildes,
    lambda nombre: _sin_tildes(nombre).upper(),
    lambda nombre: f" {_sin_tildes(nombre).lower()} ",
    str.lower,
]


def _indices(n, porcentaje):
    return random.sample(range(n), round(n * porcentaje))


def generar_categorias(n=250):
    Faker.seed(SEMILLA)
    random.seed(SEMILLA)
    fake = Faker("es_CO")

    # Solo hay 10 categorías reales: el catálogo llega repetido.
    filas = [
        {
            # fake.uuid4() produce un UUID v4 igual que uuid.uuid4(), pero reproducible con la semilla.
            "id": fake.uuid4(),
            "nombre": random.choice(CATEGORIAS),
            "descripcion": fake.sentence(nb_words=8),
            "area_responsable": random.choice(AREAS),
        }
        for _ in range(n)
    ]

    # Datos sucios
    for i in _indices(n, 0.40):
        filas[i]["nombre"] = random.choice(VARIANTES_NOMBRE)(filas[i]["nombre"])
    for i in _indices(n, 0.15):
        filas[i]["descripcion"] = None
    for i in _indices(n, 0.10):
        filas[i]["area_responsable"] = None

    duplicados = [dict(filas[i]) for i in _indices(n, 0.08)]
    df = pd.DataFrame(filas + duplicados, columns=COLUMNAS)
    df = df.sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generar_categorias()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
