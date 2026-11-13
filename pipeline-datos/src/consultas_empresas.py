"""E4-EMP-Q01: cinco consultas sobre data/limpio/empresas_limpio.csv."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    df = pd.read_csv(
        Path(base) / "data" / "limpio" / "empresas_limpio.csv",
        dtype={"nit": str, "telefono": str},
    )
    # Al releer el CSV, activa debe quedar como booleano para que la consulta 1 funcione.
    df["activa"] = df["activa"].astype(str).str.upper().map({"TRUE": True, "FALSE": False})
    return df


def _guardar(resultado, numero, base):
    resultado.to_csv(Path(base) / "data" / "limpio" / f"empresas_consulta_{numero}.csv", encoding="utf-8")


def consulta_1(df, base=RAIZ):
    print("\nConsulta 1 — ¿Qué empresas están activas?")
    activas = df[df["activa"] == True]  # noqa: E712 (así lo pide el criterio)
    print(activas[["nombre", "sector"]])
    _guardar(activas, 1, base)
    return activas


def consulta_2(df, base=RAIZ):
    print("\nConsulta 2 — ¿Qué empresas son del sector Logística, ordenadas por nombre?")
    logistica = df[df["sector"] == "Logistica"].sort_values("nombre")
    print(logistica[["nombre", "contacto"]])
    _guardar(logistica, 2, base)
    return logistica


def consulta_3(df, base=RAIZ):
    print("\nConsulta 3 — ¿Cuántas empresas hay por sector?")
    conteo = df["sector"].value_counts()
    print(conteo)
    _guardar(conteo, 3, base)
    return conteo


def consulta_4(df, base=RAIZ):
    print("\nConsulta 4 — ¿Qué sectores tienen más empresas, de mayor a menor?")
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    print(por_sector)
    _guardar(por_sector, 4, base)
    return por_sector


def consulta_5(df, base=RAIZ):
    print("\nConsulta 5 — ¿Cuántas empresas activas e inactivas hay por sector?")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla)
    _guardar(tabla, 5, base)
    return tabla


def ejecutar(base=RAIZ):
    df = cargar(base)
    return [consulta(df, base) for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5)]


if __name__ == "__main__":
    ejecutar()
