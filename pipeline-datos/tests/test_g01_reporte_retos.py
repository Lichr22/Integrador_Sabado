"""E4-RET-G01 — Gráficas y reporte de retos."""

import subprocess

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pytest

import consultas_retos
import reporte_retos
from conftest import RAIZ, SRC, assert_proceso_ok, ejecutar_script, leer_fuente
from exportar_retos import exportar
from limpiar_retos import limpiar


@pytest.fixture(scope="module")
def limpio(pipeline):
    return reporte_retos.cargar(pipeline["base"])


@pytest.fixture
def ejes(monkeypatch, tmp_path):
    """Dibuja una gráfica sin cerrarla para poder inspeccionar los ejes."""
    monkeypatch.setattr(plt, "close", lambda *args: None)

    def dibujar(grafica, df):
        datos = grafica(df, tmp_path)
        ax = plt.gca()
        return datos, ax

    yield dibujar
    plt.close("all")


def ruta_grafica(pipeline, numero):
    return pipeline["base"] / "reportes" / f"retos_grafica_{numero}.png"


def test_tc_ret_g01_001_script_existe_y_corre(ejecucion_real):
    assert (SRC / "reporte_retos.py").exists()
    assert_proceso_ok(ejecucion_real["reporte"])


def test_tc_ret_g01_002_lee_el_archivo_limpio():
    fuente = leer_fuente("reporte")
    assert '"data" / "limpio" / "retos_limpio.csv"' in fuente
    assert "crudo" not in fuente


def test_tc_ret_g01_003_grafica_1_barras(pipeline, limpio, ejes):
    conteo, ax = ejes(reporte_retos.grafica_1, limpio)

    assert ruta_grafica(pipeline, 1).exists()
    assert [barra.get_height() for barra in ax.patches] == list(conteo.values)
    assert conteo.equals(consultas_retos.consulta_3(limpio, pipeline["base"]))


def test_tc_ret_g01_004_grafica_2_linea(pipeline, limpio, ejes):
    por_mes, ax = ejes(reporte_retos.grafica_2, limpio)

    assert ruta_grafica(pipeline, 2).exists()
    assert len(ax.lines) == 1 and ax.lines[0].get_marker() == "o"
    assert list(ax.lines[0].get_ydata()) == list(por_mes.values)
    assert por_mes.equals(consultas_retos.consulta_5(limpio, pipeline["base"]))


def test_tc_ret_g01_005_grafica_3_histograma(pipeline, limpio, ejes):
    duraciones, ax = ejes(reporte_retos.grafica_3, limpio)

    assert ruta_grafica(pipeline, 3).exists()
    assert len(ax.patches) == 20
    assert sum(barra.get_height() for barra in ax.patches) == duraciones.count()


@pytest.mark.parametrize("numero", [1, 2, 3])
def test_tc_ret_g01_006_titulo_y_ejes(limpio, ejes, numero):
    _, ax = ejes(getattr(reporte_retos, f"grafica_{numero}"), limpio)

    assert ax.get_title() and ax.get_xlabel() and ax.get_ylabel()
    assert "plt.tight_layout()" in leer_fuente("reporte")


def test_tc_ret_g01_007_ejecucion_no_bloqueante(pipeline):
    fuente = leer_fuente("reporte")
    assert "plt.show" not in fuente
    assert "dpi=120" in fuente and "plt.close()" in fuente
    # Figura por defecto de 6.4 x 4.8 pulgadas a 120 dpi
    alto, ancho = mpimg.imread(ruta_grafica(pipeline, 1)).shape[:2]
    assert (ancho, alto) == (768, 576)


def test_tc_ret_g01_008_carpeta_reportes_inexistente(copia_proyecto, capsys):
    exportar(copia_proyecto)
    limpiar(copia_proyecto)
    assert not (copia_proyecto / "reportes").exists()

    proceso = ejecutar_script("reporte", cwd=copia_proyecto, timeout=60)

    assert_proceso_ok(proceso)
    assert sorted(p.name for p in (copia_proyecto / "reportes").iterdir()) == [
        "retos_grafica_1.png", "retos_grafica_2.png", "retos_grafica_3.png",
    ]


def test_tc_ret_g01_009_conclusiones_impresas(pipeline, limpio):
    salida = pipeline["salida"]["reporte"]
    conclusiones = salida[salida.index("=== Conclusiones ==="):]
    por_mes = limpio.groupby(limpio["fecha_inicio"].dt.to_period("M"))["id"].count()
    mes_pico = por_mes.idxmax()

    assert f"{reporte_retos.MESES[mes_pico.month - 1]} de {mes_pico.year}" in conclusiones
    assert "Puede deberse" in conclusiones
    for estado, dias in limpio.groupby("estado")["duracion_dias"].mean().round(1).items():
        assert f"{estado}: {dias} días" in conclusiones
    invertidas = (limpio["fecha_fin"] < limpio["fecha_inicio"]).sum()
    assert f"{invertidas} retos tenían la fecha de fin antes que la de inicio" in conclusiones


def test_tc_ret_g01_010_imagenes_versionadas():
    versionadas = subprocess.run(
        ["git", "ls-files", "reportes"], cwd=RAIZ, capture_output=True, text=True,
    ).stdout.split()
    esperadas = [f"reportes/retos_grafica_{numero}.png" for numero in (1, 2, 3)]
    if not versionadas:
        pytest.skip("Bloqueado: las imágenes existen pero aún no se ha hecho commit de reportes/")
    assert sorted(versionadas) == esperadas
