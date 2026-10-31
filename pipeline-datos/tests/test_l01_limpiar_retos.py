"""E4-RET-L01 — Limpieza de retos."""

import hashlib

import pandas as pd
import pytest

from conftest import SRC, assert_proceso_ok, ejecutar_script, leer_fuente
from exportar_retos import exportar
from limpiar_retos import COLUMNAS_OBLIGATORIAS, limpiar
from simular_retos import ESTADOS, IDS_CATEGORIA, IDS_EMPRESA, IDS_PRIORIDAD


@pytest.fixture(scope="module")
def limpio(pipeline):
    return pd.read_csv(
        pipeline["base"] / "data" / "limpio" / "retos_limpio.csv",
        parse_dates=["fecha_inicio", "fecha_fin"],
    )


@pytest.fixture(scope="module")
def crudo(pipeline):
    return pd.read_csv(pipeline["rutas"]["csv"])


def test_tc_ret_l01_001_script_existe_y_corre(ejecucion_real):
    assert (SRC / "limpiar_retos.py").exists()
    assert_proceso_ok(ejecucion_real["limpiar"])


def test_tc_ret_l01_002_lee_el_archivo_sucio():
    fuente = leer_fuente("limpiar")
    assert "pd.read_csv(entrada)" in fuente
    assert '"data" / "crudo" / "retos_sucio.csv"' in fuente


def test_tc_ret_l01_003_archivo_de_entrada_inexistente(copia_proyecto):
    proceso = ejecutar_script("limpiar", cwd=copia_proyecto)

    assert proceso.returncode == 1
    assert "No existe" in proceso.stderr and "retos_sucio.csv" in proceso.stderr
    assert "Traceback" not in proceso.stderr
    assert not (copia_proyecto / "data" / "limpio").exists()


def test_tc_ret_l01_004_diagnostico_inicial(pipeline):
    salida = pipeline["salida"]["limpiar"]
    inicial = salida[:salida.index("=== Fechas ===")]
    assert inicial.startswith("=== Diagnóstico inicial ===")
    assert "(525, 9)" in inicial
    assert "Data columns" in inicial  # df.info()
    assert "descripcion" in inicial  # df.isna().sum()
    assert "Duplicados exactos: 25" in inicial


def test_tc_ret_l01_005_sin_duplicados_exactos(limpio):
    assert limpio.duplicated().sum() == 0


def test_tc_ret_l01_006_fechas_convertidas_a_datetime(limpio, crudo):
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha_inicio"])
    assert pd.api.types.is_datetime64_any_dtype(limpio["fecha_fin"])
    assert limpio["fecha_inicio"].isna().sum() == 0
    assert limpio["fecha_fin"].isna().sum() == crudo.drop_duplicates()["fecha_fin"].isna().sum()


def test_tc_ret_l01_007_interpreta_dd_mm_yyyy_e_iso(tmp_path):
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
    assert invalidas / len(limpio) == pytest.approx(0.05, abs=0.03)
    assert invalidas == (limpio["fecha_fin"] < limpio["fecha_inicio"]).sum()
    assert f"Retos con fecha de fin anterior a la de inicio: {invalidas}" in pipeline["salida"]["limpiar"]


def test_tc_ret_l01_012_nulos_antes_y_despues(pipeline):
    salida = pipeline["salida"]["limpiar"]
    tabla = salida[salida.index("=== Nulos antes y después ==="):salida.index("=== Diagnóstico final ===")]
    assert "antes" in tabla and "despues" in tabla
    assert any(linea.split()[:3] == ["descripcion", "66", "0"] or linea.startswith("descripcion")
               for linea in tabla.splitlines())


def test_tc_ret_l01_013_diagnostico_final_y_filas_eliminadas(pipeline):
    salida = pipeline["salida"]["limpiar"]
    final = salida[salida.index("=== Diagnóstico final ==="):]
    assert f"({len(pipeline['limpio'])}, 11)" in final
    assert "fecha_valida" in final  # df.isna().sum()
    assert f"Filas eliminadas: {525 - len(pipeline['limpio'])}" in final


def test_tc_ret_l01_014_archivo_limpio_generado(pipeline):
    ruta = pipeline["base"] / "data" / "limpio" / "retos_limpio.csv"
    assert ruta.exists()
    ruta.read_text(encoding="utf-8")
    assert "Unnamed: 0" not in pd.read_csv(ruta).columns


def test_tc_ret_l01_015_idempotencia(tmp_path, capsys):
    exportar(tmp_path)
    ruta = tmp_path / "data" / "limpio" / "retos_limpio.csv"

    limpiar(tmp_path)
    primero = hashlib.sha256(ruta.read_bytes()).hexdigest()
    limpiar(tmp_path)

    assert hashlib.sha256(ruta.read_bytes()).hexdigest() == primero


def test_tc_ret_l01_016_sin_nulos_en_obligatorias(limpio):
    # Obligatorias: todas menos fecha_fin y duracion_dias (un reto puede no tener fecha de cierre).
    assert limpio[COLUMNAS_OBLIGATORIAS].isna().sum().sum() == 0
