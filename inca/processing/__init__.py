import os as _os
from importlib import import_module

_expected_file_end = "_processing.py"

__all__ = [
    fname
    for fname in _os.listdir("processing")
    if fname[-len(_expected_file_end) :] == _expected_file_end
]

# print(__all__)
for module in __all__:
    # __import__('.'.join(['processing',module.replace('.py','')]))
    import_module("." + module.replace(".py", ""), package="inca.processing")
