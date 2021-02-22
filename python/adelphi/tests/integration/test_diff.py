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
        #container = self.client.containers.run("hello-world", detach=True)
        #self.assertTrue(container in self.client.containers.list())
        self.__testCassandraVersion("4.0-beta4")

    def __testCassandraVersion(self, version):
        imageStr = "cassandra:{}".format(version)
        logConfig = docker.types.LogConfig(type=docker.types.LogConfig.types.SYSLOG)
        container = self.client.containers.run(name="adelphi", remove=True, detach=True, ports={9042:9042}, image=imageStr)

        # We now have to wait until things are actually up
        containerReady = False
        while not containerReady:
            # Old version based on literal adaptation of prior shell script, probably not applicable at all
            #(exitcode,output) = container.exec_run(cmd="cqlsh -e 'select * from system.local'")
            #log.info("exitcode: {}".format(exitcode))
            #log.info("output: {}".format(output))
            #containerReady = (exitcode == 0)
            try:
                cluster = Cluster(["127.0.0.1"],port=9042)
                session = cluster.connect()
                rs = session.execute("select * from system.local")
                log.info(rs.one())
                cluster.shutdown()
                containerReady = True
            except:
                log.info("Exception connecting, will retry", exc_info=sys.exc_info()[0])

            if not containerReady:
                time.sleep(10)

        log.info("C* ready")

        container.stop()
