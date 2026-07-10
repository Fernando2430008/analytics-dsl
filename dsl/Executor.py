from dsl.ast import DataSourceNode, PreprocessNode, PreprocessFieldNode, PreprocessSimpleFieldNode

from dsl.DataSource import DataSource
from dsl.Preprocess import Preprocess, PreprocessOperation

class Interpreter:
    def __init__(self):
        self.environment = {}

    def execute(self, program):
        for declaration in program.declarations:
            if isinstance(declaration, DataSourceNode):
                self.execute_datasource(declaration)
            
        for declaration in program.declarations:
            if isinstance(declaration, PreprocessNode):
                self.execute_preprocess(declaration)
    
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

    def execute_preprocess(self, declaration):
        operations = []
        input_name = None

        for field in declaration.fields:
            if isinstance(field, PreprocessSimpleFieldNode) and field.action == "input":
                input_name = field.value
            elif isinstance(field, PreprocessSimpleFieldNode):
                operation = PreprocessOperation(
                    action = field.action,
                    method = None,
                    columns = field.value
                )
            elif isinstance(field, PreprocessFieldNode):
                operation = PreprocessOperation(
                    action = field.action,
                    method = field.type,
                    columns = field.value
                )
                
            if field.action != "input":
                operations.append(operation)
        
        preprocess = Preprocess(
            name = declaration.name,
            input = input_name,
            operations = operations
        )

        data = self.environment[input_name]

        for op in operations:
            if op.action == "drop":
                data = preprocess.drop_operation(op, data)
            elif op.action == "impute":
                data = preprocess.impute_operation(op,data)
            elif op.action == "scale":
                data = preprocess.scale_operation(op,data)
            elif op.action == "encode":
                data = preprocess.encode_operation(op,data)

        self.environment[declaration.name] = data

        print(data.head())