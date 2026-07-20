from dataclasses import dataclass
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.model_selection import cross_validate

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
    
    def get_scoring(self):
        metric_names = {
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "auc": "roc_auc"
        }
        
        scoring = []

        for metric in self.metrics:
            scoring.append(metric_names[metric])

        return scoring
    
    def calculate_results(self, scores, scoring):
        results = {}

        for metric, scoring_name in zip(self.metrics, scoring):
            fold_scores = scores[f"test_{scoring_name}"]

            results[metric] = {
                "mean": fold_scores.mean(),
                "std": fold_scores.std(),
                "folds": fold_scores.tolist()
            }
        
        return results

    def run(self):
        X, y = self.prepare_data()
        splitter = self.split.create_splitter()
        scoring = self.get_scoring()

        scores = cross_validate(
            estimator = self.model.trained_model,
            X = X,
            y = y,
            cv = splitter,
            scoring = scoring,
            error_score = "raise"
        )

        results = self.calculate_results(scores, scoring)
        self.results = results
        return results

@dataclass
class Split():
    type:str
    fields:dict

    def create_splitter(self):
        folds = self.fields["folds"]
        stratify = self.fields.get("stratify", False)
        random_state = self.fields.get("random_state")

        shuffle = random_state is not None

        if stratify:
            return StratifiedKFold(
                n_splits = folds,
                shuffle = shuffle,
                random_state = random_state
            )

        return KFold(
            n_splits = folds,
            shuffle = shuffle,
            random_state = random_state
        )
