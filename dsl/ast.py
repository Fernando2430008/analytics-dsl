from typing import Any
from dataclasses import dataclass

# Prorgrama
@dataclass
class ProgramNode():
    declarations: list

###########################
#  Clases de datasources  #
@dataclass
class DataSourceNode():
    name:str
    fields:list

@dataclass 
class DataSourceFieldNode():
    name:str
    value:Any

###########################
#  Clases de preprocess   #
@dataclass
class PreprocessNode():
    name:str
    fields:list

@dataclass
class PreprocessSimpleFieldNode():
    action:str
    value:Any

@dataclass
class PreprocessFieldNode():
    action:str
    type:str
    value:Any

###########################
#  Clases de learner      #
@dataclass
class LearnerNode():
    name:str
    fields:list

@dataclass
class LearnerFieldNode():
    name:str
    value:str

@dataclass
class LearnerParametersNode():
    name:str
    fields:list

@dataclass
class ParameterAssignmentNode():
    name:str
    value:Any


###########################
#  Clases de model        #

@dataclass
class ModelNode():
    name:str
    fields:list

@dataclass 
class ModelFieldNode():
    name:str
    value:str

###########################
#  Clases de evaluate     #

@dataclass
class EvaluateNode():
    name:str
    fields:list

@dataclass
class EvaluateFieldNode():
    name:str
    value:Any

@dataclass
class EvaluateSplitNode():
    name:str
    type:str
    fields:list

@dataclass
class SplitAssignmentNode():
    name:str
    value:Any

###########################
#  Clases de predict      #
@dataclass
class PredictNode():
    name:str
    fields:list

@dataclass
class PredictFieldNode():
    name:str
    value:str