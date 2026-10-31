# Pipeline de datos — Equipo 4 (tabla `retos`)

Scripts de Python que simulan, exportan, limpian, consultan y grafican la tabla
`retos`, según las historias de usuario E4-RET-F01, X01, L01, Q01 y G01 del
tablero Kaizen.

## Instalación

```bash
python -m pip install -r requirements.txt
```

## Ejecución (desde esta carpeta, en orden)

| Paso | Comando | Genera |
|---|---|---|
| 1. Simulación (F01) | `python src/simular_retos.py` | Solo imprime `shape`, `head()` e `isna().sum()` |
| 2. Exportación (X01) | `python src/exportar_retos.py` | `data/crudo/retos_sucio.csv`, `.xlsx` y `.json` |
| 3. Limpieza (L01) | `python src/limpiar_retos.py` | `data/limpio/retos_limpio.csv` |
| 4. Consultas (Q01) | `python src/consultas_retos.py` | `data/limpio/retos_consulta_1..5.csv` |
| 5. Reporte (G01) | `python src/reporte_retos.py` | `reportes/retos_grafica_1..3.png` y conclusiones en consola |

Los archivos de `data/crudo` se regeneran con `python src/exportar_retos.py`.
Son reproducibles (semilla 42) siempre que se generen el mismo día, porque
`fecha_inicio` se calcula respecto a la fecha actual.

## Pruebas

```bash
python -m pip install -r requirements-test.txt
python -m pytest
```

Cada prueba se llama como su caso en la matriz de cobertura
(`test_tc_ret_f01_001_...` → `TC-RET-F01-001`).

- Resultados: `reportes-pruebas/pytest.html`
- Cobertura: `reportes-pruebas/cobertura/index.html`
- Para llevar los resultados a la matriz de Excel:
  `python tools/actualizar_matriz.py <ruta-de-la-matriz.xlsx>`

## Decisiones frente a los criterios de aceptación

| Criterio | Decisión | Motivo |
|---|---|---|
| F01-AC04 (`uuid.uuid4()`) | Se usa `fake.uuid4()` | `uuid.uuid4()` no respeta la semilla y rompe la reproducibilidad (AC13). Ambos generan UUID v4. |
| F01-AC07 (`end_date="+3m"`) | Se usa `"+3M"` | En Faker `m` son **minutos**; los meses son `M`. Con `"+3m"` no hay retos futuros. |
| F01-AC03 (500 filas) | 500 filas base + 25 duplicados = 525 | El 5% de duplicados (AC19) se agrega encima de las 500. |
| L01 (nombre) | Se agrega `str.strip()` a `nombre` | F01 ensucia el 10% de nombres con espacios, pero ningún paso de L01 los limpiaba. |
| L01-AC09 (`fecha_valida`) | `fecha_valida = ~(duracion_dias < 0)` | Con `duracion_dias >= 0` los retos sin `fecha_fin` quedaban como inválidos y se mezclaban con los incoherentes. Los nulos se reportan aparte. |
| L01-AC13 (columnas obligatorias) | Todas menos `fecha_fin` y `duracion_dias` | Ningún paso rellena `fecha_fin`; un reto puede no tener fecha de cierre. |
| Q01-AC06 (consulta 4) | `.agg(["count", "mean", "min", "max"])` | La pregunta pide la mínima, pero el código del criterio no incluía `"min"`. |
