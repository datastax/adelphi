from setuptools import setup

setup(
   name='adelphi',
   version='0.1.0',
   author='Gianluca Righetto',
   author_email='gianluca.righetto@datastax.com',
   packages=['adelphi'],
   scripts=['bin/anonymizer'],
   #url='http://pypi.python.org/pypi/PackageName/',
   url='https://github.com/datastax/adelphi',
   #license='LICENSE.txt',
   description='Schema anonymizer for Adelphi',
   #long_description=open('README.txt').read(),
   install_requires=['cassandra-driver'],
)
