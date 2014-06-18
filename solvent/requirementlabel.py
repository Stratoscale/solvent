from solvent import config
from solvent import run
from solvent import label
from solvent import manifest


class RequirementLabel:
    def __init__(self, basename, product, hash):
        self._basename = basename
        self._product = product
        if hash is None:
            self._hash = self._hashFromRequirement(basename)
        else:
            self._hash = hash

    def matching(self):
        if self._official() in self._existing(config.LOCAL_OSMOSIS):
            return self._official()
        if config.WITH_OFFICIAL_OBJECT_STORE:
            if self._official() in self._existing(config.OFFICIAL_OSMOSIS):
                return self._official()
        raise Exception("No official build for '%s' product '%s' (%s)" % (
            self._basename, self._product, self._hash))

    def _regex(self):
        return label.label(basename=self._basename, product=self._product, hash=self._hash, state=".*")

    def _official(self):
        return label.label(basename=self._basename, product=self._product, hash=self._hash, state="official")

    def _existing(self, objectStore):
        output = run.run(["osmosis", "listlabels", self._regex(), "--objectStores=" + objectStore])
        return set(output.split("\n"))

    def _hashFromRequirement(self, repositoryBasename):
        mani = manifest.Manifest.fromLocalDir()
        return mani.findRequirementByBasename(repositoryBasename)['hash']
