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


    # TODO: Note that we currently have to disable support for SASI indexes when creating
    # a schema since the base config for the Cassandra Docker images doesn't enable it.
    # https://github.com/datastax/adelphi/issues/105 aims to fix this problem but until
    # that's in place we simply exclude SASI indexes from testing.
    def getBaseSchemaPath(self):
        baseSchemaPath = self.basePath("diff-base-schema.cql")
        with open(baseSchemaPath, "w") as f:
            f.write("\n\n".join(ks.export_as_string() for ks in get_schema(sasi=False).keyspaces))
        return baseSchemaPath


    def getReferenceSchemaPath(self, version):
        return "tests/integration/resources/diff-schemas/{}.cql".format(version)
