"""Casos propios de la tabla `prioridades` (E4-PRI). Los casos comunes están en test_comunes.py."""

import pandas as pd
import pytest

import consultas_prioridades
import reporte_prioridades
from conftest import leer_fuente
from limpiar_prioridades import DIAS_MAXIMOS_VALIDOS
from simular_prioridades import DIAS, NIVELES, generar_prioridades

TOLERANCIA = 0.03


def normalizar(nombre):
    return nombre.strip().capitalize()


@pytest.fixture(scope="module")
def df():
    return generar_prioridades()


@pytest.fixture(scope="module")
def pipeline(pipelines):
    return pipelines("prioridades")


@pytest.fixture(scope="module")
def limpio(pipeline):
    return consultas_prioridades.cargar(pipeline["base"])


@pytest.fixture(scope="module")
def crudo(pipeline):
    return pd.read_csv(pipeline["rutas"]["csv"])


def filas_sin_ensuciar(df):
    return df[df["nivel"].map(lambda valor: isinstance(valor, int))]


# ---------------------------------------------------------------- F01 Simulación

def test_tc_pri_f01_006_nombre_pertenece_a_niveles(df):
    assert df["nombre"].map(normalizar).isin(NIVELES).all()


def test_tc_pri_f01_007_coherencia_nombre_nivel(df):
    limpias = filas_sin_ensuciar(df)
    assert (limpias["nivel"] == limpias["nombre"].map(normalizar).map(NIVELES)).all()


def test_tc_pri_f01_008_coherencia_nivel_dias(df):
    limpias = filas_sin_ensuciar(df)
    limpias = limpias[limpias["dias_max_respuesta"].notna() & (limpias["dias_max_respuesta"] != 999)]
    assert (limpias["dias_max_respuesta"] == limpias["nivel"].map(DIAS)).all()
    assert "dias_max_respuesta es una columna EXTRA" in leer_fuente("simular_prioridades")


def test_tc_pri_f01_011_variantes_de_nombre(df):
    valores = set(df["nombre"])
    assert any(v.isupper() for v in valores)
    assert any(v != v.strip() and v.strip().islower() for v in valores)
    assert df["nombre"].nunique() > 5


def test_tc_pri_f01_012_nivel_con_texto_y_palabras(df):
    valores = df["nivel"].dropna()
    assert valores.map(lambda v: isinstance(v, int)).any()
    assert valores.map(lambda v: isinstance(v, str) and v.isdigit()).any()
    assert valores.isin(["uno", "dos", "tres", "cuatro", "cinco"]).any()


def test_tc_pri_f01_013_nulos_en_nivel(df):
    assert df["nivel"].isna().mean() == pytest.approx(0.07, abs=TOLERANCIA)


def test_tc_pri_f01_014_nulos_en_dias(df):
    assert df["dias_max_respuesta"].isna().mean() == pytest.approx(0.05, abs=TOLERANCIA)


def test_tc_pri_f01_015_valor_absurdo_999(df):
    assert (df["dias_max_respuesta"] == 999).mean() == pytest.approx(0.03, abs=0.02)


def test_tc_pri_f01_016_catalogo_repetido(df):
    assert df["nombre"].map(normalizar).nunique() == 5


# ---------------------------------------------------------------- L01 Limpieza

def test_tc_pri_l01_006_nombres_unificados(limpio):
    assert set(limpio["nombre"]) == set(NIVELES)


def test_tc_pri_l01_007_nivel_numerico(limpio):
    assert pd.api.types.is_integer_dtype(limpio["nivel"])


def test_tc_pri_l01_008_palabras_cuatro_y_cinco(crudo, limpio):
    # F01 sí genera "cuatro" y "cinco": deben convertirse igual que "uno", "dos" y "tres".
    assert crudo["nivel"].isin(["cuatro", "cinco"]).any()
    assert limpio["nivel"].isna().sum() == 0
    assert limpio["nivel"].between(1, 5).all()


def test_tc_pri_l01_009_nivel_rellenado_desde_nombre(limpio):
    assert limpio["nivel"].isna().sum() == 0
    assert (limpio["nivel"] == limpio["nombre"].map(NIVELES)).all()


def test_tc_pri_l01_010_dias_numerico(limpio):
    assert pd.api.types.is_numeric_dtype(limpio["dias_max_respuesta"])


