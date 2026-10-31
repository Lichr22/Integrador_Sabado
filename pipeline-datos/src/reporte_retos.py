"""E4-RET-G01: gráficas y conclusiones a partir de data/limpio/retos_limpio.csv."""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def cargar(base=RAIZ):
    return pd.read_csv(
        Path(base) / "data" / "limpio" / "retos_limpio.csv",
        parse_dates=["fecha_inicio", "fecha_fin"],
    )


def _guardar(ruta, titulo, eje_x, eje_y):
    plt.title(titulo)
    plt.xlabel(eje_x)
    plt.ylabel(eje_y)
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()


def grafica_1(df, carpeta):
    conteo = df["estado"].value_counts()
    plt.figure()
    conteo.plot(kind="bar")
    _guardar(carpeta / "retos_grafica_1.png", "Cantidad de retos por estado", "Estado", "Cantidad de retos")
    return conteo


def grafica_2(df, carpeta):
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    plt.figure()
    por_mes.plot(kind="line", marker="o")
    _guardar(carpeta / "retos_grafica_2.png", "Retos que empiezan cada mes", "Mes de inicio", "Cantidad de retos")
    return por_mes


def grafica_3(df, carpeta):
    duraciones = df["duracion_dias"]
    plt.figure()
    duraciones.plot(kind="hist", bins=20)
    _guardar(carpeta / "retos_grafica_3.png", "Distribución de la duración de los retos", "Duración (días)", "Cantidad de retos")
    return duraciones


def conclusiones(df, por_mes):
    mes_pico = por_mes.idxmax()
    promedio_por_estado = df.groupby("estado")["duracion_dias"].mean().round(1)
    fechas_invertidas = int((~df["fecha_valida"]).sum())

    print("\n=== Conclusiones ===")
    print(
        f"1. Los retos se concentran en {MESES[mes_pico.month - 1]} de {mes_pico.year} "
        f"({por_mes.max()} retos, frente a un promedio de {por_mes.mean():.1f} por mes). "
        "Puede deberse a que las empresas lanzan sus retos al planear un nuevo trimestre o semestre."
    )
    print("2. Duración promedio de un reto según su estado:")
    for estado, dias in promedio_por_estado.items():
        print(f"   - {estado}: {dias} días")
    print(
        f"3. {fechas_invertidas} retos tenían la fecha de fin antes que la de inicio; "
        "el back debe rechazarlas al crear o editar un reto."
    )
    return {"mes_pico": mes_pico, "promedio_por_estado": promedio_por_estado, "fechas_invertidas": fechas_invertidas}


def generar_reporte(base=RAIZ):
    df = cargar(base)
    carpeta = Path(base) / "reportes"
    os.makedirs(carpeta, exist_ok=True)
    grafica_1(df, carpeta)
    por_mes = grafica_2(df, carpeta)
    grafica_3(df, carpeta)
    for numero in (1, 2, 3):
        print(f"Gráfica guardada: reportes/retos_grafica_{numero}.png")
    return conclusiones(df, por_mes)


if __name__ == "__main__":
    generar_reporte()
