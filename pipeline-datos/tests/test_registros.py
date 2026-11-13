"""Casos propios de la tabla `registros` (E4-REG). Los casos comunes están en test_comunes.py."""

import pandas as pd
import pytest

import consultas_registros
import reporte_registros
from limpiar_registros import PAR, limpiar
from simular_registros import ESTADOS, IDS_RETO, IDS_USUARIO, generar_registros

TOLERANCIA = 0.03


@pytest.fixture(scope="module")
def df():
    return generar_registros()


@pytest.fixture(scope="module")
def pipeline(pipelines):
    return pipelines("registros")


@pytest.fixture(scope="module")
def limpio(pipeline):
    return consultas_registros.cargar(pipeline["base"])


@pytest.fixture(scope="module")
def crudo(pipeline):
    return pd.read_csv(pipeline["rutas"]["csv"])


def fechas(df):
    return pd.to_datetime(df["fecha_registro"], format="mixed", dayfirst=True)


# ---------------------------------------------------------------- F01 Simulación

def test_tc_reg_f01_006_rango_fecha_registro(df):
    ahora = pd.Timestamp.now()
    # Faker toma "-1y" como 365,25 días, por eso se admite un día más que el año calendario.
    assert fechas(df).min() >= ahora - pd.Timedelta(days=366)
    assert fechas(df).max() <= ahora


def test_tc_reg_f01_007_observacion_es_frase(df):
    observaciones = df["observacion"].dropna()
    assert observaciones.str.endswith(".").all()
    assert 7 <= observaciones.str.split().str.len().mean() <= 13


def test_tc_reg_f01_008_estado_pertenece_a_estados(df):
    assert df["estado"].str.strip().str.upper().str.replace(" ", "_").isin(ESTADOS).all()


def test_tc_reg_f01_009_fk_id_usuario(df):
    assert df["id_usuario"].isin(IDS_USUARIO).all()


def test_tc_reg_f01_010_fk_id_reto(df):
    assert df["id_reto"].isin(IDS_RETO).all()
    assert (df["id_reto"].value_counts() > 1).all()


def test_tc_reg_f01_013_formatos_mezclados_fecha_registro(df):
    iso = df["fecha_registro"].str.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    latino = df["fecha_registro"].str.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}")
    assert iso.any() and latino.any()
    assert (iso | latino).all()


def test_tc_reg_f01_014_nulos_en_observacion(df):
    assert df["observacion"].isna().mean() == pytest.approx(0.20, abs=TOLERANCIA)


def test_tc_reg_f01_015_variantes_de_estado(df):
    valores = set(df["estado"])
    assert any(v != v.strip() for v in valores), "Falta la variante con espacios al borde"
    assert any(v.strip().islower() for v in valores), "Falta la variante en minúscula"
    assert any(" " in v.strip() for v in valores), "Falta la variante con espacio en vez de _"


def test_tc_reg_f01_016_pares_usuario_reto_repetidos(df):
    base = df.drop_duplicates()
    repetidos = base.duplicated(subset=PAR)
    assert repetidos.mean() == pytest.approx(0.10, abs=TOLERANCIA)
    assert base["id"].is_unique, "Las inscripciones dobles deben tener id distinto"


# ---------------------------------------------------------------- L01 Limpieza

def test_tc_reg_l01_006_fecha_registro_a_datetime(limpio):
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha_registro"])
    assert limpio["fecha_registro"].isna().sum() == 0


def test_tc_reg_l01_007_interpreta_ambos_formatos(tmp_path, capsys):
    fila = {"observacion": "Ok.", "estado": "INSCRITO", "id_reto": IDS_RETO[0]}
    (tmp_path / "data" / "crudo").mkdir(parents=True)
    pd.DataFrame([
        {**fila, "id": "a", "id_usuario": IDS_USUARIO[0], "fecha_registro": "15/03/2026 14:30"},
        {**fila, "id": "b", "id_usuario": IDS_USUARIO[1], "fecha_registro": "2026-03-15 14:30:00"},
    ]).to_csv(tmp_path / "data" / "crudo" / "registros_sucio.csv", index=False)

    df = limpiar(tmp_path)

    assert (df["fecha_registro"] == pd.Timestamp(2026, 3, 15, 14, 30)).all()


def test_tc_reg_l01_008_estados_unificados(limpio):
    assert set(limpio["estado"]) == set(ESTADOS)


def test_tc_reg_l01_009_observaciones_rellenadas(limpio):
    assert limpio["observacion"].isna().sum() == 0
    assert (limpio["observacion"] == "Sin observacion").any()


