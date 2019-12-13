import os as _os
from importlib import import_module

_expected_file_end = ".py"

__all__ = [
    fname
    for fname in _os.listdir("importers_exporters")
    if fname[-len(_expected_file_end) :] == _expected_file_end
    and not fname.startswith(".")
]

for module in __all__:
    # __import__('.'.join(['importers_exporters',module.replace('.py','')]))
    import_module("." + module.replace(".py", ""), package="inca.importers_exporters")
