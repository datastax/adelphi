try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tests.integration import DockerSchemaTestMixin, AdelphiExportMixin

class TestDiff(unittest.TestCase, DockerSchemaTestMixin, AdelphiExportMixin):

    def setUp(self):
        super(TestDiff, self).setUp()


    def getExportCommand(self):
        return "export-cql --no-metadata"


    def getBaseSchemaPath(self):
        return "tests/integration/resources/diff-base-schema.cql"


    def getReferenceSchemaPath(self, version):
        return "tests/integration/resources/diff-schemas/{}.cql".format(version)
