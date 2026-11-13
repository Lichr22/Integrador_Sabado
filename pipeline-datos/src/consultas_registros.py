"""E4-REG-Q01: cinco consultas sobre data/limpio/registros_limpio.csv."""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    return pd.read_csv(
        Path(base) / "data" / "limpio" / "registros_limpio.csv",
        parse_dates=["fecha_registro"],
    )


def _guardar(resultado, numero, base):
    resultado.to_csv(Path(base) / "data" / "limpio" / f"registros_consulta_{numero}.csv", encoding="utf-8")


def consulta_1(df, base=RAIZ):
    print("\nConsulta 1 — ¿Qué participaciones ya finalizaron?")
    finalizados = df[df["estado"] == "FINALIZADO"]
    print(finalizados[["id_usuario", "id_reto", "fecha_registro"]])
    _guardar(finalizados, 1, base)
    return finalizados


def consulta_2(df, base=RAIZ):
    print("\nConsulta 2 — ¿Hay participaciones repetidas (mismo usuario en el mismo reto)?")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    print(f"En el archivo limpio: {len(repetidos)} (la limpieza ya las eliminó)")
    detectados = pd.read_csv(Path(base) / "data" / "limpio" / "registros_repetidos.csv")
    print(f"Detectadas durante la limpieza: {len(detectados)} (ver data/limpio/registros_repetidos.csv)")
    _guardar(repetidos, 2, base)
    return repetidos


def consulta_3(df, base=RAIZ):
    print("\nConsulta 3 — ¿Cuántas participaciones hay por estado?")
    conteo = df["estado"].value_counts()
    print(conteo)
    _guardar(conteo, 3, base)
    return conteo


def consulta_4(df, base=RAIZ):
    print("\nConsulta 4 — ¿Cuáles son los 10 retos con más participantes?")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    print(top_retos)
    _guardar(top_retos, 4, base)
    return top_retos


def consulta_5(df, base=RAIZ):
    print("\nConsulta 5 — ¿Cuántas participaciones hubo cada mes?")
    por_mes = df.groupby("mes")["id"].count()
    print(por_mes)
    _guardar(por_mes, 5, base)
    return por_mes


def ejecutar(base=RAIZ):
    df = cargar(base)
    return [consulta(df, base) for consulta in (consulta_1, consulta_2, consulta_3, consulta_4, consulta_5)]


if __name__ == "__main__":
    ejecutar()
