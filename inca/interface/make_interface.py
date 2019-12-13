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
    e. options
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

```python
prompt_specification = dict(
    description = "this is an example of input.\njust see for yourself.",
    header = "Test input",
    inputs = [
        {"label":'enter text', "description":'nothing happens', "help":'', "input_type":'text', "minimum":None, "maximum":None, "default":None} ,
        {"label": 'pick a letter', "description":'any letter', "input_type":'radio', "options":['a','b','c'], "default":'a'},
    ]

)
TLI.prompt(prompt_specification)
```

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
import time
from collections import OrderedDict
import logging

logger = logging.getLogger("INCA.%s" % __name__)


class noprompt:
    def prompt(*args, **kwargs):
        logger.warning("Prompt required, but disabled")


class TLI:

    HELP_INDICATORS = ["h", "help", "?"]

    def TLI_text(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        *args,
        **kwargs
    ):

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        show_default = default and "(default: '{default}')\n".format(**locals()) or ""
        if not minimum and not maximum:
            criteria = ""
        elif minimum and not maximum:
            criteria = "(at least {minimum} characters)".format(**locals())
        elif not minimum and maximum:
            criteria = "(no longer than {maximum} characters)".format(**locals())
        elif minimum and maximum:
            criteria = "(between {minimum} and {maximum} characters)".format(**locals())
        response = input("{show_default}{criteria}\n> ".format(**locals()))

        if not response and default:
            response = default
        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # validation
        minimum_reached = not type(minimum) == int and True or len(response) > minimum
        maximum_avoided = not type(maximum) == int and True or len(response) < maximum

        if not minimum_reached or not maximum_avoided:
            print("Please make sure you stick to provided minimum and maximum lengths")
            show_help = True
            return TLI.TLI_text(**locals())

        return response

    def TLI_bool(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        *args,
        **kwargs
    ):

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        show_default = default and "(default: {default})".format(**locals()) or ""

        response = input("{show_default}> ".format(**locals()))

        if not response and default:
            response = default
        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # validation
        is_bool = response.lower() in ["true", "false", "t", "f"]

        if not is_bool:
            print("Please make sure you provide a boolean")
            show_help = True
            return TLI.TLI_bool(**locals())

        return response

    def TLI_radio(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        options=[],
        *args,
        **kwargs
    ):

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        print("Choices:\n\n" + "\n".join(options) + "\n")

        show_default = default and "(default: {default})".format(**locals()) or ""

        response = input("{show_default}> ".format(**locals()))

        if not response and default:
            response = default

        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        cleanresponse = response.lower().strip()

        # validation
        valid_choice = response in options

        if not valid_choice:
            print("Please make sure you stick to provided options")
            print("You specified {response}".format(**locals()))
            show_help = True
            return TLI.TLI_radio(**locals())

        choice = [c for c in options if c.lower().strip() == cleanresponse][0]

        return choice

    def TLI_checkbox(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        options=[],
        *args,
        **kwargs
    ):

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))
                    print("Choices:\n\n" + "\n".join(options) + "\n")

        show_default = default and "(default: {default})".format(**locals()) or ""
        if not minimum and not maximum:
            criteria = ""
        elif minimum and not maximum:
            criteria = "(at least {minimum} choice)".format(**locals())
        elif not minimum and maximum:
            citeria = "(no longer than {maximum} options)".format(**locals())
        elif minimum and maximum:
            criteria = "(between {minimum} and {maximum} options)".format(**locals())
        response = input(
            "{show_default}{criteria} separated by ", "> ".format(**locals())
        )

        if not response and default:
            response = default
        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # interpretation
        cleanoptions = [choice.lower().strip() for choice in response.split(",")]
        validoptions = [choice for choice in options if choice.lower() in cleanoptions]

        # validation
        minimum_reached = len(validoptions) > minimum
        maximum_avoided = len(validoptions) < maximum

        if not minimum_reached or not maximum_avoided:
            print("Please make sure you stick to provided minimum and maximum options")
            print("You provided:")
            for n, c in enumerate(validoptions):
                print(n + 1, ". ", c)
            show_help = True
            return TLI.TLI_text(**locals())

        return response

    def TLI_integer(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        *args,
        **kwargs
    ):

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        show_default = default and "(default: {default})".format(**locals()) or ""
        if not minimum and not maximum:
            criteria = ""
        elif minimum and not maximum:
            criteria = "(at least {minimum})".format(**locals())
        elif not minimum and maximum:
            citeria = "(no longer than {maximum})".format(**locals())
        elif minimum and maximum:
            criteria = "(between {minimum} and {maximum})".format(**locals())
        response = input("{show_default}{criteria}> ".format(**locals()))

        if not response and default:
            response = default

        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # validation
        try:
            response = int(response.strip())
            correct_type = True
        except ValueError:
            correct_type = False

        minimum_reached = correct_type and response >= minimum
        maximum_avoided = correct_type and response <= maximum

        if not correct_type or not minimum_reached or not maximum_avoided:
            print(
                "Please provide an integer (1,2,3,4..) between the minimum and maximum"
            )
            show_help = True
            return TLI.TLI_text(**locals())

        return response

    def TLI_float(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        *args,
        **kwargs
    ):

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        show_default = default and "(default: {default})".format(**locals()) or ""
        if not minimum and not maximum:
            criteria = ""
        elif minimum and not maximum:
            criteria = "(at least {minimum})".format(**locals())
        elif not minimum and maximum:
            citeria = "(no longer than {maximum})".format(**locals())
        elif minimum and maximum:
            criteria = "(between {minimum} and {maximum})".format(**locals())
        response = input("{show_default}{criteria}> ".format(**locals()))

        if not response and default:
            response = default

        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # validation
        try:
            response = float(response.strip())
            correct_type = True
        except ValueError:
            correct_type = False

        minimum_reached = correct_type and response >= minimum
        maximum_avoided = correct_type and response <= maximum

        if not correct_type or not minimum_reached or not maximum_avoided:
            print(
                "Please provide an decimal (1.1, 3.4, ...) between the minimum and maximum"
            )
            show_help = True
            return TLI.TLI_text(**locals())

        return response

    def TLI_date(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        *args,
        **kwargs
    ):
        def extract_date(string_input):
            try:
                return time.strptime(string_input, "%d-%m-%Y")
            except ValueError:
                return False

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        show_default = default and "(default: {default})".format(**locals()) or ""
        if not minimum and not maximum:
            criteria = ""
        elif minimum and not maximum:
            minimum = extract_date(minimum)
            maximum = extract_date("31-12-6000")
            criteria = "(at least {minimum})".format(**locals())
        elif not minimum and maximum:
            minimum = extract_date("01-01-0001")
            maximum = extract_date(maximum)
            citeria = "(no longer than {maximum})".format(**locals())
        elif minimum and maximum:
            minimum = extract_date(minimum)
            maximum = extract_date(maximum)
            criteria = "(between {minimum} and {maximum})".format(**locals())
        response = input("{show_default}{criteria}> ".format(**locals()))

        if not minimum and maximum:
            raise Exception(
                "minimum and/or maximum are misspecified! Use a day-month-year format (e.g. 24-05-1999)"
            )

        if not response and default:
            response = default

        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # validation
        try:
            response = extract_date(response.strip())
            correct_type = response
        except ValueError:
            correct_type = False

        minimum_reached = correct_type and response >= minimum
        maximum_avoided = correct_type and response <= maximum

        if not correct_type or not minimum_reached or not maximum_avoided:
            print("Please provide an date between the minimum and maximum")
            show_help = True
            return TLI.TLI_text(**locals())

        return response

    def TLI_time(
        label,
        minimum=None,
        maximum=None,
        default=None,
        description="",
        help=None,
        show_help=False,
        *args,
        **kwargs
    ):
        def extract_time(string_input):
            try:
                return time.strptime(string_input, "%H:%M:%S")
            except ValueError:
                return False

        if description or show_help:
            print(label)
            print("\t" + "\t".join(description.split("\n")))
            if show_help:
                if not help:
                    print("HELP: unavailable...")
                else:
                    print("HELP: {help}".format(**locals()))

        show_default = default and "(default: {default})".format(**locals()) or ""
        if not minimum and not maximum:
            criteria = ""
        elif minimum and not maximum:
            minimum = extract_time(minimum)
            maximum = extract_time("23:59:60")  # should always be true
            criteria = "(at least {minimum})".format(**locals())
        elif not minimum and maximum:
            minimum = extract_time("00:00:00")  # should always be true
            maximum = extract_time(maximum)
            citeria = "(no longer than {maximum})".format(**locals())
        elif minimum and maximum:
            minimum = extract_time(minimum)
            maximum = extract_time(maximum)
            criteria = "(between {minimum} and {maximum})".format(**locals())
        response = input("{show_default}{criteria}> ".format(**locals()))

        if not minimum and maximum:
            raise Exception(
                "minimum and/or maximum are misspecified! Use a day-month-year format (e.g. 24-05-1999)"
            )

        if not response and default:
            response = default

        help_requested = [
            help_found for help_found in TLI.HELP_INDICATORS if help_found == response
        ]

        if help_requested:
            show_help = True
            return TLI.TLI_text(**locals())

        # validation
        try:
            response = extract_time(response.strip())
            correct_type = response
        except ValueError:
            correct_type = False

        minimum_reached = correct_type and response >= minimum
        maximum_avoided = correct_type and response <= maximum

        if not correct_type or not minimum_reached or not maximum_avoided:
            print(
                "Please provide a time in the format hour:minute:seconds (e.g. '22:45:55') between the minimum and maximum"
            )
            show_help = True
            return TLI.TLI_text(**locals())

        return response

    def prompt(prompt_specification, verify=False):
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

        print(
            """
=============== {prompt_specification[header]:^20.50} ===============

{prompt_specification[description]}

-----------------------------------------------------------------------------------
""".format(
                **locals()
            )
        )

        responses = OrderedDict()
        for prompt in prompt_specification["inputs"]:
            responses.update(
                {
                    prompt["label"]: getattr(
                        TLI, "TLI_{prompt[input_type]}".format(prompt=prompt)
                    )(**prompt)
                }
            )
            print()

        if verify == True:
            outputs = "\n".join(
                ["{k:30.30} : {v}".format(k=k, v=v) for k, v in responses.items()]
            )
            summary = """
================ you provided ===================

{outputs}

Is this correct? (Y/n)
=================================================

> """.format(
                outputs=outputs
            )
            correct = input(summary)
            if not correct.lower().strip() in ["y", "yes", "yeah", ""]:
                return TLI.prompt(prompt_specification, verify)
        return responses
