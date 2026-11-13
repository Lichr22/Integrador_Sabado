"""E4-EMP-G01: gráficas y conclusiones a partir de data/limpio/empresas_limpio.csv."""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]


def cargar(base=RAIZ):
    df = pd.read_csv(
        Path(base) / "data" / "limpio" / "empresas_limpio.csv",
        dtype={"nit": str, "telefono": str},
    )
    df["activa"] = df["activa"].astype(str).str.upper().map({"TRUE": True, "FALSE": False})
    return df


def _guardar(ruta, titulo, eje_x, eje_y):
    plt.title(titulo)
    plt.xlabel(eje_x)
    plt.ylabel(eje_y)
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1(df, carpeta):
    por_sector = df.groupby("sector")["id"].count().sort_values(ascending=False)
    plt.figure()
    por_sector.plot(kind="bar")
    _guardar(carpeta / "empresas_grafica_1.png", "Cantidad de empresas por sector", "Sector", "Cantidad de empresas")
    return por_sector


def grafica_2(df, carpeta):
    estados = df["activa"].map({True: "Activa", False: "Inactiva"}).value_counts()
    plt.figure()
    estados.plot(kind="pie", autopct="%1.1f%%")
    _guardar(carpeta / "empresas_grafica_2.png", "Empresas activas vs inactivas", "Porcentaje del total", "Estado")
    return estados


def grafica_3(df, carpeta):
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    tabla.plot(kind="bar", stacked=True)
    _guardar(carpeta / "empresas_grafica_3.png", "Empresas activas e inactivas por sector", "Sector", "Cantidad de empresas")
    return tabla


def conclusiones(df):
    por_sector = df["sector"].value_counts()
    inactivas = (~df["activa"]).mean() * 100
    correos_invalidos = int((~df["correo_valido"]).sum())

    print("\n=== Conclusiones ===")
    print(f"1. El sector con más empresas registradas es {por_sector.idxmax()} ({por_sector.max()} empresas).")
    print(
        f"2. El {inactivas:.1f}% de las empresas está inactivo: son empresas que no pueden publicar "
        "retos, así que la oferta real de la plataforma es menor que el total registrado."
    )
    print(
        f"3. Aparecieron {correos_invalidos} correos inválidos (sin @). El back debe validarlos al "
        "crear o editar una empresa, porque con un correo inválido no se puede contactar a la empresa."
    )
    return {"sector_lider": por_sector.idxmax(), "porcentaje_inactivas": inactivas, "correos_invalidos": correos_invalidos}


def generar_reporte(base=RAIZ):
    df = cargar(base)
    carpeta = Path(base) / "reportes"
    os.makedirs(carpeta, exist_ok=True)
    for numero, grafica in enumerate((grafica_1, grafica_2, grafica_3), start=1):
        grafica(df, carpeta)
        print(f"Gráfica guardada: reportes/empresas_grafica_{numero}.png")
    return conclusiones(df)


if __name__ == "__main__":
    generar_reporte()
