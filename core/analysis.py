

class Analysis:

    def fit(self, data, **kwargs):
        """This method should train a model on the input documents"""
        raise NotImplementedError

    def predict(self, document):
        """This method should perform inference on a new unseen document"""
        raise NotImplementedError

    def update(self, data):
        """This method should provide online training functionality"""
        raise NotImplementedError

    def persist():
        """This method should save/pickle the object"""
        raise NotImplementedError

    def report():
        """This method should provide an interpretable string representation of the models output"""
        raise NotImplementedError

    def plot():
        """This method should write a figure file on disk visualing the model output"""
        raise NotImplementedError
