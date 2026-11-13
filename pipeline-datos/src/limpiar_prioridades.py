"""E4-PRI-L01: limpia data/crudo/prioridades_sucio.csv y genera data/limpio/prioridades_limpio.csv."""

import os
import sys
from pathlib import Path

import pandas as pd

from simular_prioridades import NIVELES

RAIZ = Path(__file__).resolve().parents[1]

COLUMNAS_OBLIGATORIAS = ["id", "nombre", "nivel", "dias_max_respuesta"]
# El criterio solo mapea uno/dos/tres; se agregan cuatro y cinco porque también hay niveles 4 y 5.
PALABRAS = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
DIAS_MAXIMOS_VALIDOS = 60


def limpiar(base=RAIZ):
    entrada = Path(base) / "data" / "crudo" / "prioridades_sucio.csv"
    if not entrada.exists():
        raise FileNotFoundError(
            f"No existe {entrada}. Ejecuta primero: python src/exportar_prioridades.py"
        )
    df = pd.read_csv(entrada)

    print("=== Diagnóstico inicial ===")
    print(df.shape)
    df.info()
    print(df.isna().sum())
    print(f"Duplicados exactos: {df.duplicated().sum()}")
    filas_inicio = len(df)

    df = df.drop_duplicates()
    df["nombre"] = df["nombre"].str.strip().str.capitalize()
    df["nivel"] = pd.to_numeric(df["nivel"].replace(PALABRAS), errors="coerce")
    df["nivel"] = df["nivel"].fillna(df["nombre"].map(NIVELES)).astype(int)

    df["dias_max_respuesta"] = pd.to_numeric(df["dias_max_respuesta"], errors="coerce")
    absurdos = (df["dias_max_respuesta"] > DIAS_MAXIMOS_VALIDOS).sum()
    df.loc[df["dias_max_respuesta"] > DIAS_MAXIMOS_VALIDOS, "dias_max_respuesta"] = None
    mediana = round(df["dias_max_respuesta"].median())
    df["dias_max_respuesta"] = df["dias_max_respuesta"].fillna(mediana).astype(int)
    print(f"\nValores absurdos (> {DIAS_MAXIMOS_VALIDOS} días) marcados como nulos: {absurdos}")
    print(f"Días vacíos rellenados con la mediana: {mediana}")

    salida = Path(base) / "data" / "limpio"
    os.makedirs(salida, exist_ok=True)
    catalogo = df.drop_duplicates(subset=["nombre"]).sort_values("nivel")
    catalogo.to_csv(salida / "prioridades_catalogo.csv", index=False, encoding="utf-8")
    print(f"Prioridades reales en el catálogo: {len(catalogo)}")

    print("\n=== Diagnóstico final ===")
    print(df.shape)
    print(df.isna().sum())
    print(f"Filas eliminadas: {filas_inicio - len(df)}")

    df.to_csv(salida / "prioridades_limpio.csv", index=False, encoding="utf-8")
    print("Archivo limpio: data/limpio/prioridades_limpio.csv")
    print("Catálogo: data/limpio/prioridades_catalogo.csv")
    return df


if __name__ == "__main__":
    try:
        limpiar()
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
