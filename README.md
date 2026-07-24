# Analytics DSL

Analytics DSL es un lenguaje de dominio específico desarrollado en Python para
describir y ejecutar flujos de analítica de datos tabulares. Permite cargar datos,
preprocesarlos, configurar algoritmos de clasificación, entrenar modelos, evaluarlos
y generar predicciones mediante una sintaxis declarativa.

## Alcance actual

- Carga de archivos CSV locales mediante `datasource`.
- Preprocesamiento mediante `drop`, `impute`, `scale` y `encode`.
- Configuración de los algoritmos `random_forest`, `logistic_regression` y
  `hist_gradient_boosting`.
- Entrenamiento de modelos de clasificación mediante `model`.
- Evaluación mediante validación cruzada o holdout.
- Métricas `accuracy`, `precision`, `recall`, `f1` y `auc`.
- Predicción y exportación opcional de resultados a un archivo CSV.
- Funciones para listar, consultar y eliminar objetos.
- Comentarios de una línea iniciados con `#`.
- Análisis léxico y sintáctico con PLY y validación semántica propia.

## Requisitos

- Python 3.11 o superior.
- Las dependencias incluidas en `requirements.txt`.

## Instalación

Se recomienda crear un entorno virtual antes de instalar las dependencias.

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

Después, instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta principal del proyecto:

```bash
python main.py
```

El programa abre una consola interactiva. Cada declaración debe escribirse completa
en una sola línea. Los objetos creados permanecen en memoria hasta cerrar el programa
con `Ctrl + C` o `Ctrl + Z` seguido de `Enter` en Windows.

El archivo `Example.txt` contiene un flujo completo basado en
`Churn_Modelling.csv`. Antes de ejecutarlo, ajusta las rutas de entrada y salida.

## Sintaxis disponible

### Fuente de datos

Actualmente solo se admiten archivos CSV locales.

```text
datasource customers { type csv location "C:/ruta/archivo.csv" }
```

### Preprocesamiento

- `impute`: `mean`, `median` y `mode`.
- `scale`: `standard`, `minmax`, `robust` y `maxabs`.
- `encode`: `onehot`, `label` y `frequency`.

```text
preprocess customer_pipe { input customers drop ["id"] impute mean ["age"] scale standard ["income"] encode onehot ["city"] }
```

### Algoritmos

- `random_forest`: `trees`, `depth`, `balance`, `random_state`.
- `logistic_regression`: `c`, `iterations`, `balance`, `random_state`.
- `hist_gradient_boosting`: `iterations`, `learning_rate`, `depth`, `balance`,
  `random_state`.

```text
learner classifier { algorithm random_forest parameters { trees = 200 depth = 10 balance = true random_state = 42 } }
```

### Modelo, evaluación y predicción

```text
model churn_model { fit classifier using customer_pipe target Exited }
evaluate churn_cv { model churn_model datasource customer_pipe split cross_validation { folds 5 stratify true random_state 42 } metrics [accuracy,precision,recall,f1,auc] }
evaluate churn_holdout { model churn_model datasource customer_pipe split holdout { train 0.8 test 0.2 stratify true random_state 42 } metrics [accuracy,precision,recall,f1,auc] }
predict churn_prediction { model churn_model datasource customer_pipe save_to "C:/ruta/predictions.csv" }
```

Aunque el campo se llama `datasource`, en `evaluate` y `predict` también puede
referirse a un objeto `preprocess`. Debe utilizarse la misma estructura de columnas
con la que se entrenó el modelo.

### Funciones adicionales

```text
list objects
list model
show config churn_model
show info customer_pipe
delete churn_prediction
```

`show info` solo se admite para objetos `datasource` y `preprocess`.

## Limitaciones

- El prototipo trabaja con datos tabulares provenientes de archivos CSV locales.
- Los algoritmos implementados son de clasificación.
- Las métricas configuradas están orientadas principalmente a clasificación binaria.
- El preprocesamiento no se guarda como un pipeline reutilizable; al predecir con
  datos nuevos se deben reproducir las mismas transformaciones y columnas utilizadas
  durante el entrenamiento.