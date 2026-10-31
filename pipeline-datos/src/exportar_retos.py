"""E4-RET-X01: exporta los retos sucios a CSV, Excel y JSON."""

import os
from pathlib import Path

from simular_retos import generar_retos

RAIZ = Path(__file__).resolve().parents[1]


def exportar(base=RAIZ, df=None):
    df = generar_retos() if df is None else df
    carpeta = Path(base) / "data" / "crudo"
    os.makedirs(carpeta, exist_ok=True)

    rutas = {
        "csv": carpeta / "retos_sucio.csv",
        "xlsx": carpeta / "retos_sucio.xlsx",
        "json": carpeta / "retos_sucio.json",
    }
    df.to_csv(rutas["csv"], index=False, encoding="utf-8")
    df.to_excel(rutas["xlsx"], index=False, sheet_name="retos")
    df.to_json(rutas["json"], orient="records", force_ascii=False, indent=2)

    for ruta in rutas.values():
        print(f"{ruta.relative_to(base).as_posix()} -> {df.shape}")
    return rutas


if __name__ == "__main__":
    exportar()
