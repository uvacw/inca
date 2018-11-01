from setuptools import setup, find_packages

requirements = ['celery','colorama','spacy','tqdm','elasticsearch>=6',
                'feedparser', 'httplib2','imagehash', 'loremipsum',
                'lxml','requests','statsmodels','pandas',
                'pillow==5.0','gensim>3.4','oauth2client','matplotlib',
                'networkx',
                'scikit-learn','scipy','selenium','twython','nltk','tqdm']

setup(name='inca',
      version='0.1',
      description='INfrastructure for Content Analysis',
      url='http://github.com/uvacw/inca',
      author='INCA development team',
      author_email='inca-cw-fmg@uva.nl',
      license='GNU Affero GPL',
      packages=find_packages(),
      package_data={'':['*.cfg']},
      include_package_data=True,
      install_requires=requirements,
      zip_safe=False)
