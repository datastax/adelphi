import glob
import logging
import os
import shutil
import sys
import tempfile

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from collections import namedtuple

import docker

from tests.integration import BaseIntegrationTest

logging.basicConfig(filename="adelphi.log", level=logging.INFO)
log = logging.getLogger('adelphi')

DIFF_SCHEMA_PATH = "tests/integration/resources/base-schema.cql"

TempDirs = namedtuple('TempDirs', 'basePath, outputPath, logPath')

class TestDiff(unittest.TestCase, BaseIntegrationTest):

    def stdoutPath(self, version=None, dirs=None):
        return os.path.join(dirs.outputPath, "{}-stdout.cql".format(version))


    def outputDirPath(self, version=None, dirs=None):
        return os.path.join(dirs.outputPath, version)


    def makeTempDirs(self):
        basePath = tempfile.mkdtemp()
        outputPath = os.path.join(basePath, "output")
        os.mkdir(outputPath)
        logPath = os.path.join(basePath, "logs")
        os.mkdir(logPath)
        return TempDirs(basePath, outputPath, logPath)


    def runAdelphi(self, version=None, dirs=None):
        log.info("Running Adelphi")
        stdoutPath = self.stdoutPath(version, dirs)
        outputDirPath = self.outputDirPath(version, dirs)
        os.mkdir(outputDirPath)
        stderrPath = os.path.join(dirs.logPath, "{}-stderr.log".format(version))
        subprocess.run("adelphi export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)
        subprocess.run("adelphi --output-dir={} export-cql 2>> {}".format(outputDirPath, stderrPath), shell=True)
        log.info("Adelphi completed")


    def compareSchemas(self, version=None, dirs=None):
        referencePath = "tests/integration/resources/schemas/{}.cql".format(version)

        stdoutPath = self.stdoutPath(version, dirs)
        rv1 = subprocess.run("diff -Z {} {}".format(stdoutPath, referencePath), shell=True)
        self.assertEqual(rv1.returncode, 0)

        # Find the created schema underneath the output dir.  Note that this logic will have to be fixed
        # once https://github.com/datastax/adelphi/issues/106 is resolved
        outputDirPath = self.outputDirPath(version, dirs)
        schemas = glob.glob("{}/*/schema".format(outputDirPath))
        log.info("Found schema file in output directory, path: {}".format(schemas[0]))
        rv2 = subprocess.run("diff -Z {} {}".format(schemas[0], referencePath), shell=True)
        self.assertEqual(rv2.returncode, 0)

    def runTestForVersion(self, version):
        log.info("Testing Cassandra version {}".format(version))

        container = self.client.containers.run(name="adelphi", remove=True, detach=True, ports={9042:9042}, image="cassandra:{}".format(version))
        dirs = self.makeTempDirs()

        (cluster,session) = (None,None)
        try:
            (cluster,session) = self.connectToLocalCassandra()
            self.createSchema(session, DIFF_SCHEMA_PATH)
            self.runAdelphi(version, dirs)
            self.compareSchemas(version, dirs)
        finally:
            if cluster:
                cluster.shutdown()

            if "KEEP_CONTAINER" in os.environ:
                log.info("KEEP_CONTAINER env var set, preserving Cassandra container 'adelphi'")
            else:
                container.stop()

            if "KEEP_LOGS" in os.environ:
                log.info("KEEP_LOGS env var set, preserving logs/output at {}".format(dirs.basePath))
            else:
                shutil.rmtree(dirs.basePath)


    def setUp(self):
        self.client = docker.from_env()


    def testDiff(self):
        versions = ["2.1.22", "2.2.19", "3.0.23", "3.11.9", "4.0-beta3"]
        if "CASSANDRA_VERSIONS" in os.environ:
            versions = os.environ["CASSANDRA_VERSIONS"].split(',')
            log.info("CASSANDRA_VERSIONS set, using version list {}".format(versions))

        for version in versions:
            self.runTestForVersion(version)
