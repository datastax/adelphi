import logging
import os
import shutil
import tempfile

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from collections import namedtuple

from tests.util.cassandra_util import connectToLocalCassandra, createSchema

log = logging.getLogger('adelphi')

TempDirs = namedtuple('TempDirs', 'basePath, outputDirPath')


def setupSchema(schemaPath):
    (_,session) = connectToLocalCassandra()
    createSchema(session, schemaPath)


def dropKeyspace(keyspace):
    (_,session) = connectToLocalCassandra()
    session.execute("drop keyspace {}".format(keyspace))


class SchemaTestCase(unittest.TestCase):

    def basePath(self, name):
        return os.path.join(self.dirs.basePath, name)


    def outputDirPath(self, name):
        return os.path.join(self.dirs.outputDirPath, name)


    def stdoutPath(self, version=None):
        return self.basePath("{}-stdout.out".format(version))


    def stderrPath(self, version=None):
        return self.basePath("{}-stderr.log".format(version))


    def makeTempDirs(self):
        base = tempfile.mkdtemp()
        outputDir = os.path.join(base, "outputDir")
        os.mkdir(outputDir)
        self.dirs = TempDirs(base, outputDir)


    def setUp(self):
        super(SchemaTestCase, self).setUp()

        # This should be set in the tox config
        self.version = os.environ["CASSANDRA_VERSION"]
        log.info("Testing Cassandra version {}".format(self.version))
        self.makeTempDirs()


    def tearDown(self):
        super(SchemaTestCase, self).tearDown()

        if "KEEP_LOGS" in os.environ:
            log.info("KEEP_LOGS env var set, preserving logs/output at {}".format(self.dirs.basePath))
        else:
            shutil.rmtree(self.dirs.basePath)
