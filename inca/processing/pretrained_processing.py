# -*- coding: utf-8 -*-
from ..core.processor_class import Processer
from ..core.basic_utils import dotkeys
import logging
import re
import sys

import joblib
from numpy import ndarray, int64



class pretrained(Processer):
    '''annotated based on pretrained model'''
    
    def process(self, document_field, path_to_model):
        '''classification based on pretrained model'''
        try:
            prediction = self.clf.predict([document_field])
        except AttributeError:
            self.load_model(path_to_model)
            prediction = self.clf.predict([document_field])

        if type(prediction) is ndarray and len(prediction)==1:
            prediction = prediction[0]
        if type(prediction) is int64:
            prediction = int(prediction)
        return prediction

    def load_model(self, path_to_model):
        self.clf = joblib.load(path_to_model)
