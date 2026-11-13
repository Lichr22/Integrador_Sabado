import contextlib
import importlib
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import pytest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
sys.path.insert(0, str(SRC))

ETAPAS = ["simular", "exportar", "limpiar", "consultas", "reporte"]

# Datos de cada tabla según sus criterios. `f01` traduce cada caso común de la etapa F01
# a su número en la matriz, porque cada tabla numera distinto sus casos de simulación.
TABLAS = {
    "categorias": {
        "prefijo": "CAT", "n": 250, "duplicados": 20, "groupby_minimo": 3,
        "columnas": ["id", "nombre", "descripcion", "area_responsable"],
        "constantes": ["CATEGORIAS", "AREAS"],
        "ensuciadas": ["descripcion", "area_responsable"],
        "f01": {"corre": 1, "constantes": 2, "columnas": 3, "filas": 4, "uuid": 5, "semilla": 9,
                "reproducible": 10, "duplicados": 15, "generar": 16, "import": 17, "main": 18},
    },
    "retos": {
        "prefijo": "RET", "n": 500, "duplicados": 25, "groupby_minimo": 2,
        "columnas": ["id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
                     "estado", "id_empresa", "id_categoria", "id_prioridad"],
        "constantes": ["ESTADOS", "IDS_EMPRESA", "IDS_CATEGORIA", "IDS_PRIORIDAD"],
        "ensuciadas": ["descripcion", "fecha_fin"],
        "f01": {"corre": 1, "constantes": 2, "columnas": 3, "filas": 4, "uuid": 5, "semilla": 14,
                "reproducible": 15, "duplicados": 22, "generar": 24, "import": 25, "main": 26},
    },
    "empresas": {
        "prefijo": "EMP", "n": 300, "duplicados": 15, "groupby_minimo": 2,
        "columnas": ["id", "nombre", "nit", "sector", "contacto", "correo", "telefono", "activa"],
        "constantes": ["SECTORES"],
        "ensuciadas": ["contacto"],
        "f01": {"corre": 1, "constantes": 2, "columnas": 3, "filas": 4, "uuid": 5, "semilla": 13,
                "reproducible": 14, "duplicados": 23, "generar": 25, "import": 26, "main": 27},
    },
    "registros": {
        "prefijo": "REG", "n": 800, "duplicados": 40, "groupby_minimo": 2,
        "columnas": ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto"],
        "constantes": ["ESTADOS", "IDS_USUARIO", "IDS_RETO"],
        "ensuciadas": ["observacion"],
        "f01": {"corre": 1, "constantes": 2, "columnas": 3, "filas": 4, "uuid": 5, "semilla": 11,
                "reproducible": 12, "duplicados": 17, "generar": 18, "import": 19, "main": 20},
    },
    "prioridades": {
        "prefijo": "PRI", "n": 200, "duplicados": 16, "groupby_minimo": 2,
        "columnas": ["id", "nombre", "nivel", "dias_max_respuesta"],
        "constantes": ["NIVELES", "DIAS"],
        "ensuciadas": ["nivel", "dias_max_respuesta"],
        "f01": {"corre": 1, "constantes": 2, "columnas": 3, "filas": 4, "uuid": 5, "semilla": 9,
                "reproducible": 10, "duplicados": 17, "generar": 18, "import": 19, "main": 20},
    },
}


def caso(tabla, etapa, numero):
    return f"TC-{TABLAS[tabla]['prefijo']}-{etapa}-{numero:03d}"


def casos(etapa, numero):
    """Parametriza una prueba común para las 5 tablas; el id de cada variante es el ID del caso."""
    return pytest.mark.parametrize(
        "tabla",
        [pytest.param(tabla, id=caso(tabla, etapa, numero)) for tabla in TABLAS],
    )


def casos_f01(clave):
    return pytest.mark.parametrize(
        "tabla",
        [pytest.param(tabla, id=caso(tabla, "F01", datos["f01"][clave])) for tabla, datos in TABLAS.items()],
    )


def modulo(etapa, tabla):
    return importlib.import_module(f"{etapa}_{tabla}")


def generar(tabla, **kwargs):
    return getattr(modulo("simular", tabla), f"generar_{tabla}")(**kwargs)


def ejecutar_script(nombre, cwd=RAIZ, timeout=120):
    """Ejecuta `python src/<nombre>.py` como lo haría una persona desde la raíz."""
    entorno = {**os.environ, "PYTHONUTF8": "1", "MPLBACKEND": "Agg"}
    return subprocess.run(
        [sys.executable, f"src/{nombre}.py"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=entorno, timeout=timeout,
    )


def leer_fuente(nombre):
    return (SRC / f"{nombre}.py").read_text(encoding="utf-8")


def capturar(funcion, *args):
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        resultado = funcion(*args)
    return resultado, salida.getvalue()


def assert_proceso_ok(proceso):
    assert proceso.returncode == 0, proceso.stderr
    assert "Traceback" not in proceso.stdout + proceso.stderr


@pytest.fixture(scope="session")
def ejecucion_real():
    """Corre los 25 scripts en orden sobre la carpeta real del proyecto (genera data/ y reportes/)."""
    return {
        f"{etapa}_{tabla}": ejecutar_script(f"{etapa}_{tabla}")
        for tabla in TABLAS for etapa in ETAPAS
    }


@pytest.fixture(scope="session")
def pipelines(tmp_path_factory):
    """Corre el pipeline de una tabla en una carpeta temporal y guarda lo que imprime cada etapa."""
    cache = {}

    def obtener(tabla):
        if tabla not in cache:
            base = tmp_path_factory.mktemp(tabla)
            rutas, salida_exportar = capturar(modulo("exportar", tabla).exportar, base)
            limpio, salida_limpiar = capturar(modulo("limpiar", tabla).limpiar, base)
            consultas, salida_consultas = capturar(modulo("consultas", tabla).ejecutar, base)
            conclusiones, salida_reporte = capturar(modulo("reporte", tabla).generar_reporte, base)
            cache[tabla] = {
                "base": base,
                "rutas": rutas,
                "limpio": limpio,
                "consultas": consultas,
                "conclusiones": conclusiones,
                "salida": {
                    "exportar": salida_exportar,
                    "limpiar": salida_limpiar,
                    "consultas": salida_consultas,
                    "reporte": salida_reporte,
                },
            }
        return cache[tabla]

    return obtener


@pytest.fixture
def copia_proyecto(tmp_path):
    """Copia src/ a una carpeta vacía para probar casos negativos sin tocar el proyecto real."""
    shutil.copytree(SRC, tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__"))
    return tmp_path


@pytest.fixture
def ejes(monkeypatch, tmp_path):
    """Dibuja una gráfica sin cerrarla para poder inspeccionar los ejes."""
    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "close", lambda *args: None)

    def dibujar(grafica, df):
        datos = grafica(df, tmp_path)
        return datos, plt.gca()

    yield dibujar
    monkeypatch.undo()
    plt.close("all")
