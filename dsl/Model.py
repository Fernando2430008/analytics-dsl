from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from pandas.api.types import is_numeric_dtype

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

        non_numeric_columns = []
        for column in X.columns:
            if not is_numeric_dtype(X[column]):
                non_numeric_columns.append(column)
        
        if non_numeric_columns:
            columns = ", ".join(non_numeric_columns)
            raise DSLValidationError(f"Las columnas '{columns}' deben codificarse antes de entrenar el modelo")
        return X,y

    def create_algorithm(self, params):
        if self.learner.algorithm == "random_forest":
            algorithm = RandomForestClassifier(
                n_estimators=params.get("trees", 100),
                max_depth=params.get("depth", 10),
                class_weight="balanced" if params.get("balance", False) else None,
                random_state=params.get("random_state")
            )
        elif self.learner.algorithm == "logistic_regression":
            algorithm = LogisticRegression(
                C=params.get("c", 1.0),
                max_iter=params.get("iterations", 1000),
                class_weight="balanced" if params.get("balance", False) else None,
                random_state=params.get("random_state")
            )
        elif self.learner.algorithm == "hist_gradient_boosting":
            algorithm = HistGradientBoostingClassifier(
                max_iter=params.get("iterations", 100),
                learning_rate=params.get("learning_rate", 0.1),
                max_depth=params.get("depth"),
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