"""E4-EMP-L01: limpia data/crudo/empresas_sucio.csv y genera data/limpio/empresas_limpio.csv."""

import os
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]

COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa", "correo_valido"]
# Se leen como texto para no perder ceros a la izquierda ni el formato original.
TIPOS_TEXTO = {"nit": str, "telefono": str}
VALORES_ACTIVA = {"TRUE": True, "FALSE": False, "SI": True, "NO": False, "1": True, "0": False}


def limpiar(base=RAIZ):
    entrada = Path(base) / "data" / "crudo" / "empresas_sucio.csv"
    if not entrada.exists():
        raise FileNotFoundError(
            f"No existe {entrada}. Ejecuta primero: python src/exportar_empresas.py"
        )
    df = pd.read_csv(entrada, dtype=TIPOS_TEXTO)

    print("=== Diagnóstico inicial ===")
    print(df.shape)
    df.info()
    print(df.isna().sum())
    print(f"Duplicados exactos: {df.duplicated().sum()}")
    filas_inicio = len(df)

    df = df.drop_duplicates()
    df["nombre"] = df["nombre"].str.strip()
    df["sector"] = df["sector"].str.strip().str.title()
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    # '+57 300-123-4567' queda '573001234567': se quita el indicativo para dejar 10 dígitos.
    df["telefono"] = df["telefono"].str.replace(r"^57(?=3\d{9}$)", "", regex=True)
    df["activa"] = df["activa"].astype(str).str.strip().str.upper().map(VALORES_ACTIVA)
    df["contacto"] = df["contacto"].fillna("Sin contacto")
    df["correo_valido"] = df["correo"].str.contains("@", na=False)

    print("\n=== Validaciones ===")
    print(f"Correos inválidos (sin @): {(~df['correo_valido']).sum()}")
    print(f"NIT repetidos entre empresas distintas: {df['nit'].duplicated().sum()}")

    print("\n=== Diagnóstico final ===")
    print(df.shape)
    print(df.isna().sum())
    print(f"Filas eliminadas: {filas_inicio - len(df)}")

    salida = Path(base) / "data" / "limpio" / "empresas_limpio.csv"
    os.makedirs(salida.parent, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8")
    print("Archivo limpio: data/limpio/empresas_limpio.csv")
    return df


if __name__ == "__main__":
    try:
        limpiar()
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
