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
        pass

    def validate_learner(self, declaration):
        pass



''' # Validacion de campos en datasource 
if not "type" in p[4]: 
    raise DSLValidationError(f"El tipo de dato no fue incluido")
elif not "location" in p[4]: 
    raise DSLValidationError(f"La ubicacion de el archivo no fue incluida")
'''

'''     # Verificar que los fields de el datasource no este en la lista actuals
        if field_name in p[1]:
            raise DSLValidationError(
                f"El campo '{field_name}' esta duplicado en el datasource."
            )
        '''