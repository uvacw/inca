
# How to use a pretrained classifier

Using the pretrained method in INCA, it is possible to use a pre-trained classifier to categorize documents. The result will be stored in an additional key in the database. `path_to_model` will load the pretrained classifier and apply it to your data. Make sure that the classifier is stored as a pickle file.

This method uses the same parameters as other processing methods. Using `save=True` the results will be stored in the database. `force=True` will force overwriting the content even if it already exsists. `new_key=your_new_key_name` can be used to name the additional key containing the categorization.

For instance... (assuming you have already instantiated INCA):
```python
p = myinca.processing.pretrained('nu', 'text', path_to_model='/path/to/pretrainedmodel.pkl', new_key='topic', save=True) 
next(p)
```

A freely available pre-trained classifier trained on over 1 million new items by Susan Vermeer (2018) can be downloaded [here](https://figshare.com/articles/A_supervised_machine_learning_method_to_classify_Dutch-language_news_items/7314896/1). 
