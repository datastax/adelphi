try:
    import unittest2 as unittest
except ImportError:
    import unittest

import docker
    
class TestDiff(unittest.TestCase):

    def setUp(self):
        self.client = docker.from_env()

    def testSimple(self):
        container = self.client.containers.run("hello-world", detach=True)
        self.assertTrue(container in self.client.containers.list())
