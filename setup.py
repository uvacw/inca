from setuptools import setup, find_packages

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
      zip_safe=False)
