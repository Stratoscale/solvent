from solvent import config
from solvent import run
from solvent import requirementlabel
from upseto import gitwrapper
from upseto import manifest
import logging


class FulfillRequirements:
    def __init__(self):
        mani = manifest.Manifest.fromLocalDirOrNew()
        self._requirements = []
        for requirement in mani.requirements():
            self._requirements.append((
                gitwrapper.originURLBasename(requirement['originURL']),
                requirement['hash']))

    def go(self):
        if len(self._requirements) == 0:
            logging.info("No upseto requirements to fulfill")
            return
        matching = []
        for basename, hash in self._requirements:
            requirementLabel = requirementlabel.RequirementLabel(
                basename=basename, product="build", hash=hash)
            matching.append(requirementLabel.matching())
        logging.info("Checking out '%(labels)s'", dict(labels=matching))
        run.run([
            "osmosis", "checkout", "..", "+".join(matching),
            "--MD5",
            "--objectStores=" + config.objectStoresOsmosisParameter()])
