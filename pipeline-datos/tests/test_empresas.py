"""Casos propios de la tabla `empresas` (E4-EMP). Los casos comunes están en test_comunes.py."""

import pandas as pd
import pytest

import consultas_empresas
import reporte_empresas
from limpiar_empresas import TIPOS_TEXTO
from simular_empresas import SECTORES, generar_empresas

TOLERANCIA = 0.03


@pytest.fixture(scope="module")
def df():
    return generar_empresas()


@pytest.fixture(scope="module")
def base(df):
    """Las 300 empresas sin los duplicados exactos."""
    return df.drop_duplicates()


@pytest.fixture(scope="module")
def pipeline(pipelines):
    return pipelines("empresas")


@pytest.fixture(scope="module")
def limpio(pipeline):
    return consultas_empresas.cargar(pipeline["base"])


@pytest.fixture(scope="module")
def crudo(pipeline):
    return pd.read_csv(pipeline["rutas"]["csv"], dtype=TIPOS_TEXTO)


def solo_digitos(serie):
    return serie.str.replace(r"\D", "", regex=True)


# ---------------------------------------------------------------- F01 Simulación

def test_tc_emp_f01_006_nombre_de_empresa(df):
    assert df["nombre"].str.strip().str.len().gt(0).all()


def test_tc_emp_f01_007_formato_base_de_nit(df):
    assert solo_digitos(df["nit"]).str.fullmatch(r"\d{10}").all()


def test_tc_emp_f01_008_sector_pertenece_a_sectores(df):
    assert df["sector"].str.strip().str.title().isin(SECTORES).all()


def test_tc_emp_f01_009_contacto_es_nombre_de_persona(df):
    contactos = df["contacto"].dropna()
    assert (contactos.str.split().str.len() >= 2).all()


def test_tc_emp_f01_010_correo_de_empresa(df):
    validos = df.loc[df["correo"].str.contains("@"), "correo"]
    assert validos.str.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]+").all()


def test_tc_emp_f01_011_formato_base_de_telefono(df):
    numeros = solo_digitos(df["telefono"]).str.replace(r"^57(?=\d{10}$)", "", regex=True)
    assert numeros.str.fullmatch(r"3\d{9}").all()


def test_tc_emp_f01_012_activa_booleano_base(df):
    no_ensuciados = df["activa"][df["activa"].map(lambda valor: isinstance(valor, bool))]
    assert set(no_ensuciados) == {True, False}


def test_tc_emp_f01_015_espacios_sobrantes_en_nombre(base):
    assert (base["nombre"] != base["nombre"].str.strip()).mean() == pytest.approx(0.10, abs=TOLERANCIA)


def test_tc_emp_f01_016_nombres_en_mayusculas(base):
    assert base["nombre"].str.isupper().mean() == pytest.approx(0.15, abs=TOLERANCIA)


def test_tc_emp_f01_017_dos_formatos_de_nit(base):
    con_puntos = base["nit"].str.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d")
    sin_nada = base["nit"].str.fullmatch(r"\d{10}")
    assert (con_puntos | sin_nada).all()
    assert con_puntos.mean() == pytest.approx(0.50, abs=0.01)


def test_tc_emp_f01_018_variantes_de_sector(df):
    valores = set(df["sector"])
    assert any(v.isupper() for v in valores)
    assert any(v != v.strip() and v.strip().islower() for v in valores)


def test_tc_emp_f01_019_nulos_en_contacto(df):
    assert df["contacto"].isna().mean() == pytest.approx(0.08, abs=TOLERANCIA)


def test_tc_emp_f01_020_correos_sin_arroba(df):
    assert (~df["correo"].str.contains("@")).mean() == pytest.approx(0.06, abs=0.02)


def test_tc_emp_f01_021_tres_formatos_de_telefono(df):
    formatos = [r"3\d{9}", r"3\d{2} \d{3} \d{4}", r"\+57 3\d{2}-\d{3}-\d{4}"]
    coincide = [df["telefono"].str.fullmatch(formato) for formato in formatos]
    assert all(serie.any() for serie in coincide)
    assert (coincide[0] | coincide[1] | coincide[2]).all()


def test_tc_emp_f01_022_activa_con_texto(df):
    tipos = df["activa"].map(type).value_counts()
    assert bool in tipos and str in tipos
    assert set(df["activa"][df["activa"].map(lambda v: isinstance(v, str))]) == {"SI", "No", "1", "0"}


def test_tc_emp_f01_024_nit_repetido_entre_empresas(base):
    nit = solo_digitos(base["nit"])
    assert base.loc[nit.duplicated(keep=False), "id"].is_unique
    assert nit.duplicated().mean() == pytest.approx(0.03, abs=0.01)


# ---------------------------------------------------------------- L01 Limpieza

def test_tc_emp_l01_006_nombre_sin_espacios(limpio):
    assert (limpio["nombre"] != limpio["nombre"].str.strip()).sum() == 0


def test_tc_emp_l01_007_sectores_unificados(limpio):
    assert set(limpio["sector"]) == set(SECTORES)


