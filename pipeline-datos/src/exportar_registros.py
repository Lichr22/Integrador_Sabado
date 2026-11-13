"""E4-REG-X01: exporta los registros sucios a CSV, Excel y JSON."""

import os
from pathlib import Path

from simular_registros import generar_registros

RAIZ = Path(__file__).resolve().parents[1]


def exportar(base=RAIZ, df=None):
    df = generar_registros() if df is None else df
    carpeta = Path(base) / "data" / "crudo"
    os.makedirs(carpeta, exist_ok=True)

    rutas = {
        "csv": carpeta / "registros_sucio.csv",
        "xlsx": carpeta / "registros_sucio.xlsx",
        "json": carpeta / "registros_sucio.json",
    }
    df.to_csv(rutas["csv"], index=False, encoding="utf-8")
    df.to_excel(rutas["xlsx"], index=False, sheet_name="registros")
    df.to_json(rutas["json"], orient="records", force_ascii=False, indent=2)

    for ruta in rutas.values():
        print(f"{ruta.relative_to(base).as_posix()} -> {df.shape}")
    return rutas


if __name__ == "__main__":
    exportar()
