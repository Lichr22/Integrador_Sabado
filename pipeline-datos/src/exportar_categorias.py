"""E4-CAT-X01: exporta las categorías sucias a CSV, Excel y JSON."""

import os
from pathlib import Path

from simular_categorias import generar_categorias

RAIZ = Path(__file__).resolve().parents[1]


def exportar(base=RAIZ, df=None):
    df = generar_categorias() if df is None else df
    carpeta = Path(base) / "data" / "crudo"
    os.makedirs(carpeta, exist_ok=True)

    rutas = {
        "csv": carpeta / "categorias_sucio.csv",
        "xlsx": carpeta / "categorias_sucio.xlsx",
        "json": carpeta / "categorias_sucio.json",
    }
    df.to_csv(rutas["csv"], index=False, encoding="utf-8")
    df.to_excel(rutas["xlsx"], index=False, sheet_name="categorias")
    df.to_json(rutas["json"], orient="records", force_ascii=False, indent=2)

    for ruta in rutas.values():
        print(f"{ruta.relative_to(base).as_posix()} -> {df.shape}")
    return rutas


if __name__ == "__main__":
    exportar()