def test_tc_emp_l01_008_nit_solo_digitos(pipeline):
    df = pd.read_csv(pipeline["base"] / "data" / "limpio" / "empresas_limpio.csv", dtype={"nit": str})
    assert df["nit"].str.fullmatch(r"\d{10}").all()


def test_tc_emp_l01_009_telefono_solo_digitos(limpio):
    assert limpio["telefono"].str.fullmatch(r"\d+").all()
    # Se quita el indicativo 57 para que todos queden con 10 dígitos.
    assert limpio["telefono"].str.fullmatch(r"3\d{9}").all()


def test_tc_emp_l01_010_activa_booleana(limpio, crudo):
    assert set(limpio["activa"]) == {True, False}
    assert limpio["activa"].isna().sum() == 0
    assert crudo["activa"].isin(["SI", "No", "1", "0"]).any()


def test_tc_emp_l01_011_contactos_rellenados(limpio, crudo):
    assert limpio["contacto"].isna().sum() == 0
    assert (limpio["contacto"] == "Sin contacto").sum() == crudo.drop_duplicates()["contacto"].isna().sum()


def test_tc_emp_l01_012_columna_correo_valido(limpio):
    assert limpio["correo_valido"].dtype == bool
    assert (limpio["correo_valido"] == limpio["correo"].str.contains("@")).all()
    assert (~limpio["correo_valido"]).mean() == pytest.approx(0.06, abs=0.02)


# ---------------------------------------------------------------- Q01 Consultas

def test_tc_emp_q01_003_consulta_1_activas(pipeline, limpio):
    activas = pipeline["consultas"][0]
    assert limpio["activa"].dtype == bool
    assert activas["activa"].all()
    assert len(activas) == limpio["activa"].sum()


def test_tc_emp_q01_004_consulta_2_sector_logistica(pipeline):
    logistica = pipeline["consultas"][1]
    assert len(logistica) > 0
    assert (logistica["sector"] == "Logistica").all()
    assert logistica["nombre"].is_monotonic_increasing


def test_tc_emp_q01_005_consulta_3_conteo_por_sector(pipeline, limpio):
    conteo = pipeline["consultas"][2]
    assert set(conteo.index) == set(limpio["sector"])
    assert conteo.sum() == len(limpio)


def test_tc_emp_q01_006_consulta_4_por_sector_descendente(pipeline):
    por_sector = pipeline["consultas"][3]
    assert por_sector.is_monotonic_decreasing
    assert por_sector.sort_index().equals(pipeline["consultas"][2].sort_index().rename(por_sector.name))


def test_tc_emp_q01_007_consulta_5_activas_inactivas_por_sector(pipeline, limpio):
    tabla = pipeline["consultas"][4]
    assert list(tabla.columns) == [False, True]
    assert not tabla.isna().any().any()
    assert tabla.to_numpy().sum() == len(limpio)


# ---------------------------------------------------------------- G01 Gráficas

def test_tc_emp_g01_003_grafica_1_barras(pipeline, limpio, ejes):
    por_sector, ax = ejes(reporte_empresas.grafica_1, limpio)
    assert (pipeline["base"] / "reportes" / "empresas_grafica_1.png").exists()
    assert [barra.get_height() for barra in ax.patches] == list(por_sector.values)
    assert por_sector.equals(pipeline["consultas"][3])


def test_tc_emp_g01_004_grafica_2_torta(pipeline, limpio, ejes):
    estados, ax = ejes(reporte_empresas.grafica_2, limpio)
    assert (pipeline["base"] / "reportes" / "empresas_grafica_2.png").exists()
    assert len(ax.patches) == 2
    assert any(texto.get_text().endswith("%") for texto in ax.texts)
    assert estados["Activa"] == limpio["activa"].sum()


def test_tc_emp_g01_005_grafica_3_barras_apiladas(pipeline, limpio, ejes):
    tabla, ax = ejes(reporte_empresas.grafica_3, limpio)
    assert (pipeline["base"] / "reportes" / "empresas_grafica_3.png").exists()
    sectores = len(tabla)
    inactivas, activas = ax.patches[:sectores], ax.patches[sectores:]
    # Apiladas: cada barra de activas empieza donde termina la de inactivas del mismo sector.
    assert [barra.get_y() for barra in activas] == [barra.get_height() for barra in inactivas]
    assert tabla.equals(pipeline["consultas"][4])


def test_tc_emp_g01_009_conclusiones_impresas(pipeline, limpio):
    salida = pipeline["salida"]["reporte"]
    conclusiones = salida[salida.index("=== Conclusiones ==="):]
    por_sector = limpio["sector"].value_counts()
    assert f"es {por_sector.idxmax()} ({por_sector.max()} empresas)" in conclusiones
    assert f"El {(~limpio['activa']).mean() * 100:.1f}% de las empresas está inactivo" in conclusiones
    assert f"Aparecieron {(~limpio['correo_valido']).sum()} correos inválidos" in conclusiones
