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
        labelsInLocal = self._existing(config.LOCAL_OSMOSIS)
        if self._official() in labelsInLocal:
            return self._official()
        if not config.OFFICIAL_BUILD:
            if self._clean() in labelsInLocal:
                return self._clean()
            if not config.CLEAN:
                if self._dirty() in labelsInLocal:
                    return self._dirty()
        if config.WITH_OFFICIAL_OBJECT_STORE:
            labelsInOfficial = self._existing(config.OFFICIAL_OSMOSIS)
            if self._official() in labelsInOfficial:
                return self._official()
            if not config.OFFICIAL_BUILD:
                if self._clean() in labelsInOfficial:
                    return self._clean()
                if not config.CLEAN:
                    if self._dirty() in labelsInOfficial:
                        return self._dirty()
        raise Exception("No official build for '%s' product '%s' (%s)" % (
            self._basename, self._product, self._hash))

    def _base(self, state):
        return label.label(basename=self._basename, product=self._product, hash=self._hash, state=state)

    def _regex(self):
        return self._base(state=".*")

    def _official(self):
        return self._base(state="official")

    def _clean(self):
        return self._base(state="clean")

    def _dirty(self):
        return self._base(state="dirty")

    def _existing(self, objectStore):
        output = run.run(["osmosis", "listlabels", self._regex(), "--objectStores=" + objectStore])
        return set(output.split("\n"))

    def _hashFromRequirement(self, repositoryBasename):
        mani = manifest.Manifest.fromLocalDir()
        return mani.findRequirementByBasename(repositoryBasename)['hash']
