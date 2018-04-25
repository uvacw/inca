from setuptools import setup, find_packages

setup(name='inca',
      version='0.1',
      description='INfrastructure for Content Analysis',
      url='http://github.com/uvacw/inca',
      author='Damian Trilling et al.',
      author_email='d.c.trilling@uva.nl',
      license='MIT',
      packages=find_packages(),
      package_data={'':['*.cfg']},
      include_package_data=True,
      zip_safe=False)
