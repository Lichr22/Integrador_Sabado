"""E4-REG-G01: gráficas y conclusiones a partir de data/limpio/registros_limpio.csv."""

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
        Path(base) / "data" / "limpio" / "registros_limpio.csv",
        parse_dates=["fecha_registro"],
    )


def cargar_repetidos(base=RAIZ):
    return pd.read_csv(Path(base) / "data" / "limpio" / "registros_repetidos.csv")


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
    _guardar(carpeta / "registros_grafica_1.png", "Participaciones por estado", "Estado", "Cantidad de participaciones")
    return conteo


def grafica_2(df, carpeta):
    por_mes = df.groupby("mes")["id"].count()
    plt.figure()
    por_mes.plot(kind="line", marker="o")
    _guardar(carpeta / "registros_grafica_2.png", "Participaciones por mes", "Mes", "Cantidad de participaciones")
    return por_mes


def grafica_3(df, carpeta):
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    plt.figure()
    # Se muestran los primeros 8 caracteres del UUID para que la etiqueta quepa.
    top_retos.rename(index=lambda id_reto: id_reto[:8]).plot(kind="barh")
    _guardar(carpeta / "registros_grafica_3.png", "Los 10 retos con más participantes", "Participantes", "Reto (id)")
    return top_retos


def conclusiones(df, repetidos):
    top_retos = df.groupby("id_reto")["id"].count()
    por_mes = df.groupby("mes")["id"].count()
    anio, mes = map(int, por_mes.idxmax().split("-"))
    duplicadas = len(repetidos) - repetidos[["id_usuario", "id_reto"]].drop_duplicates().shape[0]

    print("\n=== Conclusiones ===")
    print(f"1. El reto más popular es {top_retos.idxmax()} con {top_retos.max()} participantes.")
    print(f"2. El mes con más inscripciones fue {MESES[mes - 1]} de {anio} ({por_mes.max()} participaciones).")
    print(
        f"3. Se encontraron {duplicadas} inscripciones duplicadas (mismo usuario en el mismo reto). "
        "El back debe bloquearlas con 409 Conflict: una persona no puede participar dos veces en el "
        "mismo reto, y los duplicados inflan las estadísticas de participación."
    )
    return {"reto_popular": top_retos.idxmax(), "mes_pico": por_mes.idxmax(), "duplicadas": duplicadas}


def generar_reporte(base=RAIZ):
    df = cargar(base)
    carpeta = Path(base) / "reportes"
    os.makedirs(carpeta, exist_ok=True)
    for numero, grafica in enumerate((grafica_1, grafica_2, grafica_3), start=1):
        grafica(df, carpeta)
        print(f"Gráfica guardada: reportes/registros_grafica_{numero}.png")
    return conclusiones(df, cargar_repetidos(base))


if __name__ == "__main__":
    generar_reporte()
