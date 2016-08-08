import os as _os

_expected_file_end = "_client.py"

__all__ = [fname for fname in _os.listdir('clients') if fname[-len(_expected_file_end):]==_expected_file_end]

for module in __all__:
    __import__('.'.join(['clients',module.replace('.py','')]))