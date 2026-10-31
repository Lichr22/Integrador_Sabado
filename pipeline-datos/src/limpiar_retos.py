"""E4-RET-L01: limpia data/crudo/retos_sucio.csv y genera data/limpio/retos_limpio.csv."""

import os
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]

# fecha_fin no es obligatoria: un reto puede no tener fecha de cierre definida.
COLUMNAS_OBLIGATORIAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "estado",
    "id_empresa", "id_categoria", "id_prioridad",
]


def limpiar(base=RAIZ):
    entrada = Path(base) / "data" / "crudo" / "retos_sucio.csv"
    if not entrada.exists():
        raise FileNotFoundError(
            f"No existe {entrada}. Ejecuta primero: python src/exportar_retos.py"
        )
    df = pd.read_csv(entrada)

    print("=== Diagnóstico inicial ===")
    print(df.shape)
    df.info()
    nulos_antes = df.isna().sum()
    print(nulos_antes)
    print(f"Duplicados exactos: {df.duplicated().sum()}")
    filas_inicio = len(df)

    df = df.drop_duplicates()
    df["nombre"] = df["nombre"].str.strip()
    for columna in ["fecha_inicio", "fecha_fin"]:
        df[columna] = pd.to_datetime(df[columna], format="mixed", dayfirst=True, errors="coerce")
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days.astype("Int64")
    # Solo es incoherente si la fecha de fin existe y es anterior al inicio; los nulos se reportan aparte.
    df["fecha_valida"] = ~(df["duracion_dias"] < 0).fillna(False).astype(bool)

    print("\n=== Fechas ===")
    print(f"Retos con fecha de fin anterior a la de inicio: {(~df['fecha_valida']).sum()}")
    print(f"Retos sin fecha de fin: {df['fecha_fin'].isna().sum()}")

    print("\n=== Nulos antes y después ===")
    print(pd.DataFrame({"antes": nulos_antes, "despues": df.isna().sum()}).fillna(0).astype(int))

    print("\n=== Diagnóstico final ===")
    print(df.shape)
    print(df.isna().sum())
    print(f"Filas eliminadas: {filas_inicio - len(df)}")

    salida = Path(base) / "data" / "limpio" / "retos_limpio.csv"
    os.makedirs(salida.parent, exist_ok=True)
    df.to_csv(salida, index=False, encoding="utf-8")
    print(f"Archivo limpio: {salida.relative_to(base).as_posix()}")
    return df


if __name__ == "__main__":
    try:
        limpiar()
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
