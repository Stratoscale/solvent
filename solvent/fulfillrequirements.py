from solvent import config
from solvent import run
from solvent import label
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
        self._existingLabels = set(run.run([
            "osmosis", "listlabels",
            "--serverTCPPort=%d" % config.localOsmosisPort(),
            "--serverHostname=" + config.localOsmosisHostname()]).strip().split("\n"))
        matching = []
        for basename, hash in self._requirements:
            matching.append(self._matching(basename, hash))
        logging.info("Checking out '%(labels)s'", dict(labels=matching))
        run.run([
            "osmosis", "checkout", "..", "+".join(matching),
            "--MD5",
            "--serverTCPPort=%d" % config.localOsmosisPort(),
            "--serverHostname=" + config.localOsmosisHostname()])
# TODO: official server backend

    def _matching(self, basename, hash):
        official = label.label(basename=basename, product="build", hash=hash, state="official")
        if official in self._existingLabels:
            return official
        raise Exception("No official build for '%s' (%s)" % (basename, hash))
