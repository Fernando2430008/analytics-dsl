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
            if operation.method == "mean":
                data[column] = data[column].fillna(data[column].mean())
            elif operation.method == "median":
                data[column] = data[column].fillna(data[column].median())
            elif operation.method == "mode":
                data[column] = data[column].fillna(data[column].mode()[0])
            else:
                raise DSLValidationError(f"Tipo de imputacion '{operation.method}' no soportado")
        return data
    
@dataclass
class PreprocessOperation:
    action: str
    method: str
    columns: list