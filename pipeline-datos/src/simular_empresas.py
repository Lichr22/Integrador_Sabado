"""E4-EMP-F01: simula la tabla `empresas` con datos sucios a propósito."""

import random

import pandas as pd
from faker import Faker

SECTORES = ["Logistica", "Tecnologia", "Manufactura", "Salud", "Educacion", "Finanzas", "Comercio", "Energia"]

SEMILLA = 42
COLUMNAS = ["id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa"]


def _indices(n, porcentaje, excluir=()):
    disponibles = [i for i in range(n) if i not in set(excluir)]
    return random.sample(disponibles, round(n * porcentaje))


def _formato_telefono(numero, formato):
    if formato == 1:
        return f"{numero[:3]} {numero[3:6]} {numero[6:]}"
    if formato == 2:
        return f"+57 {numero[:3]}-{numero[3:6]}-{numero[6:]}"
    return numero


def generar_empresas(n=300):
    Faker.seed(SEMILLA)
    random.seed(SEMILLA)
    fake = Faker("es_CO")

    filas = [
        {
            # fake.uuid4() produce un UUID v4 igual que uuid.uuid4(), pero reproducible con la semilla.
            "id": fake.uuid4(),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        }
        for _ in range(n)
    ]

    # Datos sucios
    # 3% de NIT repetidos entre empresas distintas (el NIT debería ser único)
    copias = _indices(n, 0.03)
    originales = _indices(n, 0.03, excluir=copias)
    for copia, original in zip(copias, originales):
        filas[copia]["nit"] = filas[original]["nit"]

    espacios = _indices(n, 0.10)
    for i in espacios:
        filas[i]["nombre"] = f"  {filas[i]['nombre']}   "
    for i in _indices(n, 0.15, excluir=espacios):
        filas[i]["nombre"] = filas[i]["nombre"].upper()

    # La mitad del NIT con puntos y guiones (900.123.456-7) y la otra mitad sin nada (9001234567)
    con_puntos = set(_indices(n, 0.50))
    for i, fila in enumerate(filas):
        digitos = fila["nit"].replace("-", "")
        fila["nit"] = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9]}" if i in con_puntos else digitos
        fila["telefono"] = _formato_telefono(fila["telefono"], random.randint(0, 2))

    for i in _indices(n, 0.30):
        filas[i]["sector"] = random.choice([str.upper, lambda texto: f" {texto.lower()} "])(filas[i]["sector"])
    for i in _indices(n, 0.08):
        filas[i]["contacto"] = None
    for i in _indices(n, 0.06):
        filas[i]["correo"] = filas[i]["correo"].replace("@", "")
    for i in _indices(n, 0.20):
        filas[i]["activa"] = random.choice(["SI", "1"] if filas[i]["activa"] else ["No", "0"])

    duplicados = [dict(filas[i]) for i in _indices(n, 0.05)]
    df = pd.DataFrame(filas + duplicados, columns=COLUMNAS)
    df = df.sample(frac=1, random_state=SEMILLA).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
