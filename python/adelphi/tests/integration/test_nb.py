try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tests.integration import SchemaTestMixin

class TestNb(unittest.TestCase, SchemaTestMixin):

    def setUp(self):
        super(TestNb, self).setUp()


    def getExportCommand(self):
        return "export-nb"


    def getBaseSchemaPath(self):
        return "tests/integration/resources/nb-base-schema.cql"


    def getReferenceSchemaPath(self, version):
        return "tests/integration/resources/nb-schemas/{}.yaml".format(version)