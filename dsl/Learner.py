from dataclasses import dataclass
from typing import Any

class Learner():
    name:str
    algorithm:str
    parameters:list
    
    def __init__(self, name, algorithm, parameters):
        self.name = name
        self.algorithm = algorithm
        self.parameters = parameters
    
    def get_parameters_dict(self):
        params = {}

        for parameter in self.parameters:
            params[parameter.name] = parameter.value

        return params

@dataclass
class LearnerParameter():
    name:str
    value:Any

