from solvent import config
from solvent import run
from solvent import requirementlabel
from solvent import manifest
import logging
import os


class Bring:
    def __init__(self, repositoryBasename, product, hash, destination):
        self._repositoryBasename = repositoryBasename
        self._product = product
        if hash is None:
            self._hash = self._hashFromRequirement(repositoryBasename)
        else:
            self._hash = hash
        self._destination = destination

    def go(self):
        requirementLabel = requirementlabel.RequirementLabel(
            basename=self._repositoryBasename, product=self._product, hash=self._hash)
        label = requirementLabel.matching()
        logging.info("Checking out '%(label)s'", dict(label=label))
        if not os.path.isdir(self._destination):
            os.makedirs(self._destination)
        run.run([
            "osmosis", "checkout", self._destination, label,
            "--MD5", "--removeUnknownFiles",
            "--objectStores=" + config.objectStoresOsmosisParameter()])

    def _hashFromRequirement(self, repositoryBasename):
        mani = manifest.Manifest.fromLocalDir()
        return mani.findRequirementByBasename(repositoryBasename)['hash']
