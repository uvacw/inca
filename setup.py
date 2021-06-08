from setuptools import setup, find_packages

requirements = [
    "wheel",
    "celery>3.1,<4.0",
    "cytoolz",
    "colorama",
    "tqdm",
    "elasticsearch>=6",
    "feedparser",
    "httplib2",
    "imagehash",
    "loremipsum",
    "lxml",
    "requests<3.0.0,>=2.13.0",
    "statsmodels",
    "pandas",
    "pillow==8.2.0",
    "gensim>3.4",
    "oauth2client",
    "matplotlib",
    "networkx",
    "spacy",
    "scikit-learn",
    "scipy",
    "selenium",
    "twython",
    "nltk",
    "tqdm",
    "pattern",
    "praw",
    "nl_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/nl_core_news_sm-2.1.0/nl_core_news_sm-2.1.0.tar.gz",
]

setup(
    name="inca",
    version="0.1",
    description="INfrastructure for Content Analysis",
    url="http://github.com/uvacw/inca",
    author="INCA development team",
    author_email="inca-cw-fmg@uva.nl",
    license="GNU Affero GPL",
    packages=find_packages(),
    package_data={"": ["*.cfg", "schema.json"]},
    include_package_data=True,
    install_requires=requirements,
    dependency_links=[],
    zip_safe=False,
)

