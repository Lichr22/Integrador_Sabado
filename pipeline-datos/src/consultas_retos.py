"""E4-RET-Q01: cinco consultas sobre data/limpio/retos_limpio.csv."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    return pd.read_csv(
        Path(base) / "data" / "limpio" / "retos_limpio.csv",
        parse_dates=["fecha_inicio", "fecha_fin"],
    )


def _guardar(resultado, numero, base):
    resultado.to_csv(Path(base) / "data" / "limpio" / f"retos_consulta_{numero}.csv", encoding="utf-8")


def consulta_1(df, base=RAIZ):
    print("\nConsulta 1 — ¿Qué retos están en curso?")
    en_curso = df[df["estado"] == "EN_CURSO"]
    print(en_curso[["nombre", "fecha_inicio", "fecha_fin"]])
    _guardar(en_curso, 1, base)
    return en_curso


def consulta_2(df, base=RAIZ):
    print("\nConsulta 2 — ¿Cuáles son los 10 retos más largos?")
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    print(largos)
    _guardar(largos, 2, base)
    return largos


def consulta_3(df, base=RAIZ):
    print("\nConsulta 3 — ¿Cuántos retos hay por estado?")
    conteo = df["estado"].value_counts()
    print(conteo)
    _guardar(conteo, 3, base)
    return conteo


def consulta_4(df, base=RAIZ):
    print("\nConsulta 4 — ¿Cuál es la duración promedio, mínima y máxima por estado?")
    # El criterio indica .agg(["count", "mean", "max"]); se agrega "min" porque la pregunta pide la mínima.
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    print(resumen)
    _guardar(resumen, 4, base)
    return resumen


def consulta_5(df, base=RAIZ):
    print("\nConsulta 5 — ¿Cuántos retos empiezan cada mes?")
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    print(por_mes)
    _guardar(por_mes, 5, base)
    return por_mes


def ejecutar(base=RAIZ):
    df = cargar(base)
    return [consulta(df, base) for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5)]


if __name__ == "__main__":
    ejecutar()
