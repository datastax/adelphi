import glob
import logging
import os
import shutil
import sys
import tempfile
import time

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from collections import namedtuple

from cassandra.cluster import Cluster

import docker

from tests.util.schemadiff import cqlDigestGenerator

# Default C* versions to include in all integration tests
CASSANDRA_VERSIONS = ["2.1.22", "2.2.19", "3.0.23", "3.11.9", "4.0-beta3"]

logging.basicConfig(filename="adelphi.log", level=logging.INFO)
log = logging.getLogger('adelphi')

TempDirs = namedtuple('TempDirs', 'basePath, outputDirPath')

def digestSet(schemaFile):
    rv = set()
    for (_, digest) in cqlDigestGenerator(schemaFile):
        rv.add(digest)
    return rv


def logCqlDigest(schemaFile, digestSet):
    for (cql, digest) in cqlDigestGenerator(schemaFile):
        if digest in digestSet:
            log.info("Digest: {}, CQL: {}".format(digest,cql))


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


    def connectToLocalCassandra(self):
        session = None
        while not session:
            try:
                cluster = Cluster(["127.0.0.1"],port=9042)
                session = cluster.connect()

                # Confirm that the session is actually functioning before calling things good
                rs = session.execute("select * from system.local")
                log.info("Connected to Cassandra cluster, first row of system.local: {}".format(rs.one()))
                log.info("Cassandra cluster ready")
                return (cluster,session)
            except:
                log.info("Couldn't quite connect yet, will retry")
                time.sleep(1)


    def createSchema(self, session=None):
        schemaPath = self.getBaseSchemaPath()
        log.info("Creating schema on Cassandra cluster from file {}".format(schemaPath))
        with open(schemaPath) as schema:
            buff = ""
            for line in schema:
                realLine = line.strip()
                if len(realLine) == 0:
                    log.debug("Skipping empty statement")
                    continue
                if realLine.startswith("//"):
                    log.debug("Skipping commented statement {}".format(stmt))
                    continue
                buff += (" " if len(buff) > 0 else "")
                buff += realLine
                if realLine.endswith(';'):
                    log.debug("Executing statement {}".format(buff))
                    try:
                        session.execute(buff)
                    except:
                        log.error("Exception executing statement: {}".format(buff), exc_info=sys.exc_info()[0])
                        self.fail("Exception executing statement: {}, check log for details".format(buff))
                    buff = ""


    def runAdelphi(self, version=None):
        log.info("Running Adelphi")
        exportCmd = self.getExportCommand()
        stdoutPath = self.stdoutPath(version)
        stderrPath = self.stderrPath(version)
        subprocess.run("adelphi {} > {} 2>> {}".format(exportCmd, stdoutPath, stderrPath), shell=True)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} {} 2>> {}".format(outputDirPath, exportCmd, stderrPath), shell=True)
        log.info("Adelphi completed")


    def _compareToReference(self, comparePath, version=None):
        referencePath = self.getReferenceSchemaPath(version)
        referenceSet = digestSet(referencePath)
        compareSet = digestSet(comparePath)

        refOnlySet = referenceSet - compareSet
        if len(refOnlySet) > 0:
            log.info("Statements in reference file {} but not in compare file {}:".format(referencePath, comparePath))
            logCqlDigest(referencePath, refOnlySet)
        compareOnlySet = compareSet - referenceSet
        if len(compareOnlySet) > 0:
            log.info("Statements in compare file {} but not in reference file {}:".format(comparePath, referencePath))
            logCqlDigest(comparePath, compareOnlySet)

        self.assertEqual(referenceSet, compareSet)


    def compareSchemas(self, version=None):

        self._compareToReference(self.stdoutPath(version), version)

        # Find the created schema underneath the output dir.  Note that this logic will have to be fixed
        # once https://github.com/datastax/adelphi/issues/106 is resolved
        outputDirPath = self.outputDirPath(version)
        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertGreater(len(outputSchemas), 0)
        log.info("Found schema file in output directory, path: {}".format(outputSchemas[0]))
        self._compareToReference(outputSchemas[0], version)


    def runTestWithSchema(self, version):
        self.runAdelphi(version)
        self.compareSchemas(version)


    def runTestForVersion(self, version=None):
        log.info("Testing Cassandra version {}".format(version))

        client = docker.from_env()
        container = client.containers.run(name="adelphi", remove=True, detach=True, ports={9042:9042}, image="cassandra:{}".format(version))

        self.makeTempDirs()

        (cluster,session) = (None,None)
        try:
            (cluster,session) = self.connectToLocalCassandra()
            self.createSchema(session)
            self.runTestWithSchema(version)
        except:
            log.error("Exception running test for version {}".format(version), exc_info=sys.exc_info()[0])
            self.fail("Exception running test for version {}, check log for details".format(version))
        finally:
            if cluster:
                cluster.shutdown()

            if "KEEP_CONTAINER" in os.environ:
                log.info("KEEP_CONTAINER env var set, preserving Cassandra container 'adelphi'")
            else:
                container.stop()

            self.cleanUpVersion(version)


    def testVersions(self):
        versions = CASSANDRA_VERSIONS
        if "CASSANDRA_VERSIONS" in os.environ:
            versions = [s.strip() for s in os.environ["CASSANDRA_VERSIONS"].split(',')]

        log.info("Testing the following Cassandra versions: {}".format(versions))

        for version in versions:
            self.runTestForVersion(version)


    def cleanUpVersion(self, version):
        if "KEEP_LOGS" in os.environ:
            log.info("KEEP_LOGS env var set, preserving logs/output at {}".format(self.dirs.basePath))
        else:
            shutil.rmtree(self.dirs.basePath)
