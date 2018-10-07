# How to annotate in INCA

This document explains how to use INCA to annotate (code) texts, for example for later machine learning. It is aimed at people without familarity with Python.

## How to use Jupyter

### Make a new notebook

Open your browser and go to the URL of your INCA server that you have been provided with.

Here, you can make a new notebook by clicking on new, Python 3.

A new notebook has been created.
Give the new notebook a title where it says "untitled". You will also see a line with 
`In [ ]: <blank space>`. 
You see in the drop-down menu that you can now fill in a `code` in the black space. 
This means that you will also be able to run (Crtl + Enter) the code entered in the black space. 
You can also change the line in a `markdown`. 
These are just notes for yourself in your notebook. 
You can for example explain to yourself what the different codes do.


### A search string
```
from inca import Inca
myinca = Inca()
from collections import OrderedDict
questions=OrderedDict([('example_var_1', 'Example question 1?'),
('example_var_2', 'Example question 2?'),
('example_var_3','Example question 3?'),
('example_var_4', 'Example question 4?'),
('example_var_5','Example question 5?'),
('example_var_6', 'Example question 6?')])
p = myinca.processing.annotate(docs_or_query='(title:test OR text:test) AND publication_date>2004-01-01',field='text',highlight_regexp = r'test',new_key='myproject_test', questions=questions, extra_filterquestion = True, window=40000, extra_fields=['title','doctype'], save=True)
```

This is an example code to import data from the INCA database.
You can put different variables in that you want to measure.
You can replace `example_var_1` with a self-chosen variable name and you can replace `Example_question_1` with the question that you want the program to ask you while annotating. You can put in as many variables and questions as you would like to.  

p will search for all news articles that you want to include in your research. You can adjust the code to your liking and your own research. 
The `docs_or_query='(title:test OR text:test)'` makes INCA search for news articles that contain the word 'test' in the title or the text.
You can also adjust the period in which you want to search, by adjusting `publication_date>2004-01-01`. 
Here we are searching for news articles published after 1 January 2004. 
The `highlight_regexp = r'test'` highlights the word 'test' (this does not work). 
The `extra_filterquestion = True` will give you an extra filter question at the beginning of annotating; it will ask you if the article is relevant/should be annotated. 
You can adjust the window if you only want to see a small paragraph for example. 
If you are still testing, delete `save=True` or replace it with `save=False`. 
If you are ready to save the data, you must include save=True. 

Probably you will get the following warning, but you will be able to proceed without errors. 
`WARNING:inca.analysis.var_tsa_analysis:$DISPLAY environment variable is not set, trying a different approach. You probably are running INCA on a text console, right?
INFO:INCA:Providing verbose output`

### Start annotating
```
while True:
    next(p)
```
This code will give you all articles for which you have searched (p), you can stop annotating by pressing CRTL+C or clicking on the black box ‘interrupt the kernel’. 

```
next(p)
```
With this code you will annotate all articles one by one, you have to run the code every time you are done annotating an article.  

Both codes will show you an article and it will ask you the questions that you put in before. 


### Count articles
```
generator_annotated = myinca.database.document_generator(query='_exists_:myproject_test')
annotated = [e['_source'] for e in generator_annotated]
```

This code will show you how many articles you have annotated (you can change this wording to your liking) until now. 





### Put your data in a Data frame
First of all, you need to create a function that allows you to put your measured variables in different columns.
```
import pandas as pd
def unpack(df, column, fillna=None):
    ret = None
    if fillna is None:
        ret = pd.concat([df, pd.DataFrame((d for idx, d in df[column].iteritems()))], axis=1)
        del ret[column]
    else:
        ret = pd.concat([df, pd.DataFrame((d for idx, d in df[column].iteritems())).fillna(fillna)], axis=1)
        del ret[column]
    return ret
```
The code above splits the data that you will generate into different columns in Excel. 
If you don’t do this, the data that you are generating will appear in one column in Excel. With this code, the different variables that you are measuring will appear in different columns when you download your data as an excel-file later on.



```
df = pd.DataFrame(annotated)
df = unpack(df,'myproject_test')
df
```
This code will provide a data frame (therefore, we called it `df`) with all information about the annotated articles so far. 

#### Descriptives
```
df[['example_var_1', 'example_var_2']].describe()
df['example_var_3'].value_counts()
df['example_var_4'].value_counts()
```

These are some example codes that will provide you with some descriptive statistics. Describe can be used for numeric variables and value_counts can be used for nominal variables.

#### Export data into Excel-file
```
df.to_excel('annotated.xlsx')
```

This code will export your data into an excel-file. When you run this code, you will find the excel-file on your Jupyter-homepage (https://inca.followthenews-uva.surf-hosted.nl:8000/user/lotte/tree?redirects=1). If you now select the excel-file (.xlsx) you can click on ‘Download’ and the excel-file of your data will be downloaded. 