def test_tc_pri_l01_011_sin_valores_absurdos(limpio, crudo, pipeline):
    assert (limpio["dias_max_respuesta"] > DIAS_MAXIMOS_VALIDOS).sum() == 0
    assert limpio["dias_max_respuesta"].isna().sum() == 0
    validos = pd.to_numeric(crudo.drop_duplicates()["dias_max_respuesta"], errors="coerce")
    mediana = round(validos[validos <= DIAS_MAXIMOS_VALIDOS].median())
    assert f"Días vacíos rellenados con la mediana: {mediana}" in pipeline["salida"]["limpiar"]
    assert max(DIAS.values()) <= DIAS_MAXIMOS_VALIDOS, "El umbral borraría un valor legítimo"


def test_tc_pri_l01_012_catalogo_exportado(pipeline):
    catalogo = pd.read_csv(pipeline["base"] / "data" / "limpio" / "prioridades_catalogo.csv")
    assert len(catalogo) == 5
    assert catalogo["nombre"].is_unique
    assert sorted(catalogo["nivel"]) == [1, 2, 3, 4, 5]


# ---------------------------------------------------------------- Q01 Consultas

def test_tc_pri_q01_003_consulta_1_ordenadas(pipeline, limpio):
    ordenadas = pipeline["consultas"][0]
    assert len(ordenadas) == len(limpio)
    assert ordenadas["nivel"].is_monotonic_increasing


def test_tc_pri_q01_004_consulta_2_urgentes(pipeline, limpio):
    urgentes = pipeline["consultas"][1]
    assert urgentes["nivel"].isin([1, 2]).all()
    assert len(urgentes) == (limpio["nivel"] <= 2).sum()


def test_tc_pri_q01_005_consulta_3_conteo_por_nombre(pipeline, limpio):
    conteo = pipeline["consultas"][2]
    assert len(conteo) == 5
    assert conteo.sum() == len(limpio)


def test_tc_pri_q01_006_consulta_4_por_nivel(pipeline):
    por_nivel = pipeline["consultas"][3]
    conteo_por_nombre = pipeline["consultas"][2]
    assert list(por_nivel.index) == [1, 2, 3, 4, 5]
    for nombre, nivel in NIVELES.items():
        assert por_nivel[nivel] == conteo_por_nombre[nombre]


def test_tc_pri_q01_007_consulta_5_dias_por_prioridad(pipeline, limpio):
    resumen = pipeline["consultas"][4]
    assert resumen.shape == (5, 3)
    assert list(resumen.columns) == ["min", "mean", "max"]
    assert (resumen == resumen.round(1)).all().all()
    assert (resumen <= DIAS_MAXIMOS_VALIDOS).all().all()
    esperado = limpio.groupby("nombre")["dias_max_respuesta"].agg(["min", "mean", "max"]).round(1)
    assert resumen.equals(esperado)


# ---------------------------------------------------------------- G01 Gráficas

def test_tc_pri_g01_003_grafica_1_barras_por_nivel(pipeline, limpio, ejes):
    por_nivel, ax = ejes(reporte_prioridades.grafica_1, limpio)
    assert (pipeline["base"] / "reportes" / "prioridades_grafica_1.png").exists()
    assert [barra.get_height() for barra in ax.patches] == list(por_nivel.values)
    assert por_nivel.equals(pipeline["consultas"][3])


def test_tc_pri_g01_004_grafica_2_barras_dias_promedio(pipeline, limpio, ejes):
    promedio, ax = ejes(reporte_prioridades.grafica_2, limpio)
    assert (pipeline["base"] / "reportes" / "prioridades_grafica_2.png").exists()
    assert [barra.get_height() for barra in ax.patches] == list(promedio.values)
    assert promedio.equals(pipeline["consultas"][4]["mean"])


def test_tc_pri_g01_005_grafica_3_torta(pipeline, limpio, ejes):
    conteo, ax = ejes(reporte_prioridades.grafica_3, limpio)
    assert (pipeline["base"] / "reportes" / "prioridades_grafica_3.png").exists()
    assert len(ax.patches) == 5
    assert any(texto.get_text().endswith("%") for texto in ax.texts)
    assert conteo.equals(pipeline["consultas"][2])


def test_tc_pri_g01_009_conclusiones_impresas(pipeline, limpio):
    salida = pipeline["salida"]["reporte"]
    conclusiones = salida[salida.index("=== Conclusiones ==="):]
    assert f"quedaron {limpio['nombre'].nunique()} prioridades reales" in conclusiones
    for nivel, dias in limpio.groupby("nivel")["dias_max_respuesta"].median().items():
        assert f"nivel {nivel}: {dias:g} días" in conclusiones
    assert "entre 1 y 5" in conclusiones
