# Run test suite for some set of Cassandra versions.
#
# We implement this as a front-end script because the tox/pytest/unittest chain
# isn't great about iterating over a suite of test fixtures and re-running the
# collected tests for each of them.  Rather than fight with the frameworks we
# manage the fixture iteration manually in this script.  This also has the
# nice side effect of moving a lot of C* checking/session code out of the test
# suite, which in turn should allow us to write simpler tests.
import configparser
import logging
import os

import tox

import docker
from tenacity import retry, stop_after_attempt, wait_fixed

# Default C* versions to include in all integration tests
CASSANDRA_VERSIONS = ["2.1.22", "2.2.19", "3.0.23", "3.11.9", "4.0-beta4"]

TOX_DEPENDENCIES = """pytest
    subprocess32 ~= 3.5"""
TOX_CONFIG = "tox.ini"

logging.basicConfig(filename="adelphi-tests.log", level=logging.INFO)
log = logging.getLogger('adelphi')


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def getContainer(client, version):
    return client.containers.run(name="adelphi", remove=True, detach=True, ports={9042: 9042}, image="cassandra:{}".format(version))


def getCassandraVersions():
    if "CASSANDRA_VERSIONS" in os.environ:
        return [s.strip() for s in os.environ["CASSANDRA_VERSIONS"].split(',')]
    else:
        return CASSANDRA_VERSIONS 


def writeToxIni(version):
    config = configparser.ConfigParser()
    config["tox"] = { "envlist": "py2, py3" }
    envs = {"CASSANDRA_VERSION": version}
    config["testenv"] = {"deps": TOX_DEPENDENCIES, \
        "commands": "pytest {posargs}", \
        "setenv": "CASSANDRA_VERSION = {}".format(version)}
    with open(TOX_CONFIG, 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    client = docker.from_env()
    for version in getCassandraVersions():

        log.info("Running test suite for Cassandra version {}".format(version))
        container = getContainer(client, version)

        try:
            os.remove(TOX_CONFIG)
            writeToxIni(version)
            tox.cmdline()
        except Exception as exc:
            log.error("Exception running tests for Cassandra version {}".format(version), exc_info=exc)
        finally:
            if "KEEP_CONTAINER" in os.environ:
                log.info("KEEP_CONTAINER env var set, preserving Cassandra container 'adelphi'")
            else:
                container.stop()
