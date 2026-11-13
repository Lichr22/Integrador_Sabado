"""Casos propios de la tabla `categorias` (E4-CAT). Los casos comunes están en test_comunes.py."""

import unicodedata

import pandas as pd
import pytest

import consultas_categorias
import reporte_categorias
from conftest import leer_fuente
from simular_categorias import AREAS, CATEGORIAS, generar_categorias

TOLERANCIA = 0.03


def normalizar(texto):
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return sin_tildes.strip().lower()


@pytest.fixture(scope="module")
def df():
    return generar_categorias()


@pytest.fixture(scope="module")
def pipeline(pipelines):
    return pipelines("categorias")


@pytest.fixture(scope="module")
def limpio(pipeline):
    return consultas_categorias.cargar(pipeline["base"])


@pytest.fixture(scope="module")
def crudo(pipeline):
    return pd.read_csv(pipeline["rutas"]["csv"])


# ---------------------------------------------------------------- F01 Simulación

def test_tc_cat_f01_006_nombre_pertenece_al_catalogo(df):
    catalogo = {normalizar(nombre) for nombre in CATEGORIAS}
    normalizados = df["nombre"].map(normalizar)
    assert normalizados.isin(catalogo).all()
    assert normalizados.nunique() == 10


def test_tc_cat_f01_007_descripcion_es_frase(df):
    descripciones = df["descripcion"].dropna()
    assert descripciones.str.endswith(".").all()
    assert 6 <= descripciones.str.split().str.len().mean() <= 10


def test_tc_cat_f01_008_area_pertenece_a_areas(df):
    assert df["area_responsable"].dropna().isin(AREAS).all()
    assert "area_responsable es una columna EXTRA" in leer_fuente("simular_categorias")


def test_tc_cat_f01_011_variantes_de_escritura(df):
    valores = set(df["nombre"])
    assert any(v.isupper() for v in valores), "Falta la variante en MAYÚSCULAS"
    assert any(v != v.strip() for v in valores), "Falta la variante con espacios al borde"
    assert any(v in CATEGORIAS for v in valores) and any(normalizar(v) == v.strip() for v in valores)
    assert df["nombre"].nunique() > 10


def test_tc_cat_f01_012_nulos_en_descripcion(df):
    base = df.drop_duplicates()
    assert base["descripcion"].isna().mean() == pytest.approx(0.15, abs=TOLERANCIA)


def test_tc_cat_f01_013_nulos_en_area_responsable(df):
    assert df["area_responsable"].isna().mean() == pytest.approx(0.10, abs=TOLERANCIA)


def test_tc_cat_f01_014_catalogo_repetido(df):
    conteo = df["nombre"].map(normalizar).value_counts()
    assert len(conteo) == 10
    assert (conteo > 1).all()


# ---------------------------------------------------------------- L01 Limpieza

def test_tc_cat_l01_006_nombre_sin_espacios_y_title_case(limpio):
    assert (limpio["nombre"] == limpio["nombre"].str.strip().str.title()).all()


def test_tc_cat_l01_007_sin_tildes_en_nombre(limpio):
    assert limpio["nombre"].map(str.isascii).all()
    assert "Logistica" in set(limpio["nombre"])


def test_tc_cat_l01_008_exactamente_10_categorias(limpio):
    assert limpio["nombre"].nunique() == 10


def test_tc_cat_l01_009_nulos_rellenados(limpio, crudo):
    base = crudo.drop_duplicates()
    assert limpio.isna().sum().sum() == 0
    assert (limpio["descripcion"] == "Sin descripcion").sum() == base["descripcion"].isna().sum()
    assert (limpio["area_responsable"] == "Sin asignar").sum() == base["area_responsable"].isna().sum()


def test_tc_cat_l01_010_columna_largo_desc(limpio):
    assert pd.api.types.is_integer_dtype(limpio["largo_desc"])
    assert (limpio["largo_desc"] == limpio["descripcion"].str.len()).all()
    assert (limpio.loc[limpio["descripcion"] == "Sin descripcion", "largo_desc"] == 15).all()


