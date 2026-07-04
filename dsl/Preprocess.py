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


@dataclass
class PreprocessOperation:
    action: str
    method: str
    columns: list