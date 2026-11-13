"""E4-CAT-G01: gráficas y conclusiones a partir de data/limpio/categorias_limpio.csv."""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    return pd.read_csv(Path(base) / "data" / "limpio" / "categorias_limpio.csv")


def _guardar(ruta, titulo, eje_x, eje_y):
    plt.title(titulo)
    plt.xlabel(eje_x)
    plt.ylabel(eje_y)
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1(df, carpeta):
    conteo = df["nombre"].value_counts()
    plt.figure()
    conteo.plot(kind="barh")
    _guardar(carpeta / "categorias_grafica_1.png", "Veces que aparece cada categoría", "Cantidad de filas", "Categoría")
    return conteo


def grafica_2(df, carpeta):
    por_area = df.groupby("area_responsable")["id"].count().sort_values(ascending=False)
    plt.figure()
    por_area.plot(kind="pie", autopct="%1.1f%%")
    _guardar(carpeta / "categorias_grafica_2.png", "Reparto de categorías por área responsable", "Porcentaje del total", "Área responsable")
    return por_area


def grafica_3(df, carpeta):
    largos = df.groupby("nombre")["largo_desc"].mean().round(1).sort_values(ascending=False)
    plt.figure()
    largos.plot(kind="bar")
    _guardar(carpeta / "categorias_grafica_3.png", "Largo promedio de la descripción por categoría", "Categoría", "Caracteres en promedio")
    return largos


def conclusiones(df):
    reales = df["nombre"].nunique()
    eliminadas = len(df) - reales

    print("\n=== Conclusiones ===")
    print(
        f"1. Para llegar al catálogo se eliminaron {eliminadas} filas: el mismo nombre llegaba repetido "
        "y escrito de varias formas (mayúsculas, espacios, tildes)."
    )
    print(f"2. Al final quedaron {reales} categorías reales.")
    print(
        "3. El back debe declarar `nombre` como ÚNICO: así la base rechaza una categoría repetida "
        "o escrita distinto y el catálogo no vuelve a crecer con duplicados."
    )
    return {"eliminadas": eliminadas, "reales": reales}


def generar_reporte(base=RAIZ):
    df = cargar(base)
    carpeta = Path(base) / "reportes"
    os.makedirs(carpeta, exist_ok=True)
    for numero, grafica in enumerate((grafica_1, grafica_2, grafica_3), start=1):
        grafica(df, carpeta)
        print(f"Gráfica guardada: reportes/categorias_grafica_{numero}.png")
    return conclusiones(df)


if __name__ == "__main__":
    generar_reporte()
