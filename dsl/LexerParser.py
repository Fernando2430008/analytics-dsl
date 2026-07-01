import ply.lex as lex
import ply.yacc as yacc

from dsl.errors import DSLValidationError, DSLSyntaxError
from dsl.ast import ProgramNode, DataSourceNode, DataSourceFieldNode, PreprocessNode, PreprocessSimpleFieldNode, PreprocessFieldNode, LearnerNode, LearnerFieldNode, LearnerParametersNode, ParameterAssignmentNode
from dsl.semantic_analyzer import SemanticAnalyzer

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
    
    def p_learner_parameter_body_fild(self, p):
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
    ################################################
    #####            evaluate                  #####
    ################################################
    #####            predict                   #####
    ################################################
    #####           Extra rules                #####
    def p_value_bool(self, p):
        """value : TRUE
                | FALSE"""
        if p[1] == "true":
            p[0] = "TRUE"
        else:
            "FALSE"
            p[0] = "FALSE"
    
    def p_string_list(self, p):
        """list_strings : list_strings COMMA STRING
                        | STRING"""
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
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
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