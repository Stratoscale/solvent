from solvent import config
from solvent import run
from solvent import requirementlabel
import logging


class Bring:
    def __init__(self, repositoryBasename, product, hash, destination):
        self._repositoryBasename = repositoryBasename
        self._product = product
        self._hash = hash
        assert hash is not None
        self._destination = destination

    def go(self):
        requirementLabel = requirementlabel.RequirementLabel(
            basename=self._repositoryBasename, product=self._product, hash=self._hash)
        label = requirementLabel.matching()
        logging.info("Checking out '%(label)s'", dict(label=label))
        run.run([
            "osmosis", "checkout", self._destination, label,
            "--MD5", "--removeUnknownFiles",
            "--objectStores=" + config.objectStoresOsmosisParameter()])
