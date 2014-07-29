from solvent import config
from solvent import run
from solvent import requirementlabel
import logging
import os


class Bring:
    def __init__(self, repositoryBasename, product, hash, destination):
        self._repositoryBasename = repositoryBasename
        self._product = product
        self._hash = hash
        self._destination = destination

    def go(self):
        requirementLabel = requirementlabel.RequirementLabel(
            basename=self._repositoryBasename, product=self._product, hash=self._hash)
        label = requirementLabel.matching()
        self.label(label=label, destination=self._destination)

    @classmethod
    def label(cls, label, destination):
        logging.info("Checking out '%(label)s'", dict(label=label))
        if not os.path.isdir(destination):
            os.makedirs(destination)
        myUIDandGID = ["--myUIDandGIDcheckout"] if os.getuid() != 0 else []
        run.run([
            "osmosis", "checkout", destination, label,
            "--MD5", "--removeUnknownFiles", "--putIfMissing",
            "--objectStores=" + config.objectStoresOsmosisParameter()] + myUIDandGID)
