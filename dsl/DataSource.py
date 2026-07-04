from pathlib import Path
import pandas as pd

from dsl.errors import DSLValidationError

class DataSource:
    name: str
    type: str
    location: str

    def __init__(self, name, type, location):
        self.name = name
        self.type = type
        self.location = location

    def load(self):
        path = Path(self.location)

        if not path.exists():
            raise DSLValidationError(f"El archivo en la ruta '{path}' no existe")
                
        if self.type == "txt":
            with open (self.location, "r", encoding="utf-8") as file:                    
                data = file.read()
                return data
        elif self.type == "csv":
            data = pd.read_csv(path)
            return data


