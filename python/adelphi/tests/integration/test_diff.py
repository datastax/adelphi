try:
    import unittest2 as unittest
except ImportError:
    import unittest

from tests.integration import SchemaTestMixin
from tests.util.schema_util import get_schema

class TestDiff(unittest.TestCase, SchemaTestMixin):

    def setUp(self):
        super(TestDiff, self).setUp()


    def getExportCommand(self):
        return "export-cql --no-metadata"


    def getBaseSchemaPath(self):
        baseSchemaPath = self.basePath("diff-base-schema.cql")
        with open(baseSchemaPath, "w") as f:
            f.write("\n\n".join(ks.export_as_string() for ks in get_schema().keyspaces))
        return baseSchemaPath


    def getReferenceSchemaPath(self, version):
        return "tests/integration/resources/diff-schemas/{}.cql".format(version)
