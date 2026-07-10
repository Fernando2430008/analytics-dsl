from dsl.ast import DataSourceNode, PreprocessNode, PreprocessFieldNode, PreprocessSimpleFieldNode, LearnerNode, LearnerFieldNode, LearnerParametersNode

from dsl.DataSource import DataSource
from dsl.Preprocess import Preprocess, PreprocessOperation
from dsl.Learner import Learner, LearnerParameter

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

        for declaration in program.declarations:
            if isinstance(declaration, LearnerNode):
                self.execute_learner(declaration)
    
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

    def execute_learner(self, declaration):
        name_algorithm = None
        parameters_list = []

        for field in declaration.fields:
            if isinstance(field, LearnerFieldNode):
                name_algorithm = field.value
            else:
                for paramfield in field.fields:
                    parameter = LearnerParameter (
                        name = paramfield.name,
                        value = paramfield.value
                    )
                    parameters_list.append(parameter)

        learner = Learner (
            name = declaration.name,
            algorithm = name_algorithm,
            parameters = parameters_list
        )

        self.environment[declaration.name] = learner


