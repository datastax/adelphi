# Testing Adelphi

## Sub-directories

* unit - unit tests implemented using the [unittest](https://docs.python.org/3/library/unittest.html) module
* integration - integration tests which use Docker to manage Cassandra instances
* util - common utils for either unit or integration tests (or both)

## Integration tests

The integration tests leverage the [docker](https://pypi.org/project/docker/) module for starting and stopping local Cassandra instances of a specific version.  The framework supports some minimal customizations using env vars; these include:

* CASSANDRA_VERSIONS - a comma-delimited list of Cassandra versions to test
* KEEP_CONTAINER - do not remove the container after the test run has finished
* KEEP_LOGS - do not remove the local test working directory (containing logs and other information) after the test run has finished

The test working directory is created via tempfile.mkdtemp() and is reported via logging for each run.

If CASSANDRA_VERSIONS is not defined a default list is used; consult the source for more detail.  Also note that each test tries to re-use the name "adelphi" for Docker containers so using KEEP_CONTAINER while running multiple tests (or one test over multiple Cassandra versions) will cause Docker problems due to conflicts with existing containers.

## tox

All tests are expected to pass on the latest Python 2.7.x and Python 3.x.  The easiest way to run the tests is to use the [tox](https://tox.readthedocs.io/en/latest/) tool which automates running the entire suite of tests on both versions.  You can run the entire test suite for a single environment by using the -e flag:

    tox -e py2

You can find a working tox.ini file [one level up](https://github.com/datastax/adelphi/tree/master/python/adelphi) as well as a sample tox.ini file that might be used for development.  These files both use [pytest](https://docs.pytest.org/en/stable/) for test discovery; anything under either the unit or integration tests should be picked up automatically.  Also note that both files include the use pytest's posargs value so any necessary args to pytest can be passed directly.  This is very useful when you wish to run a single test via tox:

    tox -- tests/integration/nb/test_nb_export_stdout.py

tox works by creating distinct virtualenvs (venvs) for each environment specified in the "envlist" val specified in tox.ini.  Note that these venvs are re-used across tox runs so if you find yourself changing or adding dependencies you will need to delete your existing venvs in order to force a rebuild.
