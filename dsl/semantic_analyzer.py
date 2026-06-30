from dsl.ast import ProgramNode, DataSourceNode, PreprocessNode, LearnerNode
from dsl.errors import DSLValidationError

class SemanticAnalyzer():
    def __init__(self):
        self.symbols = {}

    def analyze(self, program):
        self.register_symbols(program)
        self.validate_declarations(program)
        return program

    def register_symbols(self, program: ProgramNode):
        for declaration in program.declarations:
            if declaration.name in self.symbols:
                raise DSLValidationError(f"El nombre '{declaration.name}' ya fue declarado anteriormente")

            if isinstance(declaration, DataSourceNode):
                self.symbols[declaration.name] = {
                    "kind" : "datasource",
                    "node" : declaration
                }

            elif isinstance(declaration, PreprocessNode):
                self.symbols[declaration.name] = {
                    "kind" : "preprocess",
                    "node" : declaration
                }

            elif isinstance (declaration, LearnerNode):
                self.symbols[declaration.name] = {
                    "kind" : "learner",
                    "node" : declaration
                }

    def validate_declarations(self, program: ProgramNode):
        for declaration in program.declarations:
            if isinstance(declaration, DataSourceNode):
                self.validate_datasource(declaration)
            elif isinstance(declaration, PreprocessNode):
                self.validate_preprocess(declaration)
            elif isinstance(declaration, LearnerNode):
                self.validate_learner(declaration)

    def validate_datasource(self, declaration):
        field_names = []
        for fields in declaration.fields:
            if fields.name in field_names:
                raise DSLValidationError(f"El campo '{fields.name}' ya fue incluido")
            field_names.append(fields.name)
        
        if not "type" in field_names: 
            raise DSLValidationError(f"El tipo de dato no fue incluido")
        elif not "location" in field_names: 
            raise DSLValidationError(f"La ubicacion de el archivo no fue incluida")
        
    def validate_preprocess(self, declaration):
        field_actions = []
        input_name = None
        for fields in declaration.fields:
            if fields.action in field_actions:
                raise DSLValidationError(f"El campo '{fields.action}' ya fue incluido")
            field_actions.append(fields.action)

            if fields.action == "input":
                input_name = fields.value
        
        if input_name is None:
            raise DSLValidationError(f"El campo input debe ser incluido")
        
        if not input_name in self.symbols:
            raise DSLValidationError(f"El datasource '{input_name}' no existe")

    def validate_learner(self, declaration):
        pass