from dataclasses import dataclass
import pandas as pd

from dsl.errors import DSLValidationError

class Preprocess:
    name: str
    input: str
    operations: list

    def __init__(self, name, input, operations):
        self.name = name
        self.input = input
        self.operations = operations
    
    def drop_operation(self, operation, data):
        return data.drop(columns = operation.columns)
    
    def impute_operation(self, operation, data):
        data = data.copy()

        for column in operation.columns:
            if column not in data.columns:
                raise DSLValidationError(f"La columna '{column}' no se encuentra en el datasource")
            
            if not pd.api.types.is_numeric_dtype(data[column]):
                raise DSLValidationError(f"La columna '{column}' debe ser numerica para aplicar impute")

            if operation.method == "mean":
                data[column] = data[column].fillna(data[column].mean()) # media

            elif operation.method == "median":
                data[column] = data[column].fillna(data[column].median()) # mediana

            elif operation.method == "mode":
                data[column] = data[column].fillna(data[column].mode()[0]) # moda

            else:
                raise DSLValidationError(f"Tipo de imputacion '{operation.method}' no soportado")
            
        return data
    
    def scale_operation(self, operation, data):
        data = data.copy()

        for column in operation.columns:
            if column not in data.columns:
                raise DSLValidationError(f"La columna '{column}' no se encuentra en el datasource")
            
            if not pd.api.types.is_numeric_dtype(data[column]):
                raise DSLValidationError(f"La columna '{column}' debe ser numerica para aplicar scale")
        
            if operation.method == "standard":
                # Formula: nuevo_valor = (valor_original - media) / desviación_estándar
                mean = data[column].mean()
                std = data[column].std(ddof=0)

                if std == 0:
                    raise DSLValidationError(f"No se puede aplicar el escalado, la desviacion estandar es '{std}'")
                
                data[column] = (data[column] - mean) / std

            elif operation.method == "minmax":
                # Formula: nuevo_valor = (valor_original - min) / (max - min)
                column_min = data[column].min()
                column_max = data[column].max()

                if column_min == column_max:
                    raise DSLValidationError(f"No se puede aplicar el escalado, todos los datos son iguales")

                data[column] = (data[column] - column_min) / (column_max - column_min)
            
            elif operation.method == "robust":
                # Formula: nuevo_valor = (valor_original - mediana) / IQR
                median = data[column].median()
                q1 = data[column].quantile(0.25)
                q3 = data[column].quantile(0.75)
                iqr = q3 - q1

                if iqr == 0:
                    raise DSLValidationError(f"No se puede aplicar el escalado, IQR es cero")

                data[column] = (data[column] - median) / iqr

            elif operation.method == "maxabs":
                # Formula: nuevo_valor = x / max(abs(x))
                max_abs = data[column].abs().max()

                if max_abs == 0:
                    raise DSLValidationError(f"No se puede aplicar el escalado, max_abs es cero")
                
                data[column] = data[column] / max_abs

            else:
                raise DSLValidationError(f"Metodo de escalado '{operation.method}' no soportado")
            
        return data
    
    def encode_operation(self, operation, data):
        data = data.copy()

        for column in operation.columns:
            if column not in data.columns:
                raise DSLValidationError(f"La columna '{column}' no se encuentra en el datasource")
            
            if operation.method == "onehot":
                column_index = data.columns.get_loc(column)
                dummies = pd.get_dummies(data[column], prefix = column, dtype = int)
                data = data.drop(columns = [column])
                for i, dummy_column in enumerate(dummies.columns):
                    data.insert(column_index + i, dummy_column, dummies[dummy_column])

            elif operation.method == "label":
                data[column] = data[column].astype("category").cat.codes

            #elif operation.method == "ordinal":
                #pass

            elif operation.method == "frequency":
                absolute_frequency = data[column].value_counts().to_dict()
                data[column] = data[column].map(absolute_frequency)

            else:
                raise DSLValidationError(f"Metodo de codificacion '{operation.method}' no soportado")

        return data


@dataclass
class PreprocessOperation:
    action: str
    method: str
    columns: list