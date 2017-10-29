from solvent import requirementlabel
from strato.racktest.infra import gitwrapper
import solvent.manifest
import logging


class CheckRequirements:
    def __init__(self):
        self._requirements = []
        import upseto.manifest  # TODO: deprecate
        upsetoManifest = upseto.manifest.Manifest.fromLocalDirOrNew()
        for requirement in upsetoManifest.requirements():
            self._requirements.append((
                gitwrapper.originURLBasename(requirement['originURL']),
                requirement['hash']))
        solventManifest = solvent.manifest.Manifest.fromLocalDirOrNew()
        for requirement in solventManifest.requirements():
            self._requirements.append((
                gitwrapper.originURLBasename(requirement['originURL']),
                requirement['hash']))

    def go(self):
        for basename, hash in self._requirements:
            requirementLabel = requirementlabel.RequirementLabel(
                basename=basename, product="build", hash=hash)
            requirementLabel.matching()
        logging.info("All requirements checked for existing labels")
