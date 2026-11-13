"""Casos propios de la tabla `retos` (E4-RET). Los casos comunes están en test_comunes.py."""

from datetime import date

import pandas as pd
import pytest

import consultas_retos
import reporte_retos
from limpiar_retos import limpiar
from simular_retos import ESTADOS, IDS_CATEGORIA, IDS_EMPRESA, IDS_PRIORIDAD, generar_retos

TOLERANCIA = 0.03  # ±3 p.p. (supuesto de la matriz)


@pytest.fixture(scope="module")
def df():
    return generar_retos()


@pytest.fixture(scope="module")
def pipeline(pipelines):
    return pipelines("retos")


@pytest.fixture(scope="module")
def limpio(pipeline):
    return consultas_retos.cargar(pipeline["base"])


@pytest.fixture(scope="module")
def crudo(pipeline):
    return pd.read_csv(pipeline["rutas"]["csv"])


def fechas_inicio(df):
    return pd.to_datetime(df["fecha_inicio"], format="mixed", dayfirst=True)


# ---------------------------------------------------------------- F01 Simulación

def test_tc_ret_f01_006_nombre_sin_punto_final(df):
    nombres = df["nombre"].str.strip()
    assert not nombres.str.endswith(".").any()
    assert 4 <= nombres.str.split().str.len().mean() <= 8


def test_tc_ret_f01_007_descripcion_es_frase(df):
    descripciones = df["descripcion"].dropna()
    assert descripciones.str.endswith(".").all()
    assert 9 <= descripciones.str.split().str.len().mean() <= 15


def test_tc_ret_f01_008_rango_fecha_inicio(df):
    hoy = pd.Timestamp(date.today())
    fechas = fechas_inicio(df)
    # Faker toma "-1y" como 365,25 días, por eso se admite un día más que el año calendario.
    assert fechas.min() >= hoy - pd.Timedelta(days=366)
    assert fechas.max() <= hoy + pd.DateOffset(months=3)
    assert fechas.max() > hoy, "Debe haber retos que empiezan en el futuro (+3 meses)"


def test_tc_ret_f01_009_duracion_valida_en_filas_no_ensuciadas(df):
    duracion = (pd.to_datetime(df["fecha_fin"]) - fechas_inicio(df)).dt.days
    assert duracion[duracion >= 0].between(15, 180).all()


def test_tc_ret_f01_010_estado_pertenece_a_estados(df):
    assert df["estado"].str.strip().str.upper().str.replace(" ", "_").isin(ESTADOS).all()


def test_tc_ret_f01_011_fk_id_empresa(df):
    assert df["id_empresa"].isin(IDS_EMPRESA).all()
    assert (df["id_empresa"].value_counts() > 1).all()


def test_tc_ret_f01_012_fk_id_categoria(df):
    assert df["id_categoria"].isin(IDS_CATEGORIA).all()


def test_tc_ret_f01_013_fk_id_prioridad(df):
    assert df["id_prioridad"].isin(IDS_PRIORIDAD).all()


def test_tc_ret_f01_016_espacios_sobrantes_en_nombre(df):
    assert (df["nombre"] != df["nombre"].str.strip()).mean() == pytest.approx(0.10, abs=TOLERANCIA)


def test_tc_ret_f01_017_nulos_en_descripcion(df):
    assert df["descripcion"].isna().mean() == pytest.approx(0.12, abs=TOLERANCIA)


def test_tc_ret_f01_018_formatos_mezclados_fecha_inicio(df):
    iso = df["fecha_inicio"].str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    latino = df["fecha_inicio"].str.fullmatch(r"\d{2}/\d{2}/\d{4}")
    assert iso.any() and latino.any()
    assert (iso | latino).all()


def test_tc_ret_f01_019_nulos_en_fecha_fin(df):
    assert df["fecha_fin"].isna().mean() == pytest.approx(0.08, abs=TOLERANCIA)


def test_tc_ret_f01_020_fecha_fin_anterior_a_inicio(df):
    invertidas = pd.to_datetime(df["fecha_fin"]) < fechas_inicio(df)
    assert invertidas.mean() == pytest.approx(0.05, abs=TOLERANCIA)


