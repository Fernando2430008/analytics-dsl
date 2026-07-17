from dataclasses import dataclass

class Evaluate():
    name:str
    model:object
    datasource:object
    split:object
    metrics:list
    results:dict

    def __init__(self, name, model, datasource, split, metrics):
        self.name = name
        self.model = model
        self.datasource = datasource
        self.split = split
        self.metrics = metrics
        self.results = {}
    
    def prepare_data(self):
        target = self.model.target
        X = self.datasource.drop(columns=[target])
        y = self.datasource[target]
        return X, y

@dataclass
class Split():
    type:str
    fields:dict
