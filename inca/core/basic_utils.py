'''
This file contains some basic utilities:

1. dotkeys(dict, key_string) : allows the use of .-separated nested fields such as 'name.firstname' as dict[name][firstname]

'''

def dotkeys(doc, key_string):
    '''returns the (nested) field specified by the key_string from the doc '''
    if type(key_string)!= list:
        keys = key_string.split('.')
    else:
        keys = key_string
    if not keys:
        return doc
    field = keys.pop(0)
    result = doc.get(field,{})
    if len(keys)>0 and type(result)==dict:
        return dotkeys(result,keys)
    else:
        return result
