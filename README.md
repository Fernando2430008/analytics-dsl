# Analytics DSL

Analytics DSL es un lenguaje de dominio específico desarrollado en Python para
cargar datos tabulares, preprocesarlos, entrenar clasificadores, evaluarlos y
obtener predicciones mediante una sintaxis declarativa.

## Requisitos y dependencias

- Python **3.11, 3.12 o 3.13**, con `pip` y soporte para entornos virtuales.
  Se recomienda Python 3.12. El conjunto de dependencias fijado no admite Python
  3.14 o posterior; usa un entorno con una versión compatible.
- Git para clonar el repositorio, o **Code → Download ZIP** en GitHub.
- Acceso a Internet durante la instalación.

| Dependencia directa | Versión | Uso |
| --- | --- | --- |
| `ply` | `3.11` | Análisis léxico y sintáctico. |
| `pandas` | `2.2.3` | Lectura de CSV y transformación de datos. |
| `scikit-learn` | `1.8.0` | Clasificadores, particiones y métricas. |

`requirements.txt` es la fuente de dependencias, también utilizada al instalar
el paquete con `pyproject.toml`. `pip` resuelve automáticamente las dependencias
transitivas, como NumPy, SciPy, joblib y threadpoolctl. No se necesita Jupyter,
Matplotlib ni una GPU. `requeriments.txt` se conserva como alias del nombre anterior.

## Instalación

```bash
git clone https://github.com/Fernando2430008/analytics-dsl.git
cd analytics-dsl
```

También puedes descargar y descomprimir el ZIP y abrir una terminal en esa carpeta.

### Windows (PowerShell o CMD)

Estos comandos usan directamente el intérprete del entorno; no hace falta activarlo
ni cambiar la política de PowerShell.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install .
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe main.py Example.txt
```

Sustituye `-3.12` por `-3.11` o `-3.13` si esa es tu versión instalada.
Si no tienes el lanzador `py`, usa `python -m venv .venv` después de comprobar
la versión con `python --version`.

### Linux y macOS

Comprueba que `python3 --version` indique una versión compatible. Si tu sistema
usa otra por defecto, sustituye `python3` por `python3.12`, por ejemplo.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install .
.venv/bin/python -m pip check
.venv/bin/python main.py Example.txt
```

Si tu distribución no incluye `venv`, instala el componente correspondiente a la
versión de Python elegida y vuelve a crear el entorno.

### Alternativa: ejecutar desde el código fuente

Con el entorno activo, puedes instalar solo las dependencias:

```bash
python -m pip install -r requirements.txt
python main.py Example.txt
```

Esta alternativa no registra el comando `analytics-dsl`; `pip install .` instala
el paquete y sus dependencias. En los comandos siguientes, `python` debe ser el
intérprete del entorno virtual; sin activarlo, usa su ruta completa como arriba.

## Ejemplo listo para ejecutar

`Example.txt` utiliza `examples/churn_demo.csv`, un conjunto de **80 filas de datos
sintéticos** incluido en el repositorio. No necesitas descargar datos externos ni
modificar rutas para probarlo. Ejecuta desde la carpeta principal:

```bash
python main.py Example.txt
```

Verás las primeras filas, las métricas de validación cruzada y holdout, las
predicciones y la lista de objetos. Se genera `churn_predictions.csv`, con una
columna adicional `prediction`. Volver a ejecutar el ejemplo reemplaza ese archivo.

Para usar tu `Churn_Modelling.csv`, cambia `location` en `Example.txt` y comprueba
que el CSV tenga las columnas utilizadas en ese archivo.

## Ejecución de archivos y consola

Después de `pip install .`, con el entorno activo:

```bash
analytics-dsl
analytics-dsl Example.txt
analytics-dsl --help
```

También funcionan `python -m dsl` y `python -m dsl Example.txt`.
`python main.py` sigue disponible desde el repositorio.

Las rutas de `location` y `save_to` se resuelven respecto de la **carpeta desde
la que ejecutas el comando**, no respecto del archivo DSL. Usa rutas absolutas
si ejecutas desde otra carpeta. En Windows puedes escribir `"C:/datos/clientes.csv"`.