def test_tc_ret_f01_021_variantes_de_estado(df):
    valores = set(df["estado"])
    assert any(v != v.strip() for v in valores), "Falta la variante con espacios al borde"
    assert any(v.strip().islower() for v in valores), "Falta la variante en minúscula"
    assert any(" " in v.strip() for v in valores), "Falta la variante con espacio en vez de _"


def test_tc_ret_f01_023_fk_agrupables(df):
    grupos = df.groupby("id_empresa").size()
    assert len(grupos) == len(IDS_EMPRESA)
    assert (grupos > 1).all()


# ---------------------------------------------------------------- L01 Limpieza

def test_tc_ret_l01_006_fechas_convertidas_a_datetime(limpio, crudo):
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha_inicio"])
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha_fin"])
    assert limpio["fecha_inicio"].isna().sum() == 0
    assert limpio["fecha_fin"].isna().sum() == crudo.drop_duplicates()["fecha_fin"].isna().sum()


def test_tc_ret_l01_007_interpreta_dd_mm_yyyy_e_iso(tmp_path, capsys):
    fila = {
        "nombre": "Reto", "descripcion": "Descripción.", "fecha_fin": "2026-04-01", "estado": "ABIERTO",
        "id_empresa": IDS_EMPRESA[0], "id_categoria": IDS_CATEGORIA[0], "id_prioridad": IDS_PRIORIDAD[0],
    }
    (tmp_path / "data" / "crudo").mkdir(parents=True)
    pd.DataFrame([
        {**fila, "id": "a", "fecha_inicio": "02/03/2026"},
        {**fila, "id": "b", "fecha_inicio": "2026-03-02"},
    ]).to_csv(tmp_path / "data" / "crudo" / "retos_sucio.csv", index=False)

    df = limpiar(tmp_path)

    assert (df["fecha_inicio"] == pd.Timestamp(2026, 3, 2)).all()


def test_tc_ret_l01_008_estados_unificados(limpio):
    assert set(limpio["estado"]) == set(ESTADOS)


def test_tc_ret_l01_009_descripciones_rellenadas(limpio, crudo):
    assert limpio["descripcion"].isna().sum() == 0
    assert (limpio["descripcion"] == "Sin descripcion").sum() == crudo.drop_duplicates()["descripcion"].isna().sum()


def test_tc_ret_l01_010_columna_duracion_dias(limpio):
    esperado = (limpio["fecha_fin"] - limpio["fecha_inicio"]).dt.days
    con_fin = limpio["fecha_fin"].notna()
    assert (limpio.loc[con_fin, "duracion_dias"] == esperado[con_fin]).all()
    assert limpio.loc[~con_fin, "duracion_dias"].isna().all()
    invertidas = limpio["fecha_fin"] < limpio["fecha_inicio"]
    assert (limpio.loc[invertidas, "duracion_dias"] < 0).all()


def test_tc_ret_l01_011_fecha_valida_y_reporte(limpio, pipeline):
    assert limpio["fecha_valida"].dtype == bool
    invalidas = (~limpio["fecha_valida"]).sum()
    assert invalidas / len(limpio) == pytest.approx(0.05, abs=TOLERANCIA)
    assert invalidas == (limpio["fecha_fin"] < limpio["fecha_inicio"]).sum()
    assert f"Retos con fecha de fin anterior a la de inicio: {invalidas}" in pipeline["salida"]["limpiar"]


def test_tc_ret_l01_012_nulos_antes_y_despues(pipeline, crudo):
    salida = pipeline["salida"]["limpiar"]
    tabla = salida[salida.index("=== Nulos antes y después ==="):salida.index("=== Diagnóstico final ===")]
    assert "antes" in tabla and "despues" in tabla
    assert f"descripcion {crudo['descripcion'].isna().sum()} 0" in " ".join(tabla.split())


# ---------------------------------------------------------------- Q01 Consultas