def test_tc_cat_l01_011_catalogo_exportado(pipeline):
    catalogo = pd.read_csv(pipeline["base"] / "data" / "limpio" / "categorias_catalogo.csv")
    assert len(catalogo) == 10
    assert catalogo["nombre"].is_unique


def test_tc_cat_l01_012_antes_vs_despues(pipeline, crudo, limpio):
    salida = pipeline["salida"]["limpiar"]
    assert f"Filas antes de limpiar: {len(crudo)}" in salida
    assert f"Filas después de limpiar: {len(limpio)}" in salida


# ---------------------------------------------------------------- Q01 Consultas

def test_tc_cat_q01_003_consulta_1_veces_por_categoria(pipeline, limpio):
    conteo = pipeline["consultas"][0]
    assert len(conteo) == 10
    assert conteo.sum() == len(limpio)
    assert conteo.equals(limpio["nombre"].value_counts())


def test_tc_cat_q01_004_consulta_2_sin_descripcion(pipeline, crudo):
    sin_desc = pipeline["consultas"][1]
    assert (sin_desc["descripcion"] == "Sin descripcion").all()
    assert len(sin_desc) == crudo.drop_duplicates()["descripcion"].isna().sum()


def test_tc_cat_q01_005_consulta_3_largo_promedio(pipeline, limpio):
    largos = pipeline["consultas"][2]
    assert len(largos) == 10
    assert largos.is_monotonic_decreasing
    assert (largos == largos.round(1)).all()
    esperado = limpio.groupby("nombre")["largo_desc"].mean().round(1)
    assert largos.sort_index().equals(esperado.sort_index())


def test_tc_cat_q01_006_consulta_4_por_area(pipeline, limpio):
    por_area = pipeline["consultas"][3]
    assert "Sin asignar" in por_area.index
    assert por_area.is_monotonic_decreasing
    assert por_area.sum() == len(limpio)


def test_tc_cat_q01_007_consulta_5_tabla_cruzada(pipeline, limpio):
    tabla = pipeline["consultas"][4]
    assert tabla.shape == (limpio["area_responsable"].nunique(), 10)
    assert not tabla.isna().any().any()
    assert tabla.to_numpy().sum() == len(limpio)


# ---------------------------------------------------------------- G01 Gráficas

def test_tc_cat_g01_003_grafica_1_barras_horizontales(pipeline, limpio, ejes):
    conteo, ax = ejes(reporte_categorias.grafica_1, limpio)
    assert (pipeline["base"] / "reportes" / "categorias_grafica_1.png").exists()
    assert [barra.get_width() for barra in ax.patches] == list(conteo.values)
    assert conteo.equals(pipeline["consultas"][0])


def test_tc_cat_g01_004_grafica_2_torta(pipeline, limpio, ejes):
    por_area, ax = ejes(reporte_categorias.grafica_2, limpio)
    assert (pipeline["base"] / "reportes" / "categorias_grafica_2.png").exists()
    assert len(ax.patches) == len(por_area)  # una porción por área
    assert any(texto.get_text().endswith("%") for texto in ax.texts)
    assert por_area.equals(pipeline["consultas"][3])


def test_tc_cat_g01_005_grafica_3_barras(pipeline, limpio, ejes):
    largos, ax = ejes(reporte_categorias.grafica_3, limpio)
    assert (pipeline["base"] / "reportes" / "categorias_grafica_3.png").exists()
    assert [barra.get_height() for barra in ax.patches] == list(largos.values)
    assert largos.equals(pipeline["consultas"][2])


def test_tc_cat_g01_009_conclusiones_impresas(pipeline, limpio):
    salida = pipeline["salida"]["reporte"]
    conclusiones = salida[salida.index("=== Conclusiones ==="):]
    reales = limpio["nombre"].nunique()
    assert f"se eliminaron {len(limpio) - reales} filas" in conclusiones
    assert f"quedaron {reales} categorías reales" in conclusiones
    assert "ÚNICO" in conclusiones
