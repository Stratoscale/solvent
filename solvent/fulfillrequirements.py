from solvent import config
from solvent import run
from solvent import requirementlabel
from strato.racktest.infra import gitwrapper
import logging


class FulfillRequirements:
    def __init__(self):
        from upseto import manifest  # TODO: deprecate
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
        for label in matching:
            logging.info("Checking out '%(label)s'", dict(label=label))
            run.run([
                "osmosis", "checkout", "..", label,
                "--MD5", "--putIfMissing",
                "--objectStores=" + config.objectStoresOsmosisParameter()])
