import ply.lex as lex
import ply.yacc as yacc

from dsl.ast import ProgramNode, DataSourceNode, DataSourceFieldNode, PreprocessNode, PreprocessSimpleFieldNode, PreprocessFieldNode, LearnerNode, LearnerFieldNode, LearnerParametersNode, ParameterAssignmentNode, ModelNode, ModelFieldNode, EvaluateNode, EvaluateFieldNode, EvaluateSplitNode, SplitAssignmentNode, PredictNode, PredictFieldNode, FunctionNode
from dsl.semantic_analyzer import SemanticAnalyzer
from dsl.Executor import Interpreter

class LexerParser:
    reserved = {
        #Palabras reservadas principales
        'datasource':'DATASOURCE',
        'preprocess':'PREPROCESS',
        'learner':'LEARNER',
        'model':'MODEL',
        'evaluate':'EVALUATE',
        'predict':'PREDICT',

        'fit':'FIT',
        'using':'USING',
        'input':'INPUT',
        'target':'TARGET',

        'type':'TYPE',
        'location':'LOCATION',

        'algorithm':'ALGORITHM',
        'parameters':'PARAMETERS',

        'drop':'DROP',
        'impute':'IMPUTE',
        'scale':'SCALE',
        'encode':'ENCODE',

        'metrics':'METRICS',

        'split':'SPLIT',
        'train':'TRAIN',
        'test':'TEST',
        'validation':'VALIDATION',
        'folds':'FOLDS',
        'stratify':'STRATIFY',
        'true':'TRUE',
        'false':'FALSE',
        'random_state':'RANDOM_STATE',

        'list' : 'LIST', # Usado para el listado de datasources
        'show' : 'SHOW', # Mostrar cabeceras de informacion
        'info' : 'INFO',
        'config' : 'CONFIG',
        'delete' : 'DELETE',
        'objects' : 'OBJECTS',

        #Posibles integraciones
        'optimize':'OPTIMIZE', # Necesita algoritmos de busqueda, ej: grid search, random search o Bayesian Optimization
        'save_to':'SAVE_TO', # Forma de guardar predicciones
        'expect':'EXPECT',   # Reglas para datos
        'export':'EXPORT', # Exportacion del modelo
    }
        
    tokens = ['LPAREN', 'RPAREN', 'EQUALS', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE',
        'COMMA', 'GREATER','LESS', 'ID', 'STRING', 'NUMBER', 'COMMENT'] + list(reserved.values())

    # Constructor
    def __init__(self):
        # Inicializar el lex y yacc
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)
        self.semantic_analyzer = SemanticAnalyzer()
        self.interpreter = Interpreter()
    
    ###############################################
    #               Reglas lexicas                #
    ###############################################
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_EQUALS = r'='
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_GREATER = r'>'
    t_LESS = r'<'

    t_ignore = ' \t' # Ignorar espacios y tabulaciones

    def t_COMMENT (self, t):
        r'\#.*'
        pass

    def t_ID (self, t):
        r'[a-zA-Z_]\w*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_STRING (self, t):
        r'"[^"]*"'
        t.value = t.value[1:-1]
        return t

    def t_NUMBER (self, t):
        r'-?\d+(\.\d+)?'
        if "." in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"Caracter no valido '{t.value[0]}'")
        t.lexer.skip(1)


    ###############################################
    #        Reglas gramaticales                  #
    ###############################################
    #####            Programa                 #####
    def p_program (self, p):
        '''program : declarations'''
        p[0] = ProgramNode(declarations=p[1])

    def p_declarations_multiple(self, p):
        '''declarations : declarations declaration'''
        p[0] = p[1] + [p[2]]

    def p_declarations_single(self, p):
        """declarations : declaration"""
        p[0] = [p[1]]
        
    ################################################
    #####            Datasource                #####
    def p_declaration_datasource(self, p):
        """declaration : DATASOURCE ID LBRACE datasource_body RBRACE"""
        p[0] = DataSourceNode(
            name=p[2],
            fields=p[4]
        )

    def p_datasource_body_multiple(self, p):
        """datasource_body : datasource_body datasource_field"""
        p[0] = p[1] + [p[2]]

    def p_datasource_body_single(self, p):
        """datasource_body : datasource_field"""
        p[0] = [p[1]]

    def p_datasource_field_type(self, p):
        """datasource_field : TYPE ID"""
        p[0] = DataSourceFieldNode(
            name = "type",
            value = p[2]
        )

    def p_datasource_field_location(self, p):
        """datasource_field : LOCATION STRING"""
        p[0] = DataSourceFieldNode(
            name = "location",
            value = p[2]
        )

    ################################################
    #####            Preprocess                #####
    def p_declaration_preprocess(self, p):
        """declaration : PREPROCESS ID LBRACE preprocess_body RBRACE"""
        p[0] = PreprocessNode(
            name = p[2],
            fields = p[4]
        )
    
    def p_preprocess_body_multiple(self, p):
        """preprocess_body : preprocess_body preprocess_field"""
        p[0] = p[1] + [p[2]]
    
    def p_preprocess_body_single(self, p):
        """preprocess_body : preprocess_field"""
        p[0] = [p[1]]
    
    def p_preprocess_field_input(self, p):
        """preprocess_field : INPUT ID"""
        p[0] = PreprocessSimpleFieldNode(
            action = p[1],
            value = p[2]
        )

    def p_preprocess_field_drop(self, p):
        """preprocess_field : DROP LBRACKET list_strings RBRACKET"""
        p[0] = PreprocessSimpleFieldNode(
            action = p[1],
            value = p[3]
        )
    
    def p_preprocess_field_impute(self, p):
        """preprocess_field : IMPUTE ID LBRACKET list_strings RBRACKET"""
        p[0] = PreprocessFieldNode(
            action = p[1],
            type = p[2],
            value = p[4]
        )
    
    def p_preprocess_field_scale(self,p):
        """preprocess_field : SCALE ID LBRACKET list_strings RBRACKET"""
        p[0] = PreprocessFieldNode(
            action = p[1],
            type = p[2],
            value = p[4]
        )
    
    def p_preprocess_field_encode(self, p):
        """preprocess_field : ENCODE ID LBRACKET list_strings RBRACKET"""
        p[0] = PreprocessFieldNode(
            action = p[1],
            type = p[2],
            value = p[4]
        )

    ################################################
    #####            learner                   #####
    def p_declaration_learner(self, p):
        """declaration : LEARNER ID LBRACE learner_body RBRACE"""
        p[0] = LearnerNode(
            name = p[2],
            fields = p[4]
        )

    def p_learner_body_multiple(self, p):
        """learner_body : learner_body learner_field"""
        p[0] = p[1] + [p[2]]

    def p_learner_body_single(self, p):
        """learner_body : learner_field"""
        p[0] = [p[1]]

    def p_learner_field_algorithm(self, p):
        """learner_field : ALGORITHM ID"""
        p[0] = LearnerFieldNode(
            name = p[1],
            value = p[2]
        )
    
    def p_learner_parameter_body_field(self, p):
        """learner_field : PARAMETERS LBRACE learner_parameter_body RBRACE"""
        p[0] = LearnerParametersNode(
            name = p[1],
            fields = p[3]
        )
    
    def p_learner_parameter_body_multiple(self, p):
        """learner_parameter_body : learner_parameter_body learner_parameter_field"""
        p[0] = p[1] + [p[2]]
    
    def p_learner_parameter_body_single(self, p):
        """learner_parameter_body : learner_parameter_field"""
        p[0] = [p[1]]

    def p_learner_parameter_field_assignment(self, p):
        """learner_parameter_field : ID EQUALS NUMBER"""
        p[0] = ParameterAssignmentNode(
            name = p[1],
            value = p[3]
        )

    ################################################
    #####            model                     #####
    def p_declaration_model(self, p):
        """declaration : MODEL ID LBRACE model_body RBRACE"""
        p[0] = ModelNode (
            name = p[2],
            fields = p[4]
        )
    
    def p_model_body_multiple(self, p):
        """model_body : model_body model_field"""
        p[0] = p[1] + [p[2]]
    
    def p_model_body_single(self, p):
        """model_body : model_field"""
        p[0] = [p[1]]
    
    def p_model_field_fit(self, p):
        """model_field : FIT ID"""
        p[0] = ModelFieldNode (
            name = p[1],
            value = p[2]
        )
    
    def p_model_field_using(self, p):
        """model_field : USING ID"""
        p[0] = ModelFieldNode (
            name = p[1],
            value = p[2]
        )
    
    def p_model_field_target(self, p):
        """model_field : TARGET ID"""
        p[0] = ModelFieldNode (
            name = p[1],
            value = p[2]
        )
    ################################################
    #####            evaluate                  #####
    def p_declaration_evaluate (self, p):
        """declaration : EVALUATE ID LBRACE evaluate_body RBRACE"""
        p[0] = EvaluateNode (
            name = p[2],
            fields = p[4]
        )
    
    def p_evaluate_body_multiple (self, p):
        """evaluate_body : evaluate_body evaluate_field"""
        p[0] = p[1] + [p[2]]
    
    def p_evaluate_body_single (self, p):
        """evaluate_body : evaluate_field"""
        p[0] = [p[1]]
    
    def p_evaluate_field_models(self, p):
        """evaluate_field : MODEL ID"""
        p[0] = EvaluateFieldNode (
            name = p[1],
            value = p[2]
        )

    def p_evaluate_field_datasource (self, p):
        """evaluate_field : DATASOURCE ID"""
        p[0] = EvaluateFieldNode (
            name = p[1],
            value = p[2]
        )
    
    def p_evaluate_split_body_field(self, p):
        """evaluate_field : SPLIT ID LBRACE evaluate_split_body RBRACE"""
        p[0] = EvaluateSplitNode (
            name = p[1],
            type = p[2],
            fields = p[4]
        )
    
    def p_evaluate_split_body_multiple (self, p):
        """evaluate_split_body : evaluate_split_body evaluate_split_field"""
        p[0] = p[1] + [p[2]]
    
    def p_evaluate_split_body_single(self, p):
        """evaluate_split_body : evaluate_split_field"""
        p[0] = [p[1]]
    
    def p_evaluate_split_field_number(self, p):
        """evaluate_split_field : TRAIN NUMBER
                                | TEST NUMBER
                                | FOLDS NUMBER
                                | RANDOM_STATE NUMBER"""
        p[0] = SplitAssignmentNode(
            name = p[1],
            value = p[2]
        )

    def p_evaluate_split_field_stratify(self, p):
        """evaluate_split_field : STRATIFY value"""
        p[0] = SplitAssignmentNode(
            name = p[1],
            value = p[2]
        )
    
    def p_evaluate_field_metrics (self, p):
        """evaluate_field : METRICS LBRACKET id_list RBRACKET"""
        p[0] = EvaluateFieldNode (
            name = p[1],
            value = p[3]
        )

    ################################################
    #####            predict                   #####
    def p_declaration_predict(self, p):
        """declaration : PREDICT ID LBRACE predict_body RBRACE"""
        p[0] = PredictNode (
            name = p[2],
            fields = p[4]
        )
    
    def p_predict_body_multiple(self, p):
        """predict_body : predict_body predict_field"""
        p[0] = p[1] + [p[2]]
    
    def p_predict_body_single(self, p):
        """predict_body : predict_field"""
        p[0] = [p[1]]
    
    def p_predict_field_model(self, p):
        """predict_field : MODEL ID"""
        p[0] = PredictFieldNode (
            name = p[1],
            value = p[2]
        )
    
    def p_predict_field_datasource(self, p):
        """predict_field : DATASOURCE ID"""
        p[0] = PredictFieldNode (
            name = p[1],
            value = p[2]
        )
    
    def p_predict_field_save_to(self, p):
        """predict_field : SAVE_TO STRING"""
        p[0] = PredictFieldNode (
            name = p[1],
            value = p[2]
        )

    ################################################
    #####           Extra functions            #####

    def p_function_list_objects(self, p):
        """declaration : LIST list_type"""
        p[0] = FunctionNode(
            action=p[1],
            option=p[2]
        )

    def p_list_type(self, p):
        """list_type : OBJECTS
                    | DATASOURCE
                    | PREPROCESS
                    | LEARNER
                    | MODEL
                    | EVALUATE
                    | PREDICT"""
        p[0] = p[1]
    
    def p_function_delete_object(self, p):
        """declaration : DELETE ID"""
        p[0] = FunctionNode (
            action = p[1],
            target = p[2]
        )
    
    def p_function_show_config_info(self, p):
        """declaration : SHOW CONFIG ID"""
        p[0] = FunctionNode (
            action = p[1],
            option = p[2],
            target = p[3]
        )
    
    ####                 data                   ####
    def p_function_show_data_info (self, p):
        """declaration : SHOW INFO ID"""
        p[0] = FunctionNode (
            action= p[1],
            option = p[2],
            target = p[3]
        )


    ################################################
    #####           Extra rules                #####
    def p_value_bool(self, p):
        """value : TRUE
                | FALSE"""
        p[0] = p[1] == "true"
    
    def p_string_list(self, p):
        """list_strings : list_strings COMMA STRING
                        | STRING"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_id_list (self, p):
        """id_list : id_list COMMA ID
                    | ID"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_error(self, p):
        if p:
            print(
                f"Syntax error at "
                f"'{p.value}' line {p.lineno}"
            )
        else:
            print("Unexpected EOF")

    #############################################
    #         Metodos de clase                  #
    #############################################

    def parse(self, code_string):
        ast = self.parser.parse(code_string, lexer = self.lexer)
        self.semantic_analyzer.analyze(ast)
        self.interpreter.execute(ast)
        return ast
    
    # Funcion unicamente para probar el analizador
    def run(self):
        print("Comenzando analizador, presiona CTRL + C para salir")
        while True:
            try:
                code = input('Entrada > ')
            except EOFError:
                break
            if not code:
                continue
            ast = self.parse(code)
            print(ast)