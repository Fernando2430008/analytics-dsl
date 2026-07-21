from dsl.errors import DSLValidationError

class Predict():
    name:str
    model:object
    data:object
    save_to: str | None
    predictions:object

    def __init__(self, name, model, data, save_to):
        self.name = name
        self.model = model
        self.data = data
        self.save_to = save_to
        self.predictions = None  

    def prepare_data(self):
        if self.model.target in self.data.columns:
            X = self.data.drop(columns = [self.model.target])
        else:
            X = self.data.copy()
        
        return X
    
    def validate_columns(self, X):
        columns_list = self.model.feature_columns

        for column in columns_list:
            if column not in X:
                raise DSLValidationError(f"La columna '{column}' debe estar en el nuevo datasource/preprocess a predecir")
        for column in X:
            if column not in columns_list:
                raise DSLValidationError(f"La columna '{column}' no fue utilizada para entrenamiento de '{self.model.name}'")

    def save_predictions(self):
        result = self.data.copy()

        if "prediction" in result.columns:
            raise DSLValidationError("Ya existe una columna llamada 'prediction'")

        result["prediction"] = self.predictions

        try:
            result.to_csv(self.save_to, index=False)
        except OSError as error:
            raise DSLValidationError(f"No se pudo guardar el archivo en '{self.save_to}'") from error

    def run(self):
        if self.model.trained_model is None:
            raise DSLValidationError(f"El model '{self.model.name}' no fue entrenado")

        X = self.prepare_data()
        self.validate_columns(X)
        X = X[self.model.feature_columns]
        self.predictions = self.model.trained_model.predict(X)

        if self.save_to is not None:
            self.save_predictions()

        return self.predictions