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

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from collections import namedtuple

from cassandra.cluster import Cluster
import docker

logging.basicConfig(filename="adelphi.log", level=logging.INFO)
log = logging.getLogger('adelphi')

TempDirs = namedtuple('TempDirs', 'basePath, outputPath, logPath')

class TestDiff(unittest.TestCase):

    def __stdoutPath(self, version=None, dirs=None):
        return os.path.join(dirs.outputPath, "{}-stdout.cql".format(version))


    def __makeTempDirs(self):
        basePath = tempfile.mkdtemp()
        outputPath = os.path.join(basePath, "output")
        os.mkdir(outputPath)
        logPath = os.path.join(basePath, "logs")
        os.mkdir(logPath)
        return TempDirs(basePath, outputPath, logPath)


    def __connectToCassandra(self):
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


    def __createSchema(self, session=None):
        log.info("Creating schema on Cassandra cluster")
        with open("integration-tests/base-schema.cql") as schema:
            for stmt in [s.strip() for s in schema.read().split(';')]:
                if len(stmt) == 0:
                    log.info("Skipping empty statement")
                    continue
                if stmt.startswith("//"):
                    log.info("Skipping commented statement {}".format(stmt))
                    continue
                realStmt = stmt + ';'
                log.debug("Executing statement {}".format(realStmt))
                try:
                    session.execute(realStmt)
                except:
                    log.info("Exception executing statement: {}".format(realStmt), exc_info=sys.exc_info()[0])


    def __runAdelphi(self, version=None, dirs=None):
        log.info("Running Adelphi")
        stdoutPath = self.__stdoutPath(version, dirs)
        stderrPath = os.path.join(dirs.logPath, "{}.log".format(version))
        subprocess.run("adelphi export-cql --no-metadata > {} 2>> {}".format(stdoutPath, stderrPath), shell=True)
        log.info("Adelphi completed")


    def __compare(self, version=None, dirs=None):
        stdoutPath = self.__stdoutPath(version, dirs)
        referencePath = "integration-tests/schemas/{}.cql".format(version)
        rv = subprocess.run("diff {} {}".format(stdoutPath, referencePath), shell=True)
        self.assertEqual(rv.returncode, 0)


    def __testCassandraVersion(self, version):
        log.info("Testing Cassandra version {}".format(version))

        container = self.client.containers.run(name="adelphi", remove=True, detach=True, ports={9042:9042}, image="cassandra:{}".format(version))
        dirs = self.__makeTempDirs()

        (cluster,session) = (None,None)
        try:
            (cluster,session) = self.__connectToCassandra()
            self.__createSchema(session)
            self.__runAdelphi(version, dirs)
            self.__compare(version, dirs)
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
            self.__testCassandraVersion(version)
