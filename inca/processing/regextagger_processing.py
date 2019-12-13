# -*- coding: utf-8 -*-
from ..core.processor_class import Processer
import logging
import re


logger = logging.getLogger("INCA")


class regex_tagger(Processer):
    """Creates a tag that is either True or False, depending on whether regex is found
    """

    def process(self, document_field, regex, **kwargs):
        """is regex mentioned?"""

        r = re.compile(regex)

        if r.findall(document_field):
            return True
        else:
            return False
