"""Casos que se repiten igual en las 5 tablas (mismo criterio, distinto archivo).

Cada prueba corre una vez por tabla y el id de la variante es el ID del caso en la matriz,
por ejemplo `test_csv_generado[TC-CAT-X01-003]`.
"""

import hashlib
import inspect
import json
import re
import subprocess
import sys
import uuid
from importlib.metadata import version

import matplotlib.image as mpimg
import pandas as pd
import pytest

from conftest import (
    RAIZ, SRC, TABLAS, assert_proceso_ok, casos, casos_f01, ejecutar_script, generar, leer_fuente, modulo,
)


def sha256(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def total_filas(tabla):
    return TABLAS[tabla]["n"] + TABLAS[tabla]["duplicados"]


def es_uuid(valor):
    return uuid.UUID(valor).version == 4


def validar_constantes(tabla, simular):
    if tabla == "categorias":
        assert len(simular.CATEGORIAS) == 10
    elif tabla == "prioridades":
        assert len(simular.NIVELES) == 5
        assert sorted(simular.NIVELES.values()) == [1, 2, 3, 4, 5]
        assert sorted(simular.DIAS) == [1, 2, 3, 4, 5]
    elif tabla == "retos":
        assert all(es_uuid(v) for v in simular.IDS_EMPRESA + simular.IDS_CATEGORIA + simular.IDS_PRIORIDAD)
    elif tabla == "registros":
        assert all(es_uuid(v) for v in simular.IDS_USUARIO + simular.IDS_RETO)
    elif tabla == "empresas":
        assert len(simular.SECTORES) > 1


# ---------------------------------------------------------------- F01 Simulación

@casos_f01("corre")
def test_script_simular_existe_y_corre(tabla, ejecucion_real):
    assert (SRC / f"simular_{tabla}.py").exists()
    assert_proceso_ok(ejecucion_real[f"simular_{tabla}"])


@casos_f01("constantes")
def test_constantes_al_inicio(tabla):
    fuente = leer_fuente(f"simular_{tabla}")
    primera_funcion = fuente.index("\ndef ")
    for constante in TABLAS[tabla]["constantes"]:
        assert fuente.index(f"\n{constante} = ") < primera_funcion, constante
    validar_constantes(tabla, modulo("simular", tabla))


@casos_f01("columnas")
def test_columnas_y_orden(tabla):
    assert list(generar(tabla).columns) == TABLAS[tabla]["columnas"]


@casos_f01("filas")
def test_cantidad_de_filas(tabla):
    # Criterio usado: N filas base + el % de duplicados exactos encima.
    df = generar(tabla)
    assert len(df) == total_filas(tabla)
    assert len(df.drop_duplicates()) == TABLAS[tabla]["n"]


@casos_f01("uuid")
def test_id_es_uuid_v4(tabla):
    assert generar(tabla)["id"].map(es_uuid).all()


@casos_f01("semilla")
def test_semilla_fija(tabla):
    fuente = leer_fuente(f"simular_{tabla}")
    assert modulo("simular", tabla).SEMILLA == 42
    assert "Faker.seed(SEMILLA)" in fuente
    assert "random.seed(SEMILLA)" in fuente
    assert 'Faker("es_CO")' in fuente


@casos_f01("reproducible")
def test_ejecuciones_repetidas_iguales(tabla):
    codigo = (
        f"import hashlib, sys; sys.path.insert(0, 'src'); from simular_{tabla} import generar_{tabla}; "
        f"print(hashlib.sha256(generar_{tabla}().to_csv(index=False).encode()).hexdigest())"
    )
    hashes = {
        subprocess.run([sys.executable, "-c", codigo], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()
        for _ in range(2)
    }
    assert hashes == {hashlib.sha256(generar(tabla).to_csv(index=False).encode()).hexdigest()}


@casos_f01("duplicados")
def test_duplicados_exactos(tabla):
    assert generar(tabla).duplicated().sum() == pytest.approx(TABLAS[tabla]["duplicados"], abs=2)


@casos_f01("generar")
def test_generar_devuelve_dataframe(tabla):
    funcion = getattr(modulo("simular", tabla), f"generar_{tabla}")
    assert inspect.signature(funcion).parameters["n"].default == TABLAS[tabla]["n"]
    pequeno = funcion(n=20)
    assert isinstance(pequeno, pd.DataFrame)
    assert len(pequeno.drop_duplicates()) == 20


@casos_f01("import")
def test_import_no_ejecuta_main(tabla, tmp_path):
    proceso = subprocess.run(
        [sys.executable, "-c", f"import sys; sys.path.insert(0, r'{SRC}'); import simular_{tabla}"],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert proceso.returncode == 0, proceso.stderr
    assert proceso.stdout == ""
    assert list(tmp_path.iterdir()) == []


@casos_f01("main")
def test_main_imprime_diagnostico(tabla, ejecucion_real):
    salida = ejecucion_real[f"simular_{tabla}"].stdout
    assert f"({total_filas(tabla)}, {len(TABLAS[tabla]['columnas'])})" in salida
    assert TABLAS[tabla]["columnas"][-1] in salida  # df.head() y df.isna().sum()
    for columna in TABLAS[tabla]["ensuciadas"]:
        nulos = re.search(rf"^{columna}\s+(\d+)$", salida, re.MULTILINE)
        assert nulos and int(nulos.group(1)) > 0, columna


# ---------------------------------------------------------------- X01 Exportación

@casos("X01", 1)
def test_script_exportar_existe_y_corre(tabla, ejecucion_real):
    assert (SRC / f"exportar_{tabla}.py").exists()
    assert_proceso_ok(ejecucion_real[f"exportar_{tabla}"])


@casos("X01", 2)
def test_reutiliza_generar_por_import(tabla):
    fuente = leer_fuente(f"exportar_{tabla}")
    assert f"from simular_{tabla} import generar_{tabla}" in fuente
    assert "Faker" not in fuente and "fake." not in fuente


@casos("X01", 3)
def test_csv_generado(tabla, pipelines):
    ruta = pipelines(tabla)["rutas"]["csv"]
    ruta.read_text(encoding="utf-8")  # falla si no es UTF-8
    df = pd.read_csv(ruta)
    assert "Unnamed: 0" not in df.columns
    assert df.shape == generar(tabla).shape


@casos("X01", 4)
def test_excel_generado(tabla, pipelines):
    ruta = pipelines(tabla)["rutas"]["xlsx"]
    assert pd.ExcelFile(ruta).sheet_names == [tabla]
    df = pd.read_excel(ruta, sheet_name=tabla)
    assert "Unnamed: 0" not in df.columns
    assert df.shape == pd.read_csv(pipelines(tabla)["rutas"]["csv"]).shape


@casos("X01", 5)
def test_json_generado(tabla, pipelines):
    texto = pipelines(tabla)["rutas"]["json"].read_text(encoding="utf-8")
    registros = json.loads(texto)
    assert isinstance(registros, list) and isinstance(registros[0], dict)
    assert "\n  " in texto, "El JSON debe estar indentado"
    assert "\\u00" not in texto, "Las tildes no deben quedar escapadas"
    assert len(registros) == total_filas(tabla)


@casos("X01", 6)
def test_consistencia_entre_formatos(tabla, pipelines):
    rutas = pipelines(tabla)["rutas"]
    tablas = {
        "csv": pd.read_csv(rutas["csv"], dtype=str),
        "xlsx": pd.read_excel(rutas["xlsx"], sheet_name=tabla, dtype=str),
        "json": pd.read_json(rutas["json"], orient="records", dtype=False),
    }
    csv = tablas["csv"]
    for formato, df in tablas.items():
        assert df.shape == csv.shape, formato
        assert list(df.columns) == list(csv.columns), formato
        assert df.isna().sum().equals(csv.isna().sum()), formato
        assert df.astype(str).duplicated().sum() == csv.duplicated().sum(), formato


@casos("X01", 7)
def test_crea_carpeta_inexistente(tabla, tmp_path, capsys):
    assert not (tmp_path / "data").exists()

    rutas = modulo("exportar", tabla).exportar(tmp_path)

    assert all(ruta.exists() for ruta in rutas.values())


@casos("X01", 8)
def test_carpeta_ya_existente(tabla, copia_proyecto):
    carpeta = copia_proyecto / "data" / "crudo"
    primera = ejecutar_script(f"exportar_{tabla}", cwd=copia_proyecto)
    hashes = {ext: sha256(carpeta / f"{tabla}_sucio.{ext}") for ext in ("csv", "json")}
    excel = pd.read_excel(carpeta / f"{tabla}_sucio.xlsx")

    segunda = ejecutar_script(f"exportar_{tabla}", cwd=copia_proyecto)

    assert_proceso_ok(primera)
    assert_proceso_ok(segunda)
    assert hashes == {ext: sha256(carpeta / f"{tabla}_sucio.{ext}") for ext in ("csv", "json")}
    assert excel.equals(pd.read_excel(carpeta / f"{tabla}_sucio.xlsx"))


@casos("X01", 9)
def test_salida_por_consola(tabla, pipelines):
    forma = f"({total_filas(tabla)}, {len(TABLAS[tabla]['columnas'])})"
    assert pipelines(tabla)["salida"]["exportar"].strip().splitlines() == [
        f"data/crudo/{tabla}_sucio.{ext} -> {forma}" for ext in ("csv", "xlsx", "json")
    ]


@casos("X01", 10)
def test_requirements_completo(tabla):
    requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "pandas>=2,<3" in requisitos
    for paquete in ("faker", "openpyxl", "matplotlib"):
        assert paquete in requisitos
    assert version("pandas").startswith("2.")


@casos("X01", 11)
def test_archivos_versionados_o_documentados(tabla):
    versionados = subprocess.run(
        ["git", "ls-files", f"data/crudo/{tabla}_sucio.*"], cwd=RAIZ, capture_output=True, text=True,
    ).stdout.split()
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    documentado = f"python src/exportar_{tabla}.py" in readme and "data/crudo" in readme
    assert len(versionados) == 3 or documentado


# ---------------------------------------------------------------- L01 Limpieza

def limpio(tabla, pipelines):
    return pd.read_csv(pipelines(tabla)["base"] / "data" / "limpio" / f"{tabla}_limpio.csv")


def seccion(salida, titulo):
    inicio = salida.index(f"=== {titulo} ===")
    fin = salida.find("\n===", inicio + 1)
    return salida[inicio:fin if fin != -1 else None]


@casos("L01", 1)
def test_script_limpiar_existe_y_corre(tabla, ejecucion_real):
    assert (SRC / f"limpiar_{tabla}.py").exists()
    assert_proceso_ok(ejecucion_real[f"limpiar_{tabla}"])


@casos("L01", 2)
def test_lee_el_archivo_sucio(tabla):
    fuente = leer_fuente(f"limpiar_{tabla}")
    assert "pd.read_csv(entrada" in fuente
    assert f'"data" / "crudo" / "{tabla}_sucio.csv"' in fuente


@casos("L01", 3)
def test_archivo_de_entrada_inexistente(tabla, copia_proyecto):
    proceso = ejecutar_script(f"limpiar_{tabla}", cwd=copia_proyecto)

    assert proceso.returncode == 1
    assert "No existe" in proceso.stderr and f"{tabla}_sucio.csv" in proceso.stderr
    assert "Traceback" not in proceso.stderr
    assert not (copia_proyecto / "data" / "limpio").exists()


@casos("L01", 4)
def test_diagnostico_inicial(tabla, pipelines):
    salida = pipelines(tabla)["salida"]["limpiar"]
    inicial = seccion(salida, "Diagnóstico inicial")
    assert salida.startswith("=== Diagnóstico inicial ===")
    assert f"({total_filas(tabla)}, {len(TABLAS[tabla]['columnas'])})" in inicial
    assert "Data columns" in inicial  # df.info()
    assert TABLAS[tabla]["columnas"][-1] in inicial  # df.isna().sum()
    assert f"Duplicados exactos: {TABLAS[tabla]['duplicados']}" in inicial


@casos("L01", 5)
def test_sin_duplicados_exactos(tabla, pipelines):
    assert limpio(tabla, pipelines).duplicated().sum() == 0


@casos("L01", 13)
def test_diagnostico_final_y_filas_eliminadas(tabla, pipelines):
    df = limpio(tabla, pipelines)
    final = seccion(pipelines(tabla)["salida"]["limpiar"], "Diagnóstico final")
    assert f"({len(df)}, {len(df.columns)})" in final
    assert df.columns[-1] in final  # df.isna().sum()
    assert f"Filas eliminadas: {total_filas(tabla) - len(df)}" in final


@casos("L01", 14)
def test_archivo_limpio_generado(tabla, pipelines):
    ruta = pipelines(tabla)["base"] / "data" / "limpio" / f"{tabla}_limpio.csv"
    assert ruta.exists()
    ruta.read_text(encoding="utf-8")
    assert "Unnamed: 0" not in pd.read_csv(ruta).columns


@casos("L01", 15)
def test_idempotencia(tabla, tmp_path, capsys):
    modulo("exportar", tabla).exportar(tmp_path)
    ruta = tmp_path / "data" / "limpio" / f"{tabla}_limpio.csv"

    modulo("limpiar", tabla).limpiar(tmp_path)
    primero = sha256(ruta)
    modulo("limpiar", tabla).limpiar(tmp_path)

    assert sha256(ruta) == primero


@casos("L01", 16)
def test_sin_nulos_en_obligatorias(tabla, pipelines):
    obligatorias = modulo("limpiar", tabla).COLUMNAS_OBLIGATORIAS
    assert limpio(tabla, pipelines)[obligatorias].isna().sum().sum() == 0


# ---------------------------------------------------------------- Q01 Consultas

@casos("Q01", 1)
def test_script_consultas_existe_y_corre(tabla, ejecucion_real):
    assert (SRC / f"consultas_{tabla}.py").exists()
    assert_proceso_ok(ejecucion_real[f"consultas_{tabla}"])


@casos("Q01", 2)
def test_consultas_lee_el_archivo_limpio(tabla):
    fuente = leer_fuente(f"consultas_{tabla}")
    assert f'"data" / "limpio" / "{tabla}_limpio.csv"' in fuente
    assert "crudo" not in fuente


@casos("Q01", 8)
def test_usa_groupby(tabla):
    assert leer_fuente(f"consultas_{tabla}").count(".groupby(") >= TABLAS[tabla]["groupby_minimo"]


@casos("Q01", 9)
def test_una_funcion_por_consulta(tabla, pipelines):
    consultas = modulo("consultas", tabla)
    salida = pipelines(tabla)["salida"]["consultas"]
    for numero in range(1, 6):
        assert callable(getattr(consultas, f"consulta_{numero}"))
        assert f"Consulta {numero} — ¿" in salida


@casos("Q01", 10)
def test_cinco_archivos_de_consulta(tabla, pipelines):
    for numero in range(1, 6):
        ruta = pipelines(tabla)["base"] / "data" / "limpio" / f"{tabla}_consulta_{numero}.csv"
        assert ruta.exists() and len(pd.read_csv(ruta).columns) > 0, ruta.name


@casos("Q01", 11)
def test_orden_de_salida(tabla, ejecucion_real):
    salida = ejecucion_real[f"consultas_{tabla}"].stdout
    posiciones = [salida.index(f"Consulta {numero} —") for numero in range(1, 6)]
    assert posiciones == sorted(posiciones)


# ---------------------------------------------------------------- G01 Gráficas y reporte

@casos("G01", 1)
def test_script_reporte_existe_y_corre(tabla, ejecucion_real):
    assert (SRC / f"reporte_{tabla}.py").exists()
    assert_proceso_ok(ejecucion_real[f"reporte_{tabla}"])


@casos("G01", 2)
def test_reporte_lee_el_archivo_limpio(tabla):
    fuente = leer_fuente(f"reporte_{tabla}")
    assert f'"data" / "limpio" / "{tabla}_limpio.csv"' in fuente
    assert "crudo" not in fuente


@casos("G01", 6)
def test_titulo_y_ejes_en_cada_grafica(tabla, pipelines, ejes):
    reporte = modulo("reporte", tabla)
    df = reporte.cargar(pipelines(tabla)["base"])
    assert "plt.tight_layout()" in leer_fuente(f"reporte_{tabla}")
    for numero in (1, 2, 3):
        _, ax = ejes(getattr(reporte, f"grafica_{numero}"), df)
        assert ax.get_title() and ax.get_xlabel() and ax.get_ylabel(), f"gráfica {numero}"


@casos("G01", 7)
def test_ejecucion_no_bloqueante(tabla, pipelines):
    fuente = leer_fuente(f"reporte_{tabla}")
    assert "plt.show" not in fuente
    assert "dpi=120" in fuente and "plt.close()" in fuente
    # Figura por defecto de 6.4 x 4.8 pulgadas a 120 dpi
    for numero in (1, 2, 3):
        imagen = mpimg.imread(pipelines(tabla)["base"] / "reportes" / f"{tabla}_grafica_{numero}.png")
        assert imagen.shape[:2] == (576, 768)


@casos("G01", 8)
def test_carpeta_reportes_inexistente(tabla, copia_proyecto, capsys):
    modulo("exportar", tabla).exportar(copia_proyecto)
    modulo("limpiar", tabla).limpiar(copia_proyecto)
    assert not (copia_proyecto / "reportes").exists()

    proceso = ejecutar_script(f"reporte_{tabla}", cwd=copia_proyecto, timeout=60)

    assert_proceso_ok(proceso)
    assert sorted(p.name for p in (copia_proyecto / "reportes").iterdir()) == [
        f"{tabla}_grafica_{numero}.png" for numero in (1, 2, 3)
    ]


@casos("G01", 10)
def test_imagenes_versionadas(tabla):
    versionadas = subprocess.run(
        ["git", "ls-files", f"reportes/{tabla}_grafica_*.png"], cwd=RAIZ, capture_output=True, text=True,
    ).stdout.split()
    if not versionadas:
        pytest.skip("Las imágenes existen pero aún no se ha hecho commit de reportes/")
    assert sorted(versionadas) == [f"reportes/{tabla}_grafica_{numero}.png" for numero in (1, 2, 3)]
