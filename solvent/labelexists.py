from solvent import config
from solvent import run


class LabelExists:
    def exists(self, label):
        if self._exists(config.LOCAL_OSMOSIS, label):
            return True
        if config.WITH_OFFICIAL_OBJECT_STORE:
            return self._exists(config.OFFICIAL_OSMOSIS, label)
        return False

    def _exists(self, objectStore, label):
        output = run.run(["osmosis", "listlabels", "^" + label + "$", "--objectStores=" + objectStore])
        lines = output.strip().split('\n')
        return len(lines) > 1 or len(lines[0]) > 0
