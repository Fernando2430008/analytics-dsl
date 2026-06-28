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

    #hola como estas pr