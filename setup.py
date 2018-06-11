from setuptools import setup, find_packages

requirements = ['celery','colorama','spacy','tqdm','elasticsearch==5.4',
                'feedparser', 'httplib2','imagehash', 'loremipsum',
                'lxml','requests','statsmodels','pandas',
                'pillow==5.0','gensim','oauth2client','matplotlib',
                'scikit-learn','scipy','selenium','twython','nltk']

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
