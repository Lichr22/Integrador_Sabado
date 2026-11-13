# Pipeline de datos — Equipo 4

Scripts de Python que simulan, exportan, limpian, consultan y grafican las cinco
tablas de la plataforma de retos, según las historias de usuario E4 del tablero
Kaizen (F01 simulación, X01 exportación, L01 limpieza, Q01 consultas y
G01 gráficas).

| Tabla | Prefijo HU | Responsable |
|---|---|---|
| `categorias` | E4-CAT | Valentina Corredor |
| `retos` | E4-RET | Alirio Andrés Piña |
| `empresas` | E4-EMP | Andrés Espinosa |
| `registros` | E4-REG | Alirio Andrés Piña |
| `prioridades` | E4-PRI | Andrés Espinosa |

## Instalación

```bash
python -m pip install -r requirements.txt
```

## Ejecución (desde esta carpeta, en orden, por tabla)

Reemplaza `<tabla>` por `categorias`, `retos`, `empresas`, `registros` o `prioridades`.

| Paso | Comando | Genera |
|---|---|---|
| 1. Simulación (F01) | `python src/simular_<tabla>.py` | Solo imprime `shape`, `head()` e `isna().sum()` |
| 2. Exportación (X01) | `python src/exportar_<tabla>.py` | `data/crudo/<tabla>_sucio.csv`, `.xlsx` y `.json` |
| 3. Limpieza (L01) | `python src/limpiar_<tabla>.py` | `data/limpio/<tabla>_limpio.csv` |
| 4. Consultas (Q01) | `python src/consultas_<tabla>.py` | `data/limpio/<tabla>_consulta_1..5.csv` |
| 5. Reporte (G01) | `python src/reporte_<tabla>.py` | `reportes/<tabla>_grafica_1..3.png` y conclusiones en consola |

La limpieza también genera `data/limpio/categorias_catalogo.csv`,
`data/limpio/prioridades_catalogo.csv` y `data/limpio/registros_repetidos.csv`.

### Cómo regenerar los archivos de `data/crudo`

```bash
python src/exportar_categorias.py
python src/exportar_retos.py
python src/exportar_empresas.py
python src/exportar_registros.py
python src/exportar_prioridades.py
```

Son reproducibles (semilla 42) siempre que se generen el mismo día, porque las
fechas de retos y registros se calculan respecto a la fecha actual.

## Pruebas

```bash
python -m pip install -r requirements-test.txt
python -m pytest
```

Cada caso de la matriz de cobertura tiene su prueba:

- Los casos que se repiten igual en las 5 tablas (existe y corre, exportación,
  carpetas, idempotencia, versionado…) están en `tests/test_comunes.py` y corren
  una vez por tabla: `test_csv_generado[TC-CAT-X01-003]`.
- Los casos propios de cada tabla están en `tests/test_<tabla>.py`:
  `test_tc_ret_f01_018_...` → `TC-RET-F01-018`.

Reportes:

- Resultados: `reportes-pruebas/pytest.html`
- Cobertura: `reportes-pruebas/cobertura/index.html`
- Para llevar los resultados a la matriz de Excel:
  `python tools/actualizar_matriz.py <ruta-de-la-matriz.xlsx>`

## Decisiones frente a los criterios de aceptación

| Criterio | Decisión | Motivo |
|---|---|---|
| F01-AC04 de todas las tablas (`uuid.uuid4()`) | Se usa `fake.uuid4()` | `uuid.uuid4()` no respeta la semilla y rompe la reproducibilidad. Ambos generan UUID v4. |
| F01 de todas las tablas (N filas) | N filas base + el % de duplicados encima | Ej.: retos 500 + 25 = 525. |
| RET-F01-AC07 (`end_date="+3m"`) | Se usa `"+3M"` | En Faker `m` son **minutos**; los meses son `M`. Con `"+3m"` no hay retos futuros. |
| REG-F01-AC05 (`end_date="now"`) | Rango de un año que termina hoy a las 00:00 | Con `"now"` cada ejecución usa otra hora y el archivo no es reproducible (AC10). |
| RET-L01 (nombre) | Se agrega `str.strip()` a `nombre` | F01 ensucia el 10% de nombres con espacios, pero ningún paso de L01 los limpiaba. |
| RET-L01-AC09 (`fecha_valida`) | `fecha_valida = ~(duracion_dias < 0)` | Con `duracion_dias >= 0` los retos sin `fecha_fin` quedaban como inválidos. Los nulos se reportan aparte. |
| RET-L01-AC13 (obligatorias) | Todas menos `fecha_fin` y `duracion_dias` | Ningún paso rellena `fecha_fin`; un reto puede no tener fecha de cierre. |
| RET-Q01-AC06 (consulta 4) | `.agg(["count", "mean", "min", "max"])` | La pregunta pide la mínima, pero el código del criterio no incluía `"min"`. |
| EMP-L01 (lectura) | `pd.read_csv(..., dtype={"nit": str, "telefono": str})` | Sin esto pandas los lee como números y se pierden ceros y formatos. |
| EMP-L01-AC08 (teléfono) | Se quita el indicativo `57` | `'+57 300-123-4567'` quedaba con 12 dígitos y el resto con 10. |
| EMP-L01 (NIT) | Se reportan los NIT repetidos | F01 ensucia un 3% de NIT repetidos y ningún criterio los trataba. |
| EMP-Q01 (activa) | Se convierte `activa` a booleano al leer | Al releer el CSV, `activa == True` depende del tipo inferido por pandas. |
| REG-L01 / Q01 / G01 (repetidos) | L01 guarda `registros_repetidos.csv` | El limpio ya no tiene repetidos: la consulta 2 da 0 filas y G01 no podría reportarlos. |
| PRI-L01-AC06 (`nivel`) | Se mapean `uno` a `cinco` | El criterio solo mapeaba `uno`, `dos` y `tres`, pero F01 también genera niveles 4 y 5. |
| PRI-L01-AC09 (mediana) | Mediana redondeada a días enteros | `dias_max_respuesta` es entero. El umbral de 60 días es válido: el máximo de `DIAS` es 30. |
