import os as _os
from importlib import import_module
_expected_file_end = "_scraper.py"

__all__ = [fname for fname in _os.listdir('scrapers') if fname[-len(_expected_file_end):]==_expected_file_end and not fname.startswith('.')]

for module in __all__:
    #__import__('.'.join(['scrapers',module.replace('.py','')]))
    import_module('.'+module.replace('.py',''), package='inca.scrapers')
    
