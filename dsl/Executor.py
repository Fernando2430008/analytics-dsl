from dsl.ast import DataSourceNode
from dsl.DataSource import DataSource

class Interpreter:
    def __init__(self):
        self.environment = {}

    def execute(self, program):
        for declaration in program.declarations:
            if isinstance(declaration, DataSourceNode):
                self.execute_datasource(declaration)
    
    def execute_datasource(self, declaration):
        fields = {}

        for field in declaration.fields:
            fields[field.name] = field.value
        
        datasource = DataSource (
            name = declaration.name,
            type = fields["type"],
            location = fields["location"]
        )

        data = datasource.load()
        self.environment[declaration.name] = data

        #Verificando funcionalidad
        print(data.head())