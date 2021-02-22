import logging
import time
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from cassandra.cluster import Cluster
import docker

logging.basicConfig(filename="adelphi.log", level=logging.INFO)
log = logging.getLogger('adelphi')

class TestDiff(unittest.TestCase):

    def setUp(self):
        self.client = docker.from_env()


    def testSimple(self):
        self.__testCassandraVersion("4.0-beta4")


    def __connectToCassandra(self):
        self.session = None
        while not self.session:
            # Old version based on literal adaptation of prior shell script, probably not applicable at all now
            #(exitcode,output) = container.exec_run(cmd="cqlsh -e 'select * from system.local'")
            #containerReady = (exitcode == 0)
            try:
                self.cluster = Cluster(["127.0.0.1"],port=9042)
                self.session = self.cluster.connect()

                # Confirm that the session is actually functioning before calling things good
                rs = self.session.execute("select * from system.local")
                log.info("Connected to Cassandra cluster, first row of system.local: {}".format(rs.one()))
            except:
                log.info("Exception connecting, will retry", exc_info=sys.exc_info()[0])
                time.sleep(10)


    def __createSchema(self):
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
                log.info("Executing statement {}".format(realStmt))
                self.session.execute(realStmt)


    def __testCassandraVersion(self, version):
        container = self.client.containers.run(name="adelphi", remove=True, detach=True, ports={9042:9042}, image="cassandra:{}".format(version))

        self.__connectToCassandra()

        log.info("Cassandra cluster ready")

        self.__createSchema()

        self.cluster.shutdown()
        #container.stop()
