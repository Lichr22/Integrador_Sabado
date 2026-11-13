"""E4-CAT-Q01: cinco consultas sobre data/limpio/categorias_limpio.csv."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    return pd.read_csv(Path(base) / "data" / "limpio" / "categorias_limpio.csv")


def _guardar(resultado, numero, base):
    resultado.to_csv(Path(base) / "data" / "limpio" / f"categorias_consulta_{numero}.csv", encoding="utf-8")


def consulta_1(df, base=RAIZ):
    print("\nConsulta 1 — ¿Cuántas veces aparece cada categoría?")
    conteo = df["nombre"].value_counts()
    print(conteo)
    _guardar(conteo, 1, base)
    return conteo


def consulta_2(df, base=RAIZ):
    print("\nConsulta 2 — ¿Qué categorías no tienen descripción?")
    sin_desc = df[df["descripcion"] == "Sin descripcion"]
    print(sin_desc[["nombre", "area_responsable"]])
    _guardar(sin_desc, 2, base)
    return sin_desc


def consulta_3(df, base=RAIZ):
    print("\nConsulta 3 — ¿Cuál es el largo promedio de la descripción por categoría?")
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    print(largos)
    _guardar(largos, 3, base)
    return largos


def consulta_4(df, base=RAIZ):
    print("\nConsulta 4 — ¿Cuántas categorías maneja cada área?")
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    print(por_area)
    _guardar(por_area, 4, base)
    return por_area


def consulta_5(df, base=RAIZ):
    print("\nConsulta 5 — ¿Cómo se reparten las categorías por área?")
    tabla = df.groupby(["area_responsable", "nombre"])["id"].count().unstack(fill_value=0)
    print(tabla)
    _guardar(tabla, 5, base)
    return tabla


def ejecutar(base=RAIZ):
    df = cargar(base)
    return [consulta(df, base) for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5)]


if __name__ == "__main__":
    ejecutar()
