"""E4-CAT-L01: limpia data/crudo/categorias_sucio.csv y genera data/limpio/categorias_limpio.csv."""

import os
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]

COLUMNAS_OBLIGATORIAS = ["id", "nombre", "descripcion", "area_responsable", "largo_desc"]


def limpiar(base=RAIZ):
    entrada = Path(base) / "data" / "crudo" / "categorias_sucio.csv"
    if not entrada.exists():
        raise FileNotFoundError(
            f"No existe {entrada}. Ejecuta primero: python src/exportar_categorias.py"
        )
    df = pd.read_csv(entrada)

    print("=== Diagnóstico inicial ===")
    print(df.shape)
    df.info()
    print(df.isna().sum())
    print(f"Duplicados exactos: {df.duplicated().sum()}")
    filas_inicio = len(df)

    df = df.drop_duplicates()
    df["nombre"] = df["nombre"].str.strip().str.title()
    # Quitar las tildes para que "logística" y "logistica" queden iguales
    df["nombre"] = df["nombre"].str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("utf-8")
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["area_responsable"] = df["area_responsable"].fillna("Sin asignar")
    df["largo_desc"] = df["descripcion"].str.len()

    salida = Path(base) / "data" / "limpio"
    os.makedirs(salida, exist_ok=True)
    catalogo = df.drop_duplicates(subset=["nombre"]).sort_values("nombre")
    catalogo.to_csv(salida / "categorias_catalogo.csv", index=False, encoding="utf-8")

    print("\n=== Resultado de la limpieza ===")
    print(f"Filas antes de limpiar: {filas_inicio}")
    print(f"Filas después de limpiar: {len(df)}")
    print(f"Categorías reales en el catálogo: {len(catalogo)}")

    print("\n=== Diagnóstico final ===")
    print(df.shape)
    print(df.isna().sum())
    print(f"Filas eliminadas: {filas_inicio - len(df)}")

    df.to_csv(salida / "categorias_limpio.csv", index=False, encoding="utf-8")
    print("Archivo limpio: data/limpio/categorias_limpio.csv")
    print("Catálogo: data/limpio/categorias_catalogo.csv")
    return df


if __name__ == "__main__":
    try:
        limpiar()
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
