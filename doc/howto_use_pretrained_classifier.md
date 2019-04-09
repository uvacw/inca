
# How to use a pretrained classifier

With the pretrained method in INCA, it is possible to use a pre-trained classifier to categorize documents. The result will be stored in an additional key in the database. `path_to_model` will load the pretrained classifier and apply it to your data. Make sure that the classifier is stored as a pickle file.

This method uses the same parameters as other processing methods. Using `save=True`, the results will be stored in the database. `force=True` will force overwriting the content even if the key already exists. `new_key='your_new_key_name'` can be used to name the additional key containing the categorization. As described in the [processing documentation](https://github.com/uvacw/inca/blob/development/doc/howto_process.md), it is also possible to use an Elasticsearch Query instead of a doctype. 

For instance... (assuming you have already instantiated INCA):
```python
p = myinca.processing.pretrained('nu', 'text', path_to_model='/path/to/pretrainedmodel.pkl', new_key='topic', save=True) 
next(p)
```

A freely available Passive Aggressive classifier trained on over 1 million news items by Susan Vermeer (2018) can be downloaded [here](https://figshare.com/articles/A_supervised_machine_learning_method_to_classify_Dutch-language_news_items/7314896/1). Keep in mind that for accurate results, you need to preprocess your text in the same way as was done for the classifier. In this case, either use the (1) the full text, (2) stopword removal, or (3) only use the lead of the text. 
