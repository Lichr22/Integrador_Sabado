"""E4-RET-X01 — Exportación de retos a CSV, Excel y JSON."""

import hashlib
import json
import subprocess
from importlib.metadata import version

import pandas as pd

from conftest import RAIZ, SRC, assert_proceso_ok, ejecutar_script, leer_fuente
from exportar_retos import exportar
from simular_retos import generar_retos


def leer_los_tres(rutas):
    return {
        "csv": pd.read_csv(rutas["csv"]),
        "xlsx": pd.read_excel(rutas["xlsx"], sheet_name="retos"),
        "json": pd.read_json(rutas["json"], orient="records", dtype=False),
    }


def sha256(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def test_tc_ret_x01_001_script_existe_y_corre(ejecucion_real):
    assert (SRC / "exportar_retos.py").exists()
    assert_proceso_ok(ejecucion_real["exportar"])


def test_tc_ret_x01_002_reutiliza_generar_por_import():
    fuente = leer_fuente("exportar")
    assert "from simular_retos import generar_retos" in fuente
    assert "Faker" not in fuente and "fake." not in fuente


def test_tc_ret_x01_003_csv_generado(pipeline):
    ruta = pipeline["rutas"]["csv"]
    ruta.read_text(encoding="utf-8")  # falla si no es UTF-8
    df = pd.read_csv(ruta)
    assert "Unnamed: 0" not in df.columns
    assert df.shape == generar_retos().shape


def test_tc_ret_x01_004_excel_generado(pipeline):
    ruta = pipeline["rutas"]["xlsx"]
    assert pd.ExcelFile(ruta).sheet_names == ["retos"]
    df = pd.read_excel(ruta, sheet_name="retos")
    assert "Unnamed: 0" not in df.columns
    assert df.shape == pd.read_csv(pipeline["rutas"]["csv"]).shape


def test_tc_ret_x01_005_json_generado(pipeline):
    texto = pipeline["rutas"]["json"].read_text(encoding="utf-8")
    registros = json.loads(texto)
    assert isinstance(registros, list) and isinstance(registros[0], dict)
    assert "\n  " in texto, "El JSON debe estar indentado"
    assert "\\u00" not in texto, "Las tildes no deben quedar escapadas"
    assert len(registros) == len(generar_retos())


def test_tc_ret_x01_006_consistencia_entre_formatos(pipeline):
    tablas = leer_los_tres(pipeline["rutas"])
    csv = tablas["csv"]
    for nombre, tabla in tablas.items():
        assert tabla.shape == csv.shape, nombre
        assert list(tabla.columns) == list(csv.columns), nombre
        assert tabla.isna().sum().equals(csv.isna().sum()), nombre
        assert tabla.duplicated().sum() == csv.duplicated().sum(), nombre


def test_tc_ret_x01_007_crea_carpeta_inexistente(tmp_path):
    assert not (tmp_path / "data").exists()

    rutas = exportar(tmp_path)

    assert all(ruta.exists() for ruta in rutas.values())


def test_tc_ret_x01_008_carpeta_ya_existente(copia_proyecto):
    primera = ejecutar_script("exportar", cwd=copia_proyecto)
    carpeta = copia_proyecto / "data" / "crudo"
    hashes = {nombre: sha256(carpeta / f"retos_sucio.{nombre}") for nombre in ("csv", "json")}
    excel = pd.read_excel(carpeta / "retos_sucio.xlsx")

    segunda = ejecutar_script("exportar", cwd=copia_proyecto)

    assert_proceso_ok(primera)
    assert_proceso_ok(segunda)
    assert hashes == {nombre: sha256(carpeta / f"retos_sucio.{nombre}") for nombre in ("csv", "json")}
    assert excel.equals(pd.read_excel(carpeta / "retos_sucio.xlsx"))


def test_tc_ret_x01_009_salida_por_consola(pipeline):
    lineas = pipeline["salida"]["exportar"].strip().splitlines()
    assert lineas == [
        "data/crudo/retos_sucio.csv -> (525, 9)",
        "data/crudo/retos_sucio.xlsx -> (525, 9)",
        "data/crudo/retos_sucio.json -> (525, 9)",
    ]


def test_tc_ret_x01_010_requirements_completo():
    requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "pandas>=2,<3" in requisitos
    for paquete in ("faker", "openpyxl", "matplotlib"):
        assert paquete in requisitos
    assert version("pandas").startswith("2.")


def test_tc_ret_x01_011_archivos_versionados_o_documentados():
    versionados = subprocess.run(
        ["git", "ls-files", "data/crudo"], cwd=RAIZ, capture_output=True, text=True,
    ).stdout.split()
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    documentado = "python src/exportar_retos.py" in readme and "data/crudo" in readme
    assert len(versionados) == 3 or documentado
