import contextlib
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

import consultas_retos  # noqa: E402
import exportar_retos  # noqa: E402
import limpiar_retos  # noqa: E402
import reporte_retos  # noqa: E402

ORDEN_SCRIPTS = ["simular", "exportar", "limpiar", "consultas", "reporte"]


def ejecutar_script(nombre, cwd=RAIZ, timeout=120):
    """Ejecuta `python src/<nombre>_retos.py` como lo haría una persona desde la raíz."""
    entorno = {**os.environ, "PYTHONUTF8": "1", "MPLBACKEND": "Agg"}
    return subprocess.run(
        [sys.executable, f"src/{nombre}_retos.py"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=entorno, timeout=timeout,
    )


def leer_fuente(nombre):
    return (SRC / f"{nombre}_retos.py").read_text(encoding="utf-8")


def _capturar(funcion, *args):
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        resultado = funcion(*args)
    return resultado, salida.getvalue()


@pytest.fixture(scope="session")
def ejecucion_real():
    """Corre los 5 scripts en orden sobre la carpeta real del proyecto (genera data/ y reportes/)."""
    return {nombre: ejecutar_script(nombre) for nombre in ORDEN_SCRIPTS}


@pytest.fixture(scope="session")
def pipeline(tmp_path_factory):
    """Corre el pipeline completo en una carpeta temporal y guarda lo que imprime cada etapa."""
    base = tmp_path_factory.mktemp("pipeline")
    rutas, salida_exportar = _capturar(exportar_retos.exportar, base)
    limpio, salida_limpiar = _capturar(limpiar_retos.limpiar, base)
    consultas, salida_consultas = _capturar(consultas_retos.ejecutar, base)
    conclusiones, salida_reporte = _capturar(reporte_retos.generar_reporte, base)
    return {
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


@pytest.fixture
def copia_proyecto(tmp_path):
    """Copia src/ a una carpeta vacía para probar casos negativos sin tocar el proyecto real."""
    shutil.copytree(SRC, tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__"))
    return tmp_path


def assert_proceso_ok(proceso):
    assert proceso.returncode == 0, proceso.stderr
    assert "Traceback" not in proceso.stdout + proceso.stderr
