"""E4-REG-L01: limpia data/crudo/registros_sucio.csv y genera data/limpio/registros_limpio.csv."""

import os
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]

COLUMNAS_OBLIGATORIAS = ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto", "mes"]
PAR = ["id_usuario", "id_reto"]


def limpiar(base=RAIZ):
    entrada = Path(base) / "data" / "crudo" / "registros_sucio.csv"
    if not entrada.exists():
        raise FileNotFoundError(
            f"No existe {entrada}. Ejecuta primero: python src/exportar_registros.py"
        )
    df = pd.read_csv(entrada)

    print("=== Diagnóstico inicial ===")
    print(df.shape)
    df.info()
    print(df.isna().sum())
    print(f"Duplicados exactos: {df.duplicated().sum()}")
    filas_inicio = len(df)

    df = df.drop_duplicates()
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], format="mixed", dayfirst=True, errors="coerce")
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    df["observacion"] = df["observacion"].fillna("Sin observacion")

    repetidos = df[df.duplicated(subset=PAR, keep=False)]
    print("\n=== Participaciones repetidas ===")
    print(f"Participaciones repetidas (mismo usuario en el mismo reto): {len(repetidos)}")
    df = df.drop_duplicates(subset=PAR, keep="first")
    print(f"Inscripciones duplicadas eliminadas: {len(repetidos) - repetidos[PAR].drop_duplicates().shape[0]}")

    df["mes"] = df["fecha_registro"].dt.to_period("M")

    print("\n=== Diagnóstico final ===")
    print(df.shape)
    print(df.isna().sum())
    print(f"Filas eliminadas: {filas_inicio - len(df)}")

    salida = Path(base) / "data" / "limpio"
    os.makedirs(salida, exist_ok=True)
    df.to_csv(salida / "registros_limpio.csv", index=False, encoding="utf-8")
    # El limpio ya no tiene los repetidos: se guardan aparte para poder reportarlos en Q01 y G01.
    repetidos.sort_values(PAR).to_csv(salida / "registros_repetidos.csv", index=False, encoding="utf-8")
    print("Archivo limpio: data/limpio/registros_limpio.csv")
    print("Participaciones repetidas: data/limpio/registros_repetidos.csv")
    return df


if __name__ == "__main__":
    try:
        limpiar()
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
