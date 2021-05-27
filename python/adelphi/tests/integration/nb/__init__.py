import yaml

class ExportNbMixin:

    def compareToReferenceYaml(self, referencePath, comparePath):
        # Loader specification here to avoid a deprecation warning... see https://msg.pyyaml.org/load
        referenceYaml = yaml.load(open(referencePath), Loader=yaml.FullLoader)
        compareYaml = yaml.load(open(comparePath), Loader=yaml.FullLoader)
        self.assertEqual(referenceYaml, compareYaml)
