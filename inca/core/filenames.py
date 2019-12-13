"""
This file provides utilities for generating file names
for data import and export and related tasks
"""

from urllib.parse import quote_plus
from hashlib import md5


def id2filename(id):
    """create a filenmame for exporting docments.                                                                                                 
                                                                                                                                                  
    In principle, documents should be saved as {id}.json. However, as ids can                                                                     
    be arbitrary strings, filenames can (a) be too long or (b) contain illegal                                                                    
    characters like '/'. This function takes care of this                                                                                         
    """

    encoded_filename = quote_plus(id)  # use URL encoding to get rid of illegal chacters

    if len(encoded_filename) > 132:
        # many filenames allow a maximum of 255 bytes as file name. However, on
        # encrypted file systems, this can be much lower. Therefore, we play safe
        hashed_filename = md5(encoded_filename.encode("utf-8")).hexdigest()
        return encoded_filename[:100] + hashed_filename
    else:
        return encoded_filename
