"""E4-PRI-G01: gráficas y conclusiones a partir de data/limpio/prioridades_limpio.csv."""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    return pd.read_csv(Path(base) / "data" / "limpio" / "prioridades_limpio.csv")


def _guardar(ruta, titulo, eje_x, eje_y):
    plt.title(titulo)
    plt.xlabel(eje_x)
    plt.ylabel(eje_y)
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1(df, carpeta):
    por_nivel = df.groupby("nivel")["id"].count()
    plt.figure()
    por_nivel.plot(kind="bar")
    _guardar(carpeta / "prioridades_grafica_1.png", "Cantidad de filas por nivel", "Nivel (1 = más urgente)", "Cantidad de filas")
    return por_nivel


def grafica_2(df, carpeta):
    resumen = df.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    plt.figure()
    resumen["mean"].plot(kind="bar")
    _guardar(carpeta / "prioridades_grafica_2.png", "Días promedio de respuesta por prioridad", "Prioridad", "Días promedio")
    return resumen["mean"]


def grafica_3(df, carpeta):
    conteo = df["nombre"].value_counts()
    plt.figure()
    conteo.plot(kind="pie", autopct="%1.1f%%")
    _guardar(carpeta / "prioridades_grafica_3.png", "Reparto de las prioridades", "Porcentaje del total", "Prioridad")
    return conteo


def conclusiones(df):
    reales = df["nombre"].nunique()
    dias_por_nivel = df.groupby("nivel")["dias_max_respuesta"].median()
    crece = dias_por_nivel.is_monotonic_increasing

    print("\n=== Conclusiones ===")
    print(f"1. Al final quedaron {reales} prioridades reales.")
    detalle = ", ".join(f"nivel {nivel}: {dias:g} días" for nivel, dias in dias_por_nivel.items())
    relacion = "a mayor nivel (menos urgente), más días de respuesta" if crece else "no hay una relación directa"
    print(f"2. Relación entre nivel y días máximos de respuesta: {relacion} ({detalle}).")
    print(
        "3. El back debe validar que `nivel` esté entre 1 y 5: un nivel fuera de ese rango no "
        "corresponde a ninguna prioridad real y rompe el orden de urgencia."
    )
    return {"reales": reales, "dias_por_nivel": dias_por_nivel}


def generar_reporte(base=RAIZ):
    df = cargar(base)
    carpeta = Path(base) / "reportes"
    os.makedirs(carpeta, exist_ok=True)
    for numero, grafica in enumerate((grafica_1, grafica_2, grafica_3), start=1):
        grafica(df, carpeta)
        print(f"Gráfica guardada: reportes/prioridades_grafica_{numero}.png")
    return conclusiones(df)


if __name__ == "__main__":
    generar_reporte()
