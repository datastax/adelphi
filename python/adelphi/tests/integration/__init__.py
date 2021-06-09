import logging
import os
import shutil
import tempfile

from collections import namedtuple

from tests.util.cassandra_util import connectToLocalCassandra,createSchema

log = logging.getLogger('adelphi')

TempDirs = namedtuple('TempDirs', 'basePath, outputDirPath')

class SchemaTestMixin:

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


    def testAdelphi(self, version=None):
        log.info("Testing Cassandra version {}".format(version))

        self.makeTempDirs()
        try:
            (_,session) = connectToLocalCassandra()
            createSchema(session, self.getBaseSchemaPath)
            log.info("Running Adelphi")
            self.runAdelphi(version)
            log.info("Adelphi run completed, evaluating Adelphi output(s)")
            self.evalAdelphiOutput(version)
        finally:
            self.cleanUpTempDirs(version)


    def cleanUpTempDirs(self, version):
        if "KEEP_LOGS" in os.environ:
            log.info("KEEP_LOGS env var set, preserving logs/output at {}".format(self.dirs.basePath))
        else:
            shutil.rmtree(self.dirs.basePath)
