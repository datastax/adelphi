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

from tests.integration import BaseIntegrationTest, CASSANDRA_VERSIONS

logging.basicConfig(filename="adelphi.log", level=logging.INFO)
log = logging.getLogger('adelphi')

TempDirs = namedtuple('TempDirs', 'basePath, outputPath, logPath')

class TestDiff(BaseIntegrationTest, unittest.TestCase):

    def stdoutPath(self, version=None):
        return os.path.join(self.dirs.outputPath, "{}-stdout.cql".format(version))


    def outputDirPath(self, version=None):
        return os.path.join(self.dirs.outputPath, version)


    def makeTempDirs(self):
        basePath = tempfile.mkdtemp()
        outputPath = os.path.join(basePath, "output")
        os.mkdir(outputPath)
        logPath = os.path.join(basePath, "logs")
        os.mkdir(logPath)
        return TempDirs(basePath, outputPath, logPath)


    def runAdelphi(self, version=None):
        log.info("Running Adelphi")
        stdoutPath = self.stdoutPath(version)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        stderrPath = os.path.join(self.dirs.logPath, "{}-stderr.log".format(version))
        subprocess.run("adelphi export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)
        subprocess.run("adelphi --output-dir={} export-cql 2>> {}".format(outputDirPath, stderrPath), shell=True)
        log.info("Adelphi completed")


    def compareSchemas(self, version=None):
        referencePath = "tests/integration/resources/diff-schemas/{}.cql".format(version)

        stdoutPath = self.stdoutPath(version)
        rv1 = subprocess.run("diff -Z {} {}".format(stdoutPath, referencePath), shell=True)
        self.assertEqual(rv1.returncode, 0)

        # Find the created schema underneath the output dir.  Note that this logic will have to be fixed
        # once https://github.com/datastax/adelphi/issues/106 is resolved
        outputDirPath = self.outputDirPath(version)
        schemas = glob.glob("{}/*/schema".format(outputDirPath))
        log.info("Found schema file in output directory, path: {}".format(schemas[0]))
        rv2 = subprocess.run("diff -Z {} {}".format(schemas[0], referencePath), shell=True)
        self.assertEqual(rv2.returncode, 0)


    def setUp(self):
        super(TestDiff, self).setUp()
        self.dirs = self.makeTempDirs()


    def runTestWithSchema(self, version):
        self.runAdelphi(version)
        self.compareSchemas(version)


    def cleanUpVersion(self, version):
        if "KEEP_LOGS" in os.environ:
            log.info("KEEP_LOGS env var set, preserving logs/output at {}".format(self.dirs.basePath))
        else:
            shutil.rmtree(self.dirs.basePath)


    def getSchemaPath(self):
        return "tests/integration/resources/diff-base-schema.cql"
