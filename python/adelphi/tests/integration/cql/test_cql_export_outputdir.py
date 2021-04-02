import glob
import logging
import os
import shutil
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

from tests.integration import SchemaTestMixin
from tests.integration.cql import ExportCqlMixin

log = logging.getLogger('adelphi')

class TestCqlExportOutputDir(unittest.TestCase, SchemaTestMixin, ExportCqlMixin):

    def setUp(self):
        super(TestCqlExportOutputDir, self).setUp()


    def runAdelphi(self, version):
        stderrPath = self.stderrPath(version)
        outputDirPath = self.outputDirPath(version)
        os.mkdir(outputDirPath)
        subprocess.run("adelphi --output-dir={} export-cql --no-metadata 2>> {}".format(outputDirPath, stderrPath), shell=True)


    def evalAdelphiOutput(self, version):
        referencePath = "tests/integration/resources/cql-schemas/{}.cql".format(version)

        # Basic idea here is to find all schemas written to the output dir and aggregate them into a single schema
        # file.  We then compare this aggregated file to the reference schema.  Ordering is important here but
        # the current keyspace names hash to something that causes individual keyspaces to be discovered in the
        # correct order.
        outputDirPath = self.outputDirPath(version)
        allOutputFileName = "{}-all".format(version)
        allOutputPath = self.outputDirPath(allOutputFileName)

        outputSchemas = glob.glob("{}/*/schema".format(outputDirPath))
        self.assertGreater(len(outputSchemas), 0)
        with open(allOutputPath, "w+") as allOutputFile:
            for outputSchema in outputSchemas:
                with open(outputSchema) as outputSchemaFile:
                    shutil.copyfileobj(outputSchemaFile, allOutputFile)
                    allOutputFile.write("\n")
        self.compareToReferenceCql(referencePath, allOutputPath)
