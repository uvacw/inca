from ..core.processor_class import Processer
import logging
import random

logger = logging.getLogger("INCA")


class randomfield(Processer):
    """adds a random field"""

    def process(self, field=None, choiceset=[0, 1]):
        """random field"""
        return random.choice(choiceset)
