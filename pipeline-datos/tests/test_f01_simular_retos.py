"""E4-RET-F01 — Simulación de retos con Faker."""

import hashlib
import inspect
import re
import subprocess
import sys
import uuid
from datetime import date

import pandas as pd
import pytest

import simular_retos
from conftest import RAIZ, SRC, assert_proceso_ok, leer_fuente
from simular_retos import ESTADOS, IDS_CATEGORIA, IDS_EMPRESA, IDS_PRIORIDAD, generar_retos

TOLERANCIA = 0.03  # ±3 p.p. (supuesto de la matriz)


@pytest.fixture(scope="module")
def df():
    return generar_retos()


def fechas_inicio(df):
    return pd.to_datetime(df["fecha_inicio"], format="mixed", dayfirst=True)


def test_tc_ret_f01_001_script_existe_y_corre(ejecucion_real):
    assert (SRC / "simular_retos.py").exists()
    assert_proceso_ok(ejecucion_real["simular"])


def test_tc_ret_f01_002_constantes_al_inicio():
    fuente = leer_fuente("simular")
    primera_funcion = fuente.index("\ndef ")
    for constante in ["ESTADOS", "IDS_EMPRESA", "IDS_CATEGORIA", "IDS_PRIORIDAD"]:
        assert fuente.index(f"\n{constante} = ") < primera_funcion
    for ids in (IDS_EMPRESA, IDS_CATEGORIA, IDS_PRIORIDAD):
        assert all(uuid.UUID(valor) for valor in ids)


def test_tc_ret_f01_003_columnas_y_orden(df):
    assert list(df.columns) == [
        "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
        "estado", "id_empresa", "id_categoria", "id_prioridad",
    ]


def test_tc_ret_f01_004_cantidad_de_filas(df):
    # Criterio usado: 500 filas base + 5% de duplicados exactos.
    assert len(df) == 525
    assert len(df.drop_duplicates()) == 500


def test_tc_ret_f01_005_id_es_uuid_v4(df):
    assert all(uuid.UUID(valor).version == 4 for valor in df["id"])


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
    validas = duracion[duracion >= 0]
    assert validas.between(15, 180).all()


def test_tc_ret_f01_010_estado_pertenece_a_estados(df):
    normalizado = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    assert normalizado.isin(ESTADOS).all()


def test_tc_ret_f01_011_fk_id_empresa(df):
    assert df["id_empresa"].isin(IDS_EMPRESA).all()
    assert (df["id_empresa"].value_counts() > 1).all()


def test_tc_ret_f01_012_fk_id_categoria(df):
    assert df["id_categoria"].isin(IDS_CATEGORIA).all()


def test_tc_ret_f01_013_fk_id_prioridad(df):
    assert df["id_prioridad"].isin(IDS_PRIORIDAD).all()


def test_tc_ret_f01_014_semilla_fija():
    fuente = leer_fuente("simular")
    assert simular_retos.SEMILLA == 42
    assert "Faker.seed(SEMILLA)" in fuente
    assert "random.seed(SEMILLA)" in fuente
    assert 'Faker("es_CO")' in fuente


def test_tc_ret_f01_015_ejecuciones_repetidas_iguales():
    codigo = (
        "import hashlib, sys; sys.path.insert(0, 'src'); from simular_retos import generar_retos; "
        "print(hashlib.sha256(generar_retos().to_csv(index=False).encode()).hexdigest())"
    )
    hashes = {
        subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True, check=True).stdout
        for _ in range(2)
    }
    assert len(hashes) == 1
    assert hashes == {hashlib.sha256(generar_retos().to_csv(index=False).encode()).hexdigest() + "\n"}


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


def test_tc_ret_f01_022_duplicados_exactos(df):
    assert df.duplicated().sum() == pytest.approx(25, abs=2)


def test_tc_ret_f01_023_fk_agrupables(df):
    grupos = df.groupby("id_empresa").size()
    assert len(grupos) == len(IDS_EMPRESA)
    assert (grupos > 1).all()


def test_tc_ret_f01_024_generar_retos_devuelve_dataframe():
    assert inspect.signature(generar_retos).parameters["n"].default == 500
    pequeno = generar_retos(n=20)
    assert isinstance(pequeno, pd.DataFrame)
    assert len(pequeno.drop_duplicates()) == 20


def test_tc_ret_f01_025_import_no_ejecuta_main(tmp_path):
    proceso = subprocess.run(
        [sys.executable, "-c", f"import sys; sys.path.insert(0, r'{SRC}'); import simular_retos"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert proceso.returncode == 0, proceso.stderr
    assert proceso.stdout == ""
    assert list(tmp_path.iterdir()) == []


def test_tc_ret_f01_026_main_imprime_diagnostico(ejecucion_real):
    salida = ejecucion_real["simular"].stdout
    assert "(525, 9)" in salida
    assert "id_prioridad" in salida  # df.head()
    nulos = dict(re.findall(r"^(descripcion|fecha_fin)\s+(\d+)$", salida, re.MULTILINE))
    assert int(nulos["descripcion"]) > 0
    assert int(nulos["fecha_fin"]) > 0
