import os as _os

_expected_file_end = "_processing.py"

__all__ = [fname for fname in _os.listdir('processing') if fname[-len(_expected_file_end):]==_expected_file_end]

for module in __all__:
    __import__('.'.join(['processing',module.replace('.py','')]))
