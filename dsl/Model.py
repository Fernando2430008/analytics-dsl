from sklearn.ensemble import RandomForestClassifier


from dsl.errors import DSLValidationError

class Model:
    name: str
    learner: object
    data: object
    target: str
    trained_model: object

    def __init__(self, name, learner, data, target):
        self.name = name
        self.learner = learner
        self.data = data
        self.target = target
        self.feature_columns = []
        self.trained_model = None

    def prepare_data(self):
        if self.target not in self.data.columns:
            raise DSLValidationError(f"La columna target '{self.target}' no existe en los datos")
    
        X = self.data.drop(columns = [self.target])
        y = self.data[self.target]
        return X,y

    def create_algorithm(self, params):
        if self.learner.algorithm == "random_forest":
            algorithm = RandomForestClassifier(
                n_estimators=params.get("trees", 100),
                max_depth=params.get("depth", 10),
                class_weight="balanced" if params.get("balance", False) else None,
                random_state=params.get("random_state")
            )
            
        else:
            raise DSLValidationError(f"Algoritmo '{self.learner.algorithm}' no soportado")
        
    
        return algorithm

    def train(self, algorithm, X, y):
        algorithm.fit(X, y)
        self.feature_columns = X.columns.tolist()
        self.trained_model = algorithm