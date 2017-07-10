"""

This file includes functionality to generate interfaces



Prompt specification
-------------------

Prompts are specified through dictionaries that include the following
fields:

1. header
2. description
3. inputs:
  [

    a. label
    b. description
    c. help
    d. input type
    e. choices
  ]

Input types
-----------

text (min,maximum, default):
    string between minimum and maximum characters
bool (default):
    a True/False value
radio (['a','b',...'z'], default):
    select one multiple-choice option from list
checkbox (['a','b',...,'z'],minimum,maximum, default)
    select between minimum and maximum items from list
integer (minimum,maximum, default):
    enter a number between minimum and maximum
float (minimum,maximum, default):
    enter a float (decimal) between minimum and maximum
date (minimum, maximum, default):
    enter a date between minimum and maximum
time (minimum, maximum, default):
    enter a time between minimum and maximum

Example
-------

prompt_specification = {
    description = "this is an example of input.
    header = 'Test input'
    just see for yourself."
    inputs = [
        {"label":'enter text', "description":'nothing happens', "help":'', "input_type":'text', "minimum":None, "maximum":None, "default":None} ,
        {"label": 'pick a letter', "description":'any letter', "input_type":'radio', "options":['a','b','c'], "default":'a'},
    ]

}

Should generate something like:

  |-------------------------------------|
  | TEST INPUT                          |
  |-------------------------------------|
  |this is an example of input.         |
  |just see for yourself.               |
  |-------------------------------------|
  | enter text:                         |
  |   nothing happens                   |
  | >                                   |
  | pick a letter:                      |
  |   any letter                        |
  | >                                   |
  |-------------------------------------|


"""

HELP_INDICATORS = ['h','help','?']

def TLI_text(label,minimum=None, maximum=None, default=None, description="", help=None , show_help=False, *args, **kwargs):

    if description or show_help:
        print(label)
        print('\t'+'\t'.join(description.split('\n')))
        if show_help:
            if not help:
                print("HELP: unavailable...")
            else:
                print("HELP: {help}".format(**locals()))

    show_default = default and "(default: {default})".format(**locals()) or ""
    if not minimum and not maximum:
        criteria = ""
    elif minimum and not maximum:
        criteria = "(at least {minimum} characters)".format(**locals())
    elif not minimum and maximum:
        citeria = "(no longer than {maximum} characters)".format(**locals())
    elif minimum and maximum:
        criteria = "(between {minimum} and {maximum} characters)".format(**locals())
    response = input('{show_default}{criteria}> '.format(**locals()))

    if not response and default:
        response = default
    help_requested = [help_found for help_found in HELP_INDICATORS if help_found==response]

    if help_requested:
        show_help=True
        return TLI_text(**locals())

    # validation
    minimum_reached = not type(minimum)==int and True  or len(response) > minimum
    maximum_avoided = not type(maximum)==int and True or len(response) < maximum

    if not minimum_reached or not maximum_avoided:
        print("Please make sure you stick to provided minimum and maximum lengths")
        show_help = True
        return TLI_text(**locals())

    return response

def TLI_bool(label,minimum=None, maximum=None, default=None, description="", help=None , show_help=False, *args, **kwargs):

    if description or show_help:
        print(label)
        print('\t'+'\t'.join(description.split('\n')))
        if show_help:
            if not help:
                print("HELP: unavailable...")
            else:
                print("HELP: {help}".format(**locals()))

    show_default = default and "(default: {default})".format(**locals()) or ""

    response = input('{show_default}> '.format(**locals()))

    if not response and default:
        response = default
    help_requested = [help_found for help_found in HELP_INDICATORS if help_found==response]

    if help_requested:
        show_help=True
        return TLI_text(**locals())

    # validation
    is_bool = response.lower() in ['true','false','t','f']

    if not is_bool:
        print("Please make sure you provide a boolean")
        show_help = True
        return TLI_bool(**locals())

    return response

def TLI_radio(label,minimum=None, maximum=None, default=None, description="", help=None , show_help=False, choices=[],*args, **kwargs):

    if description or show_help:
        print(label)
        print('\t'+'\t'.join(description.split('\n')))
        if show_help:
            if not help:
                print("HELP: unavailable...")
            else:
                print("HELP: {help}".format(**locals()))

    print("Choices:\n\n"+"\n".join(choices)+"\n")

    show_default = default and "(default: {default})".format(**locals()) or ""

    response = input('{show_default}> '.format(**locals()))

    if not response and default:
        response = default

    help_requested = [help_found for help_found in HELP_INDICATORS if help_found==response]

    if help_requested:
        show_help=True
        return TLI_text(**locals())

    cleanresponse = response.lower().strip()

    # validation
    valid_choice = response in choices

    if valid_choice:
        print("Please make sure you stick to provided choices")
        show_help = True
        return TLI_radio(**locals())

    choice = [c for c in choices if c == cleanresponse][0]

    return choice


def TLI_prompt(prompt_specification, verify=False):
    """Starts a text-based user interaction.

    Usefull to prompt users to enter specific information based on
    external resources, such as asking users to enter authentication codes.

    Parameters
    ----------
    prompt_specification : dict
        Dict specifying that to show.
        See prompt_specification for more information.
    verify : Bool [default=False]
        whether users should verify their answers (Y/N) before submission

    """
