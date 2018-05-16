# Breaking changes

We made a couple of fundamental changes to INCA to fix some design mistakes from the early days. This will make INCA future-proof and easier to use.

However, this also means that some code you used before won't work any more (or work in a different way).


## 1. INCA is now a module
Before, we had a directory `inca` with a file `inca.py`. With `import inca`, we imported that file. Now, we are importing a *directory* called `inca` instead; thus, within the directory `inca`, we have a second one with the same name. Thus, a workflow to test and change a scraper that looked like this:

```
cd ~/inca
ipython3
import inca
<<<do something in python>>>
exit()
emacs scrapers/whatever.py
git add scrapers/whatever.py
```
stays basically the same, except that the two last rows now read:
```
emacs inca/scrapers/whatever.py
git add inca/scrapers/whatever.py
```
Similarily, the location of some other directories changed (e.g., `doc` is now outside of the second-level `inca` folder.

Why did we do this? Because it makes INCA *pip installable*! (more about that later)


## 2. Instantiate the Inca() class instead of direct access to functions

Already before, there were basically to ways of using inca. The first one directly accessed all functionalities, for instance like this:
```python
import inca
s = inca.rssscrapers.news_scraper.nu()
s.run()
```
The second way was instantiating the Inca-class:
```python
from inca import Inca
myinca = Inca()
myinca.rssscrapers.nu()
```

The second way is *strongly* preferred, because the `myinca` instance contains exactly the functionality the enduser needs, nicely ordered and searchable via TAB-completion. Also, it hides all unnecessary (and/or dangerous) internal functions from the user. The new version of inca, in fact, *only* allows the second version. All new functionality must be built to be usable this way.

If, for a transition period, you *really* need to access functions directly in the old way, you need to do so via inserting an additional `__main`:
```python
import inca
s = inca.__main__.rssscrapers.news_scraper.nu()
```



## 3. Scrapers and Processors "run" automatically upon calling, arguments moved from __init__ to run

As the example in the previous section showed, there is no need any more to explicitly call the `run()` method: this is done automatically. Relatedly, the arguments that are passed when calling a scraper are not passed to `__init__()` any more, but to `run()` (and possibly passed through to `.get()` or whatever). This holds true for scrapers, processors, and so on. If your scraper needs some specific arguments (e.g., `maxpages`, `starturl`, ...), this cannot be realized via the `__init__()` method any more. Instead, add these arguments to the `.get()` method of your scraper.




## 4. `database=True` becomes `save=True`

Upon instantiating a scraper, it was possible to pass an argument `database` that indicated whether the resulting data should be stored or not. 

- The argument has been renamed to `save`, which is clearer and more consistent with the argument that processors take (there, it has always been `save`)
- `save` is now an argument of the `.get()` method of each scraper, to where it gets passed when supplied to `run` (which happens automatically when a scraper is used in the new way as described above).
Thus, if you want to scrape without saving, just do:
```python
data = myinca.rssscrapers.nu(save=False)
```
- We removed the functionality that returned data regardless of the setting of the save-functionality if Elasticsearch is not running on the system. If Elasticseach is not running, the user gets a warning upon importing inca, but subsequently needs to make sure that `save=False` is used. The reason is that it is preferable to have an error than to have the user wrongly assume that something is saved when in fact it is not.


