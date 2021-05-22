import sys

from setuptools import setup

PY3 = sys.version_info[0] == 3

dependencies = [
    'cassandra-driver ~= 3.24',
    'click ~= 7.1',
    'PyGithub ~= 1.45',
    'PyYAML ~= 5.4'
    ]

if not PY3:
    dependencies.append('backports.tempfile ~= 1.0')

long_description = ""
with open("README.md") as f:
    long_description = f.read()

setup(
    name='adelphi',
    url='https://github.com/datastax/adelphi',
    description='Tooling for Adelphi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='0.2.1',
    project_urls={
        'Documentation': 'https://github.com/datastax/adelphi/blob/master/python/adelphi/README.md',
        'Source': 'https://github.com/datastax/adelphi',
        'Issues': 'https://github.com/datastax/adelphi/issues',
    },
    author='DataStax',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
   ],
   packages=['adelphi'],
   scripts=['bin/adelphi'],
   install_requires=dependencies,
)
