from celery import Task


class Analysis(Task):
    def fit(self, documents, add_prediction="", **kwargs):
        """
        This method should train a model on the input documents.\n
        :param documents: the documents (dictionaries) to train on
        :type documents: iterable
        :param add_prediction: this switch signals the mutation of the train set documents by adding a key, value pair document.\
                               If given (add_prediction != ''), then key=add_prediction and value should be the model's output:
                                 * For classification tasks: class labels
                                 * For clustering tasks: assigned cluster
        :type add_prediction: str
        """
        raise NotImplementedError

    def predict(self, documents, add_prediction="", **kwargs):
        """
        This method should perform inference on new unseen documents.\n
        :param documents: the documents (dictionaries) to perform inference on
        :type documents: iterable
        :param add_prediction: this switch signals the mutation of the given documents by adding a key, value pair document.\
                               If given (add_prediction != ''), then key=add_prediction and value should be the model's output:\n
                                 * For classification tasks: class labels\n
                                 * For clustering tasks: assigned cluster\n
        :type add_prediction: str
        """
        raise NotImplementedError

    def update(self, documents, **kwargs):
        """
        This method should provide online training functionality. In most cases this should basically result in some weight updating based on new evidence.\n
        :param documents: the documents (dictionaries) presented as new evidence to the model. Expected functionality for weight updating
        :type documents: iterable
        """
        raise NotImplementedError

    def interpretation(self, **kwargs):
        """
        This method should have the functionality to interpret the status of the model after being trained and also document the various design choices\
        (i.e. parameters settings, assumptions, model selection, test method, dataset used). For example it can return a report-like looking formatted string.\n
        Please consider the following as possible model state interpretation:
           * For classification tasks depending on the underlying model: coeficient/feature weights, feature selection (random forest)
           * For clustering tasks: clusterings members/structure, distributions
        """
        raise NotImplementedError

    def quality(self, **kwargs):
        """
        This method should have the functionality to report on the quality of the underlying (trained) model used for the analysis (on a dataset):
           * For classification tasks: retrieval metrics precision, recall, f1-score on a test set internally handled; intrinsic evaluation on hidden evidence.
           * For clustering tasks take into consideration application and underlying clustering method since it optimizes against given metric. Example metrics:\n
             - inertia: sum of squared distance for each point to it's closest centroid, i.e., its assigned cluster.
             - silhouette
        """
        raise NotImplementedError

    def plot(self, figure_names, **kwargs):
        """
        This method should write one or more figure files on disk, visualing the model and its behaviour.
           * For classification tasks:\n
             - ROC curve: plot the true positive rate against the false positive rate at various threshold settings.\n
             - pre-rec curve: shows the tradeoff between precision and recall at various threshold settings.\n
           * For clustering/unsupervised tasks:\n
             - a 2D visualization of the data reduced to 2D\n
        :param figure_names: the file paths to save the created figures to
        :type figure_names: iterable
        """
        raise NotImplementedError

    def runwrap(self, action="run", *args, **kwargs):
        """
        Call the task as either a local or distributed process
        """
        if action == "run":
            return self.run(*args, **kwargs)

        if action == "delay":
            return self.delay(*args, **kwargs)

    def run(self, *args, **kwargs):
        self.fit(*args, **kwargs)
        # self.predict(*args,**kwargs)
        self.quality(*args, **kwargs)
        self.interpetation(*args, **kwargs)
