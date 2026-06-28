from dataclasses import dataclass
from pathlib import Path
from dsl.errors import DSLValidationError

@dataclass
class DataSource:
    name: str
    type: str
    location: str

    def get_document(self):
        path = Path(self.location)

        if not path.exists():
            raise DSLValidationError(f"El archivo en la ruta '{path}' no existe")
                
        if self.type == "txt":
            with open (self.location, "r", encoding="utf-8") as archivo:                    
                contenido = archivo.read()
                return contenido
        
        raise DSLValidationError(f"Tipo de dato '{self.type}' no soportado")

