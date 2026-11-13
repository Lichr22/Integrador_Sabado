"""E4-PRI-Q01: cinco consultas sobre data/limpio/prioridades_limpio.csv."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    return pd.read_csv(Path(base) / "data" / "limpio" / "prioridades_limpio.csv")


def _guardar(resultado, numero, base):
    resultado.to_csv(Path(base) / "data" / "limpio" / f"prioridades_consulta_{numero}.csv", encoding="utf-8")


def consulta_1(df, base=RAIZ):
    print("\nConsulta 1 — ¿Cuáles son las prioridades, de la más urgente a la menos urgente?")
    ordenadas = df.sort_values("nivel")
    print(ordenadas)
    _guardar(ordenadas, 1, base)
    return ordenadas


def consulta_2(df, base=RAIZ):
    print("\nConsulta 2 — ¿Cuáles son las prioridades urgentes (nivel 1 y 2)?")
    urgentes = df[df["nivel"] <= 2]
    print(urgentes)
    _guardar(urgentes, 2, base)
    return urgentes


def consulta_3(df, base=RAIZ):
    print("\nConsulta 3 — ¿Cuántas veces aparece cada nombre?")
    conteo = df["nombre"].value_counts()
    print(conteo)
    _guardar(conteo, 3, base)
    return conteo


def consulta_4(df, base=RAIZ):
    print("\nConsulta 4 — ¿Cuántas filas hay por nivel?")
    por_nivel = df.groupby("nivel")["id"].count()
    print(por_nivel)
    _guardar(por_nivel, 4, base)
    return por_nivel


def consulta_5(df, base=RAIZ):
    print("\nConsulta 5 — ¿Cuáles son los días de respuesta mínimo, promedio y máximo por prioridad?")
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    print(resumen)
    _guardar(resumen, 5, base)
    return resumen


def ejecutar(base=RAIZ):
    df = cargar(base)
    return [consulta(df, base) for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5)]


if __name__ == "__main__":
    ejecutar()
