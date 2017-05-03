# Contributing Code Guide
### *a guide for contributing code*

## Introduction

So you are going to join the team? *Great!*  Let's get some formalities
out of the way so you can get to work!

This guide assumes you are familiar with markdown, git and commandline. In addition, you should have a copy of INCA installed. If you are unsure about this things, please consult the [getting started guide](/gettingstarted.md)

First, Let's be clear about code styles. In the past, changes have been made on
a pretty ad-hoc basis. No Longer!


Follow these steps when adding code:
1. Make changes in a seperate branch
2. Start out small so you understand what you do
3. Write code in line with our preferred style
4. Document your code
5. Test your code **before** you push it to github
6. Have your code reviewed through a pull request

## 1. Sandboxing your changes

We want to avoid losing track of what's going on in the code-base. What was added when/how/why are not questions you want to have during a live demo! This is why we want to keep branches separated in the following way:

| Branch | Purpose |
|:--                    |:--|
| Master                | code running on the production server
| Development           | code checked but incomplete
| << issue-specific >>  | changes made to solve a specifc issue

This means that when you want to make changes to the code, you start
by making a new branch. You might, for example, want to pick up the
issue "scraper for financial times". You would do the following:

```bash
YOU@HOME> cd /path/to/INCA # go to inca directory
YOU@HOME> git pull # get the most recent version of the code
YOU@HOME> git checkout development #switch to the development branches
#make a new branch based on the development branch for your additions
YOU@HOME> git checkout -b financial_times
YOU@HOME> vim scrapers/financial_times.py # start coding!
...
YOU@HOME> git add scrapers/financial_times.py # add your added files
# Be clear in your commit messages!
YOU@HOME> git commit -m "I added a financial times scraper, tested locally"
YOU@HOME> git push # push your branch to the central repository
```

You can now ask for a 'pull request' in the online interface. Someone from our team will have a look at it!

## 2. Start out small

It's easy to get lost in code (bring food!). Often, it is best to start out small. Therefore we recommend you:
1. add new file** for a scraper rather than writing it in the same file as another.
2. Test the class directly by importing it:
```python
>>> from inca.scrapers.my_scraper import MyScraper
>>> for item in MyScraper().get():
>>>   print(item)
```


## 3. Write good code

Code is read more often than it is written! And even your own code will
be hard to understand when you go back to it after a month. This makes
clear code paramount. We aim to follow the [Google style guide](https://google.github.io/styleguide/pyguide.html#Python_Style_Rules). Some examples:

- indentation = 4 spaces (not tabs)
- lines no longer than *80* characters
- almost always use a docstring
- give sensible names to variables
  NOT
  ```python
  i = 2
  a = "lorum ipsum"
  ai = documents[2]
  ```
  but
  ```python
  iteration = 2
  document  = "lorum ipsum"
  document_i = documents[2]
  ```
- name things according to the following schema:
  - module_name
  - package_name
  - ClassName, method_name
  - ExceptionName
  - function_name
  - GLOBAL_CONSTANT_NAME
  - global_var_name
  - instance_var_name
  - function_parameter_name
  - local_var_name
  
  Suggestion: provide a short explanation of what these terms represent / when to use them? Or is this considered common knowledge? 
  In addition to this, would it be helpful to include a short dictionary that explains the most important terms/concepts of the guide?
  
- Split up complicated conditions

  Don't:
  ```python
  >>> If this > that and such < this or other != 0:
  >>>   print('hot mess')
  ```
  Do:
  ```python
  >>> this_bigger    = this > that
  >>> such_smaller   = such < this
  >>> other_not_zero = other != 0
  >>> if this_bigger and such_smaller or other_not_zero:
  >>>   print("trust me, this will help when conditions are complicated")
  ```

## 4. Write good documentation

Life is weird. Signal yields to noise. What was easy becomes hard. Fight entropy: write documentation!

Documentation is used to describe the purpose of a class, functionality of a function and assumptions in your code. There are three main ways in which we expect documentation to be provided:

1. Class docstring

  When you define a class, you should spell out what the main purpose is of that class, such as:
  ```python
  class MyScraper(Scraper):
    """ Scrapes mywebsite.nl """
  ```
2. Get method docstring (for scrapers)

  Should specify how a scraper goes about retrieving content:

  ```python
  class MyScraper(Scraper):
    """ Scrapers mywebsite.nl """

    def get(self):
      """ Retrieves posts backward in time from the index page """
  ```
3. Inline with your code

  Should clarify what comparisons or loops aim to accomplish

  ```python
  # check whether content exists
  assert document.keys("content",None), Exception("No content!")
  ```

With documentation you explain to a reader what your code is doing and where. We also use the docstrings for classes and methods to generate help.

## 5. Testing Testing Testing

*TODO*

## 6. making a "Pull" request

*TODO*
