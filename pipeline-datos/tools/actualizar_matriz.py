"""Lleva los resultados de pytest (reportes-pruebas/junit.xml) a la matriz de cobertura en Excel.

Uso: python tools/actualizar_matriz.py <matriz.xlsx> [--salida <archivo.xlsx>] [--tester "Nombre"]

Solo diligencia las columnas Estado, Resultado obtenido / Evidencia y Tester de los casos
que tienen una prueba automatizada. Las fórmulas del Resumen y de la Trazabilidad se recalculan
al abrir el archivo en Excel.
"""

import argparse
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.styles import PatternFill

RAIZ = Path(__file__).resolve().parents[1]
PATRON_CASO = re.compile(r"test_tc_(ret|cat|emp)_([a-z]\d{2})_(\d{3})")
RELLENOS = {
    "Pasó": PatternFill("solid", fgColor="FFC6EFCE"),
    "Falló": PatternFill("solid", fgColor="FFFFC7CE"),
    "Bloqueado": PatternFill("solid", fgColor="FFFFEB9C"),
}

HALLAZGOS_NUEVOS = [
    ("RET-F01", 'AC07 usa `end_date="+3m"`, pero en Faker `m` son MINUTOS: no se generan retos futuros. '
                'Los meses se escriben `M`.', "Alta",
     'Usar `fake.date_between(start_date="-1y", end_date="+3M")`. Aplicado en src/simular_retos.py.'),
    ("RET-F01", "AC04 pide `str(uuid.uuid4())`, que no depende de la semilla: el archivo no sería reproducible "
                "como exige AC13.", "Media",
     "Usar `fake.uuid4()` (también UUID v4, pero con semilla). Aplicado en src/simular_retos.py."),
    ("RET-L01", "F01-AC14 ensucia el 10% de los nombres con espacios, pero ningún paso de L01 los limpia.", "Media",
     'Agregar `df["nombre"] = df["nombre"].str.strip()`. Aplicado en src/limpiar_retos.py.'),
    ("RET-F01", 'Faker toma "-1y" como 365,25 días: puede generar una fecha un día anterior al año calendario.',
     "Baja", "Aceptar ±1 día en la validación del rango de fecha_inicio."),
]


def leer_resultados(junit):
    """Agrupa los resultados por caso: un caso con varias pruebas pasa solo si todas pasan."""
    raiz = ET.parse(junit).getroot()
    fecha = datetime.fromisoformat(raiz.find("testsuite").get("timestamp")).strftime("%d/%m/%Y")
    casos = {}
    for prueba in raiz.iter("testcase"):
        coincidencia = PATRON_CASO.search(prueba.get("name"))
        if not coincidencia:
            continue
        tabla, etapa, numero = coincidencia.groups()
        caso = f"TC-{tabla.upper()}-{etapa.upper()}-{numero}"
        if prueba.find("failure") is not None or prueba.find("error") is not None:
            detalle = (prueba.find("failure") or prueba.find("error")).get("message", "")
            estado = ("Falló", detalle.splitlines()[0][:200] if detalle else "")
        elif prueba.find("skipped") is not None:
            estado = ("Bloqueado", prueba.find("skipped").get("message", ""))
        else:
            estado = ("Pasó", "")
        anterior = casos.get(caso)
        prioridad = ["Pasó", "Bloqueado", "Falló"]
        if anterior is None or prioridad.index(estado[0]) > prioridad.index(anterior["estado"]):
            casos[caso] = {"estado": estado[0], "detalle": estado[1], "pruebas": []}
        casos[caso]["pruebas"].append(f"{prueba.get('classname').split('.')[-1]}.py::{prueba.get('name')}")
    return casos, fecha


def actualizar(matriz, salida, tester, junit):
    casos, fecha = leer_resultados(junit)
    libro = openpyxl.load_workbook(matriz)
    hoja = libro["Casos de prueba"]
    columnas = {celda.value: celda.column for celda in hoja[1]}

    actualizados = 0
    for fila in hoja.iter_rows(min_row=2):
        caso = casos.get(fila[0].value)
        if caso is None:
            continue
        prueba = caso["pruebas"][0] if len(caso["pruebas"]) == 1 else f"{caso['pruebas'][0].split('[')[0]} ({len(caso['pruebas'])} variantes)"
        evidencia = f"{caso['estado']} en pytest ({fecha}). Prueba: tests/{prueba}. Reporte: reportes-pruebas/pytest.html"
        if caso["detalle"]:
            evidencia += f". Detalle: {caso['detalle']}"
        celda_estado = hoja.cell(row=fila[0].row, column=columnas["Estado"])
        celda_estado.value = caso["estado"]
        celda_estado.fill = RELLENOS[caso["estado"]]
        hoja.cell(row=fila[0].row, column=columnas["Resultado obtenido / Evidencia"]).value = evidencia
        hoja.cell(row=fila[0].row, column=columnas["Tester"]).value = tester
        actualizados += 1

    hallazgos = libro["Hallazgos"]
    existentes = {fila[2] for fila in hallazgos.iter_rows(min_row=2, values_only=True)}
    for hu, texto, severidad, recomendacion in HALLAZGOS_NUEVOS:
        if texto in existentes:
            continue
        ultima = hallazgos.max_row
        nueva = ultima + 1
        hallazgos.append([ultima, hu, texto, severidad, recomendacion])
        for columna in range(1, 6):
            origen = hallazgos.cell(row=ultima, column=columna)
            destino = hallazgos.cell(row=nueva, column=columna)
            destino._style = origen._style

    libro.calculation.fullCalcOnLoad = True
    libro.save(salida)
    resumen = {estado: sum(c["estado"] == estado for c in casos.values()) for estado in RELLENOS}
    print(f"Casos actualizados: {actualizados} {resumen}")
    print(f"Matriz guardada en: {salida}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("matriz", type=Path)
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--tester", default="Alirio Andres Piña (pytest)")
    parser.add_argument("--junit", type=Path, default=RAIZ / "reportes-pruebas" / "junit.xml")
    args = parser.parse_args()
    salida = args.salida or RAIZ / "evidencias" / f"{args.matriz.stem}_ejecutada.xlsx"
    salida.parent.mkdir(parents=True, exist_ok=True)
    actualizar(args.matriz, salida, args.tester, args.junit)


if __name__ == "__main__":
    main()