En la consola, escribe o pega un bloque de una o varias líneas y pulsa `Enter`
en una **línea vacía** para ejecutarlo. Incluso una declaración de una sola línea
necesita esa línea vacía. El prompt `...` indica que se sigue acumulando texto.

```text
Entrada > datasource customers {
...     type csv
...     location "examples/churn_demo.csv"
... }
...
```

Los objetos permanecen en memoria durante la sesión. Usa `Ctrl + C` para salir,
`Ctrl + D` en Linux/macOS o `Ctrl + Z` seguido de `Enter` en Windows.
Al recibir fin de entrada se ejecuta el último bloque pendiente.
Para ejecutar un archivo completo, utiliza el argumento de archivo mostrado arriba.

## Sintaxis disponible

Se admiten comentarios de una línea iniciados con `#` y se realiza validación
léxica, sintáctica y semántica.

### Fuente de datos

Solo se admiten archivos CSV locales.

```text
datasource customers { type csv location "examples/churn_demo.csv" }
```

### Preprocesamiento

| Operación | Métodos |
| --- | --- |
| `drop` | Elimina las columnas indicadas. |
| `impute` | `mean`, `median`, `mode`. |
| `scale` | `standard`, `minmax`, `robust`, `maxabs`. |
| `encode` | `onehot`, `label`, `frequency`. |

`frequency` reemplaza cada categoría por su conteo absoluto en el conjunto.

```text
preprocess customer_pipe { input customers drop ["RowNumber", "CustomerId", "Surname"] impute mean ["Age", "Balance"] scale standard ["Age", "Balance"] encode onehot ["Geography", "Gender"] }
```

### Clasificadores

| Algoritmo | Parámetros admitidos |
| --- | --- |
| `random_forest` | `trees`, `depth`, `balance`, `random_state`. |
| `logistic_regression` | `c`, `iterations`, `balance`, `random_state`. |
| `hist_gradient_boosting` | `iterations`, `learning_rate`, `depth`, `balance`, `random_state`. |

```text
learner classifier { algorithm random_forest parameters { trees = 200 depth = 10 balance = true random_state = 42 } }
```

### Modelo, evaluación y predicción

```text
model churn_model { fit classifier using customer_pipe target Exited }
evaluate churn_cv { model churn_model datasource customer_pipe split cross_validation { folds 5 stratify true random_state 42 } metrics [accuracy,precision,recall,f1,auc] }
evaluate churn_holdout { model churn_model datasource customer_pipe split holdout { train 0.8 test 0.2 stratify true random_state 42 } metrics [accuracy,precision,recall,f1,auc] }
predict churn_prediction { model churn_model datasource customer_pipe save_to "churn_predictions.csv" }
```

Aunque el campo se llama `datasource`, en `evaluate` y `predict` también puede
referirse a un `preprocess`. Las columnas deben coincidir con las utilizadas en
el entrenamiento. `evaluate` necesita la columna objetivo; `predict` admite datos
con o sin ella.

### Funciones adicionales

```text
list objects
list model
show config churn_model
show info customer_pipe
delete churn_prediction
```

`show info` solo se admite para objetos `datasource` y `preprocess`.

## Verificación para desarrollo

Con el entorno activo y las dependencias instaladas:

```bash
python -m pip check
python -m unittest discover -s tests -v
```

Las pruebas cubren el ejemplo completo, los tres clasificadores, la consola
multilínea y la ejecución de archivos, incluidos errores de entrada. Se usa
`unittest`, incluido en Python; no necesitas instalar pytest.

## Limitaciones actuales

- Los algoritmos son de clasificación, no de regresión, y trabajan con CSV locales.
- Las métricas están orientadas principalmente a clasificación binaria. Para
  `precision`, `recall` y `f1`, utiliza un objetivo codificado como `0` y `1`.
- El preprocesamiento se calcula antes de dividir los datos en `evaluate`;
  puede usar información del conjunto de prueba. Las métricas del ejemplo
  demuestran funcionamiento. Una evaluación rigurosa requiere ajustar las
  transformaciones dentro de cada partición de entrenamiento.
- No se guarda un pipeline reutilizable. Para datos nuevos se deben reproducir
  las transformaciones y columnas del entrenamiento; el intérprete no conserva
  los parámetros de transformación para aplicarlos después.
- Los objetos y modelos permanecen solo en memoria y no se guardan al cerrar.
