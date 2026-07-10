from dsl.ast import ProgramNode, DataSourceNode, PreprocessNode, LearnerNode, LearnerParametersNode, ModelNode
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
            
            elif isinstance(declaration, ModelNode):
                self.symbols[declaration.name] = {
                    "kind" : "model",
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
            elif isinstance(declaration, ModelNode):
                self.validate_model(declaration)

    def validate_datasource(self, declaration):
        field_names = {}
        supported_types = ["csv"]

        for field in declaration.fields:
            if field.name in field_names:
                raise DSLValidationError(f"El campo '{field.name}' ya fue incluido")
            field_names[field.name] = field.value
        
        if not "type" in field_names: 
            raise DSLValidationError(f"El tipo de dato no fue incluido")
        if field_names["type"] not in supported_types:
            raise DSLValidationError(f"Tipo de dato '{field_names['type']}' no soportado")
        if not "location" in field_names: 
            raise DSLValidationError(f"La ubicacion de el archivo no fue incluida")
        
    def validate_preprocess(self, declaration):
        drop_list = []
        impute_list = []
        scale_list = []
        encode_list = []
        input_name = None
        for field in declaration.fields:
            if field.action == "input":
                if input_name is not None:
                    raise DSLValidationError(f"El campo '{field.action}' ya fue incluido")
                input_name = field.value
                continue
            
            for val in field.value:
                if field.action == "drop":
                    if val in drop_list:
                        raise DSLValidationError(f"La columna '{val}' ya fue incluida en '{field.action}'")
                    drop_list.append(val)

                elif field.action == "impute":
                    if val in impute_list:
                        raise DSLValidationError(f"La columna '{val}' ya fue incluida en '{field.action}'")
                    impute_list.append(val)

                elif field.action == "scale":
                    if val in scale_list:
                        raise DSLValidationError(f"La columna '{val}' ya fue incluida en '{field.action}'")
                    scale_list.append(val)

                elif field.action == "encode":
                    if val in encode_list:
                        raise DSLValidationError(f"La columna '{val}' ya fue incluida en '{field.action}'")
                    encode_list.append(val)
        
        if input_name is None:
            raise DSLValidationError(f"El campo input debe ser incluido")
        
        if not input_name in self.symbols:
            raise DSLValidationError(f"El datasource '{input_name}' no existe")
        
        if self.symbols[input_name]["kind"] != "datasource":
            raise DSLValidationError(f"'{input_name}' no es un datasource")

    def validate_learner(self, declaration):
        field_names = []
        algorithm_value = None
        supported_algorithms = ["random_forest"]
        for field in declaration.fields:
            if field.name in field_names:
                raise DSLValidationError(f"El campo '{field.name}' ya fue incluido")
            field_names.append(field.name)

            if field.name == "algorithm":
                algorithm_value = field.value

        if algorithm_value is None:
            raise DSLValidationError(f"El campo algorithm debe der incluido")
        
        if algorithm_value not in supported_algorithms:
            raise DSLValidationError(f"Algoritmo '{algorithm_value}' no soportado")
        
        if "parameters" in field_names:
            for field in declaration.fields:
                if field.name == "parameters":
                    self.validate_parameters(algorithm_value, field)

    def validate_parameters(self, algorithm_value, declaration):
        field_names = {}
        allowed_fields = []

        for field in declaration.fields:
            if field.name in field_names:
                raise DSLValidationError(f"El campo '{field.name}' ya fue incluido")
            field_names[field.name] = field.value

        if algorithm_value == "random_forest":
            allowed_fields = ["trees", "depth"]

        for field in field_names:
            if field not in allowed_fields:
                raise DSLValidationError(f"El campo '{field}' no esta permitido en el algoritmo '{algorithm_value}'")

        if "trees" in field_names:
            if not isinstance(field_names["trees"], int):
                raise DSLValidationError(f"El valor de 'trees' debe ser un entero")
            if field_names["trees"] <= 0:
                raise DSLValidationError(f"El valor de 'trees' debe ser mayor a cero")
        if "depth" in field_names:
            if not isinstance(field_names["depth"], int):
                raise DSLValidationError(f"El valor de 'depth' debe ser un entero")
            if field_names["depth"] <= 0:
                raise DSLValidationError(f"El valor de 'depth' debe ser mayor a cero")
            
    def validate_model(self, declaration):
        field_names = {}

        for field in declaration.fields:
            if field.name in field_names:
                raise DSLValidationError(f"El campo '{field.name}' ya fue incluido")
            field_names[field.name] = field.value
        
        required_fields = ["fit", "using", "target"]

        for required in required_fields:
            if required not in field_names:
                raise DSLValidationError(f"El campo '{required}' debe ser incluido en el model")

        learner_name = field_names["fit"]
        using_name = field_names["using"]
        target_name = field_names["target"]

        if learner_name not in self.symbols:
            raise DSLValidationError(f"El learner '{learner_name}' no existe")

        if self.symbols[learner_name]["kind"] != "learner":
            raise DSLValidationError(f"'{learner_name}' no es un learner")

        if using_name not in self.symbols:
            raise DSLValidationError(f"El datasource o preprocess '{using_name}' no existe")

        if self.symbols[using_name]["kind"] not in ["datasource", "preprocess"]:
            raise DSLValidationError(f"'{using_name}' no es un datasource ni un preprocess")

        if not isinstance(target_name, str):
            raise DSLValidationError("El target debe ser el nombre de una columna")
            
        