"""E4-RET-Q01 — Consultas sobre los retos limpios."""

import pandas as pd
import pytest

import consultas_retos
from conftest import SRC, assert_proceso_ok, leer_fuente


@pytest.fixture(scope="module")
def limpio(pipeline):
    return consultas_retos.cargar(pipeline["base"])


def archivo_consulta(pipeline, numero):
    return pipeline["base"] / "data" / "limpio" / f"retos_consulta_{numero}.csv"


def test_tc_ret_q01_001_script_existe_y_corre(ejecucion_real):
    assert (SRC / "consultas_retos.py").exists()
    assert_proceso_ok(ejecucion_real["consultas"])


def test_tc_ret_q01_002_lee_el_archivo_limpio():
    fuente = leer_fuente("consultas")
    assert '"data" / "limpio" / "retos_limpio.csv"' in fuente
    assert "crudo" not in fuente


def test_tc_ret_q01_003_consulta_1_en_curso(pipeline, limpio):
    en_curso = pipeline["consultas"][0]
    assert (en_curso["estado"] == "EN_CURSO").all()
    assert len(en_curso) == limpio["estado"].value_counts()["EN_CURSO"]
    assert len(pd.read_csv(archivo_consulta(pipeline, 1))) == len(en_curso)


def test_tc_ret_q01_004_consulta_2_diez_mas_largos(pipeline, limpio):
    largos = pipeline["consultas"][1]
    assert largos.shape == (10, 3)
    assert list(largos.columns) == ["nombre", "duracion_dias", "estado"]
    assert largos["duracion_dias"].is_monotonic_decreasing
    assert largos["duracion_dias"].iloc[0] == limpio["duracion_dias"].max()
    assert len(pd.read_csv(archivo_consulta(pipeline, 2))) == 10


def test_tc_ret_q01_005_consulta_3_por_estado(pipeline, limpio):
    conteo = pipeline["consultas"][2]
    assert set(conteo.index) == set(limpio["estado"])
    assert conteo.sum() == len(limpio)
    assert archivo_consulta(pipeline, 3).exists()


def test_tc_ret_q01_006_consulta_4_groupby_duracion(pipeline, limpio):
    resumen = pipeline["consultas"][3]
    assert list(resumen.columns) == ["count", "mean", "min", "max"]
    assert set(resumen.index) == set(limpio["estado"])
    for estado, grupo in limpio.groupby("estado"):
        assert resumen.loc[estado, "count"] == grupo["duracion_dias"].count()
        assert resumen.loc[estado, "mean"] == pytest.approx(grupo["duracion_dias"].mean())
        assert resumen.loc[estado, "min"] == grupo["duracion_dias"].min()
        assert resumen.loc[estado, "max"] == grupo["duracion_dias"].max()
    assert archivo_consulta(pipeline, 4).exists()


def test_tc_ret_q01_007_consulta_5_por_mes(pipeline, limpio):
    por_mes = pipeline["consultas"][4]
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha_inicio"])
    assert isinstance(por_mes.index, pd.PeriodIndex) and por_mes.index.freqstr == "M"
    assert por_mes.index.is_monotonic_increasing
    assert por_mes.sum() == len(limpio)
    assert archivo_consulta(pipeline, 5).exists()


def test_tc_ret_q01_008_usa_groupby():
    assert leer_fuente("consultas").count(".groupby(") >= 2


def test_tc_ret_q01_009_una_funcion_por_consulta(pipeline):
    salida = pipeline["salida"]["consultas"]
    for numero in range(1, 6):
        assert callable(getattr(consultas_retos, f"consulta_{numero}"))
        assert f"Consulta {numero} — ¿" in salida


def test_tc_ret_q01_010_cinco_archivos_de_consulta(pipeline):
    for numero in range(1, 6):
        ruta = archivo_consulta(pipeline, numero)
        assert ruta.exists() and len(pd.read_csv(ruta)) > 0, ruta.name


def test_tc_ret_q01_011_orden_de_salida(ejecucion_real):
    salida = ejecucion_real["consultas"].stdout
    posiciones = [salida.index(f"Consulta {numero} —") for numero in range(1, 6)]
    assert posiciones == sorted(posiciones)
