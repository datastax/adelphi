from setuptools import setup

PY3 = sys.version_info[0] == 3

dependencies = [
    'cassandra-driver >= 3.24.0',
    'click >= 7.1.2',
    'PyGithub >= 1.45'
    ]

if not PY3:
    dependencies.append('backports.tempfile')

setup(
   name='adelphi',
   version='0.1.0',
   author='Gianluca Righetto',
   author_email='gianluca.righetto@datastax.com',
   packages=['adelphi'],
   scripts=['bin/adelphi'],
   #url='http://pypi.python.org/pypi/PackageName/',
   url='https://github.com/datastax/adelphi',
   #license='LICENSE.txt',
   description='Tooling for Adelphi',
   #long_description=open('README.txt').read(),
   install_requires=dependencies,
)
