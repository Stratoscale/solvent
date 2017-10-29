from solvent import config
from solvent import label
from solvent import run
from strato.racktest.infra import gitwrapper


class ThisProjectLabel:
    def __init__(self, product):
        gitWrapper = gitwrapper.GitWrapper('.')
        hash = gitWrapper.hash()
        basename = gitWrapper.originURLBasename()

        if config.OFFICIAL_BUILD:
            state = 'officialcandidate'
        elif config.CLEAN:
            state = 'cleancandidate'
        else:
            state = 'dirty'

        self._label = label.label(basename, product, hash, state)
        self._makeSureExists()

    def _makeSureExists(self):
        if self._exists(config.LOCAL_OSMOSIS):
            return
        if config.WITH_OFFICIAL_OBJECT_STORE:
            if self._exists(config.OFFICIAL_OSMOSIS):
                return
        raise Exception("Label '%s' does not exists in any of the object stores" % self._label)

    def _exists(self, objectStore):
        output = run.run(["osmosis", "listlabels", "^%s$" % self._label, "--objectStores=" + objectStore])
        return self._label in output

    def label(self):
        return self._label
