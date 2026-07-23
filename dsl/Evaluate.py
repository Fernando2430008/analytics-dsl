from dataclasses import dataclass
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.base import clone
from sklearn.metrics import get_scorer

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
    
    def run_cross_validation(self, X, y):
        splitter = self.split.create_splitter_cv()
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
    
    def run_holdout(self, X, y):
        X_train, X_test, y_train, y_test = self.split.create_splitter_h(X,y)
        scoring = self.get_scoring()

        model_copy = clone(self.model.trained_model)
        model_copy.fit(X_train, y_train)

        results = {}
        for metric, scoring_name in zip(self.metrics, scoring):
            scorer = get_scorer(scoring_name)
            score = scorer(model_copy, X_test, y_test)
            results[metric] = {"score": score}
        
        self.results = results
        
        return results

    def run(self):
        X, y = self.prepare_data()

        if self.split.type == "cross_validation":
            results = self.run_cross_validation(X, y)
        elif self.split.type == "holdout":
            results = self.run_holdout(X,y)

        return results

@dataclass
class Split():
    type:str
    fields:dict

    def create_splitter_cv(self):
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
    
    def create_splitter_h(self, X, y):
        train_size = self.fields["train"]
        test_size = self.fields["test"]
        random_state = self.fields.get("random_state")
        stratify = self.fields.get("stratify", False)

        stratify_data = y if stratify else None

        X_train, X_test, y_train, y_test = train_test_split(X, 
                                                            y, 
                                                            train_size = train_size, 
                                                            test_size = test_size, 
                                                            random_state = random_state, 
                                                            stratify = stratify_data)

        return X_train, X_test, y_train, y_test

