import logging
import os
import shutil
import tempfile

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from collections import namedtuple

from adelphi.store import with_local_cluster, create_schema

log = logging.getLogger('adelphi')

TempDirs = namedtuple('TempDirs', 'basePath, outputDirPath')


def __keyspacesForCluster(cluster):
    return set(cluster.metadata.keyspaces.keys())


def setupSchema(schemaPath):
    def schemaFn(cluster):
        return create_schema(cluster.connect(), schemaPath)
    return with_local_cluster(schemaFn)


def getAllKeyspaces():
    return with_local_cluster(__keyspacesForCluster)


def dropNewKeyspaces(origKeyspaces):
    def dropFn(cluster):
        currentKeyspaces = __keyspacesForCluster(cluster)
        droppingKeyspaces = currentKeyspaces - origKeyspaces
        log.info("Dropping the following keyspaes created by this test: {}".format(",".join(droppingKeyspaces)))
        session = cluster.connect()
        for keyspace in droppingKeyspaces:
            session.execute("drop keyspace {}".format(keyspace))
    return with_local_cluster(dropFn)


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
        # Invoking for completeness; for unittest base setUp/tearDown impls are no-ops
        super(SchemaTestCase, self).setUp()

        # This should be set in the tox config
        self.version = os.environ["CASSANDRA_VERSION"]
        log.info("Testing Cassandra version {}".format(self.version))

        self.makeTempDirs()


    def tearDown(self):
        super(SchemaTestCase, self).tearDown()

        # TODO: Note that there's no easy way to access this from test-adelphi unless we modify the
        # ini generation code... and I'm not completely sure that's worth it.  Might want to think
        # about just deleting this outright... or making it a CLI option that can be easily accessed.
        if "KEEP_LOGS" in os.environ:
            log.info("KEEP_LOGS env var set, preserving logs/output at {}".format(self.dirs.basePath))
        else:
            shutil.rmtree(self.dirs.basePath)