def test_tc_ret_q01_003_consulta_1_en_curso(pipeline, limpio):
    en_curso = pipeline["consultas"][0]
    assert (en_curso["estado"] == "EN_CURSO").all()
    assert len(en_curso) == limpio["estado"].value_counts()["EN_CURSO"]
    assert len(pd.read_csv(pipeline["base"] / "data" / "limpio" / "retos_consulta_1.csv")) == len(en_curso)


def test_tc_ret_q01_004_consulta_2_diez_mas_largos(pipeline, limpio):
    largos = pipeline["consultas"][1]
    assert largos.shape == (10, 3)
    assert list(largos.columns) == ["nombre", "duracion_dias", "estado"]
    assert largos["duracion_dias"].is_monotonic_decreasing
    assert largos["duracion_dias"].iloc[0] == limpio["duracion_dias"].max()


def test_tc_ret_q01_005_consulta_3_por_estado(pipeline, limpio):
    conteo = pipeline["consultas"][2]
    assert set(conteo.index) == set(limpio["estado"])
    assert conteo.sum() == len(limpio)


def test_tc_ret_q01_006_consulta_4_groupby_duracion(pipeline, limpio):
    resumen = pipeline["consultas"][3]
    assert list(resumen.columns) == ["count", "mean", "min", "max"]
    for estado, grupo in limpio.groupby("estado"):
        assert resumen.loc[estado, "count"] == grupo["duracion_dias"].count()
        assert resumen.loc[estado, "mean"] == pytest.approx(grupo["duracion_dias"].mean())
        assert resumen.loc[estado, "min"] == grupo["duracion_dias"].min()
        assert resumen.loc[estado, "max"] == grupo["duracion_dias"].max()


def test_tc_ret_q01_007_consulta_5_por_mes(pipeline, limpio):
    por_mes = pipeline["consultas"][4]
    assert isinstance(por_mes.index, pd.PeriodIndex) and por_mes.index.freqstr == "M"
    assert por_mes.index.is_monotonic_increasing
    assert por_mes.sum() == len(limpio)


# ---------------------------------------------------------------- G01 Gráficas

def test_tc_ret_g01_003_grafica_1_barras(pipeline, limpio, ejes):
    conteo, ax = ejes(reporte_retos.grafica_1, limpio)
    assert (pipeline["base"] / "reportes" / "retos_grafica_1.png").exists()
    assert [barra.get_height() for barra in ax.patches] == list(conteo.values)
    assert conteo.equals(pipeline["consultas"][2])


def test_tc_ret_g01_004_grafica_2_linea(pipeline, limpio, ejes):
    por_mes, ax = ejes(reporte_retos.grafica_2, limpio)
    assert (pipeline["base"] / "reportes" / "retos_grafica_2.png").exists()
    assert len(ax.lines) == 1 and ax.lines[0].get_marker() == "o"
    assert list(ax.lines[0].get_ydata()) == list(por_mes.values)
    assert por_mes.equals(pipeline["consultas"][4])


def test_tc_ret_g01_005_grafica_3_histograma(pipeline, limpio, ejes):
    duraciones, ax = ejes(reporte_retos.grafica_3, limpio)
    assert (pipeline["base"] / "reportes" / "retos_grafica_3.png").exists()
    assert len(ax.patches) == 20
    assert sum(barra.get_height() for barra in ax.patches) == duraciones.count()


def test_tc_ret_g01_009_conclusiones_impresas(pipeline, limpio):
    salida = pipeline["salida"]["reporte"]
    conclusiones = salida[salida.index("=== Conclusiones ==="):]
    mes_pico = limpio.groupby(limpio["fecha_inicio"].dt.to_period("M"))["id"].count().idxmax()

    assert f"{reporte_retos.MESES[mes_pico.month - 1]} de {mes_pico.year}" in conclusiones
    assert "Puede deberse" in conclusiones
    for estado, dias in limpio.groupby("estado")["duracion_dias"].mean().round(1).items():
        assert f"{estado}: {dias} días" in conclusiones
    invertidas = (limpio["fecha_fin"] < limpio["fecha_inicio"]).sum()
    assert f"{invertidas} retos tenían la fecha de fin antes que la de inicio" in conclusiones