def test_tc_reg_l01_010_reporte_de_participaciones_repetidas(pipeline, crudo):
    esperado = crudo.drop_duplicates().duplicated(subset=PAR, keep=False).sum()
    assert f"Participaciones repetidas (mismo usuario en el mismo reto): {esperado}" in pipeline["salida"]["limpiar"]


def test_tc_reg_l01_011_par_usuario_reto_unico(limpio):
    assert limpio.duplicated(subset=PAR).sum() == 0


def test_tc_reg_l01_012_columna_mes(limpio):
    assert limpio["mes"].str.fullmatch(r"\d{4}-\d{2}").all()
    assert (limpio["mes"] == limpio["fecha_registro"].dt.strftime("%Y-%m")).all()


# ---------------------------------------------------------------- Q01 Consultas

def test_tc_reg_q01_003_consulta_1_finalizados(pipeline, limpio):
    finalizados = pipeline["consultas"][0]
    assert (finalizados["estado"] == "FINALIZADO").all()
    assert len(finalizados) == limpio["estado"].value_counts()["FINALIZADO"]


def test_tc_reg_q01_004_consulta_2_repetidos(pipeline):
    # Sobre el archivo limpio da 0 filas porque L01 ya las eliminó (ver Hallazgos 13 y 14).
    assert len(pipeline["consultas"][1]) == 0
    assert "Detectadas durante la limpieza:" in pipeline["salida"]["consultas"]


def test_tc_reg_q01_005_consulta_3_por_estado(pipeline, limpio):
    conteo = pipeline["consultas"][2]
    assert set(conteo.index) == set(ESTADOS)
    assert conteo.sum() == len(limpio)


def test_tc_reg_q01_006_consulta_4_top_10_retos(pipeline, limpio):
    top = pipeline["consultas"][3]
    assert len(top) == 10
    assert top.is_monotonic_decreasing
    assert top.iloc[0] == limpio["id_reto"].value_counts().max()


def test_tc_reg_q01_007_consulta_5_por_mes(pipeline, limpio):
    por_mes = pipeline["consultas"][4]
    assert por_mes.index.is_monotonic_increasing
    assert por_mes.sum() == len(limpio)


# ---------------------------------------------------------------- G01 Gráficas

def test_tc_reg_g01_003_grafica_1_barras(pipeline, limpio, ejes):
    conteo, ax = ejes(reporte_registros.grafica_1, limpio)
    assert (pipeline["base"] / "reportes" / "registros_grafica_1.png").exists()
    assert [barra.get_height() for barra in ax.patches] == list(conteo.values)
    assert conteo.equals(pipeline["consultas"][2])


def test_tc_reg_g01_004_grafica_2_linea(pipeline, limpio, ejes):
    por_mes, ax = ejes(reporte_registros.grafica_2, limpio)
    assert (pipeline["base"] / "reportes" / "registros_grafica_2.png").exists()
    assert len(ax.lines) == 1 and ax.lines[0].get_marker() == "o"
    assert list(ax.lines[0].get_ydata()) == list(por_mes.values)
    assert por_mes.equals(pipeline["consultas"][4])


def test_tc_reg_g01_005_grafica_3_barras_horizontales(pipeline, limpio, ejes):
    top, ax = ejes(reporte_registros.grafica_3, limpio)
    assert (pipeline["base"] / "reportes" / "registros_grafica_3.png").exists()
    assert [barra.get_width() for barra in ax.patches] == list(top.values)
    assert top.equals(pipeline["consultas"][3])


def test_tc_reg_g01_009_conclusiones_impresas(pipeline, limpio):
    salida = pipeline["salida"]["reporte"]
    conclusiones = salida[salida.index("=== Conclusiones ==="):]
    top = limpio["id_reto"].value_counts()
    por_mes = limpio.groupby("mes")["id"].count()
    anio, mes = map(int, por_mes.idxmax().split("-"))
    repetidos = pd.read_csv(pipeline["base"] / "data" / "limpio" / "registros_repetidos.csv")
    duplicadas = len(repetidos) - repetidos[PAR].drop_duplicates().shape[0]

    assert f"{top.idxmax()} con {top.max()} participantes" in conclusiones
    assert f"{reporte_registros.MESES[mes - 1]} de {anio} ({por_mes.max()} participaciones)" in conclusiones
    assert f"Se encontraron {duplicadas} inscripciones duplicadas" in conclusiones
    assert "409" in conclusiones
