# Analytics DSL

Analytics DSL es un lenguaje de dominio específico desarrollado en Python para
cargar datos tabulares, preprocesarlos, entrenar clasificadores, evaluarlos y
obtener predicciones mediante una sintaxis declarativa.

## Requisitos

- Python 3.11, 3.12 o 3.13. Se recomienda Python 3.12.
- `pip` y soporte para entornos virtuales.
- Git, o descargar y descomprimir el repositorio desde **Code → Download ZIP**.
- Acceso a Internet para instalar las dependencias.

| Dependencia | Versión | Uso |
| --- | --- | --- |
| `ply` | `3.11` | Análisis léxico y sintáctico. |
| `pandas` | `2.2.3` | Lectura de CSV y transformación de datos. |
| `scikit-learn` | `1.8.0` | Clasificadores, particiones y métricas. |

Estas son las tres dependencias directas necesarias. `pip` instala automáticamente
sus dependencias transitivas, como NumPy y SciPy. El archivo debe llamarse
**`requirements.txt`**, sin espacios en el nombre.

## Instalación

Clona el repositorio y entra en su carpeta:

```bash
git clone https://github.com/Fernando2430008/analytics-dsl.git
cd analytics-dsl
```

También puedes descargar el ZIP y abrir una terminal en la carpeta descomprimida.

### Windows (PowerShell o CMD)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe main.py
```

Sustituye `-3.12` por `-3.11` o `-3.13` si esa es tu versión instalada.
Si no tienes el lanzador `py`, comprueba `python --version` y utiliza
`python -m venv .venv` con una versión compatible.

### Linux y macOS

Comprueba que `python3 --version` indique una versión compatible. Si tu sistema
usa otra por defecto, sustituye `python3` por `python3.12`, por ejemplo.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python main.py
```

Si tu distribución no incluye `venv`, instala el componente correspondiente a la
versión de Python elegida y vuelve a crear el entorno.

## Uso de la consola

`main.py` abre una consola interactiva. Escribe o pega un bloque de una o varias
líneas y pulsa `Enter` en una **línea vacía** para ejecutarlo. Incluso una declaración
de una sola línea necesita esa línea vacía. El prompt `...` indica que se sigue
acumulando texto.

```text
Entrada > datasource customers {
...     type csv
...     location "examples/Churn_Modelling.csv"
... }
...
```

Los objetos permanecen en memoria durante la sesión. Usa `Ctrl + C` para salir,
`Ctrl + D` en Linux/macOS o `Ctrl + Z` seguido de `Enter` en Windows.
Ejecuta el bloque pendiente con una línea vacía antes de salir.

## Ejemplo incluido

El repositorio contiene `examples/Churn_Modelling.csv`, con **10 000 filas**, y
`Example.txt`, que describe un flujo completo de clasificación del abandono de
clientes. No necesitas descargar el CSV por separado.

El ejemplo carga los datos, elimina identificadores, imputa y escala variables,
codifica categorías, entrena un bosque aleatorio, calcula métricas mediante
validación cruzada y holdout, y exporta `churn_predictions.csv`. La columna
`prediction` contiene las predicciones. Volver a ejecutar el ejemplo reemplaza
ese archivo.

Puedes pegar los bloques de `Example.txt` en la consola, en su orden original,
ejecutando cada bloque mediante una línea vacía. También puedes enviar el archivo
completo a la entrada de la consola desde la carpeta principal del repositorio:

**Linux y macOS:**

```bash
.venv/bin/python main.py < Example.txt
```

**Windows CMD:**

```bat
.venv\Scripts\python.exe main.py < Example.txt
```

**Windows PowerShell:**

```powershell
Get-Content Example.txt | .venv\Scripts\python.exe main.py
```

Conserva una línea vacía al final de `Example.txt`, para que se ejecute el último
bloque al redirigir la entrada. `main.py` abre la consola y no procesa un nombre
de archivo pasado como argumento.

Las rutas de `location` y `save_to` se resuelven respecto de la carpeta desde la
que ejecutas el programa. Usa rutas absolutas si ejecutas desde otra carpeta.
En Windows puedes escribir rutas como `"C:/datos/clientes.csv"`.

## Sintaxis disponible

Se admiten comentarios de una línea iniciados con `#` y se realiza validación
léxica, sintáctica y semántica.

### Fuente de datos

Solo se admiten archivos CSV locales.

```text
datasource customers { type csv location "examples/Churn_Modelling.csv" }
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

En `evaluate` y `predict`, el campo `datasource` también puede referirse a un
`preprocess`. Las columnas deben coincidir con las del entrenamiento.
`evaluate` necesita la columna objetivo; `predict` admite datos con o sin ella.

### Funciones adicionales

```text
list objects
list model
show config churn_model
show info customer_pipe
delete churn_prediction
```

`show info` solo se admite para objetos `datasource` y `preprocess`.

## Limitaciones actuales

- Los algoritmos son de clasificación, no de regresión, y trabajan con CSV locales.
- Las métricas están orientadas principalmente a clasificación binaria. Para
  `precision`, `recall` y `f1`, utiliza un objetivo codificado como `0` y `1`.
- El preprocesamiento se calcula antes de dividir los datos en `evaluate` y puede
  usar información del conjunto de prueba. Una evaluación rigurosa requiere ajustar
  las transformaciones dentro de cada partición de entrenamiento.
- No se guarda un pipeline reutilizable. Para datos nuevos se deben reproducir
  las transformaciones y columnas del entrenamiento; el intérprete no conserva
  los parámetros de transformación para aplicarlos después.
- Los objetos y modelos permanecen solo en memoria y no se guardan al cerrar.