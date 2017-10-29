from solvent import config
from solvent import run
from solvent import label
from strato.racktest.infra import gitwrapper
import logging
import os


class Unsubmit:
    def __init__(self):
        git = gitwrapper.GitWrapper(os.getcwd())
        self._basename = git.originURLBasename()
        if config.OFFICIAL_BUILD:
            self._state = 'officialcandidate'
        elif config.CLEAN:
            self._state = 'cleancandidate'
        else:
            self._state = 'dirty'
        self._labelExpression = label.label(
            basename=self._basename, product=".*", hash=git.hash(), state=self._state)

    def go(self):
        if config.WITH_OFFICIAL_OBJECT_STORE:
            logging.info("unsubmitting in official object store")
            self._clearObjectStore(config.OFFICIAL_OSMOSIS)
        logging.info("unsubmitting locally")
        self._clearObjectStore(config.LOCAL_OSMOSIS)

    def _list(self, objectStore):
        output = run.run([
            "osmosis", "listlabels", '^' + self._labelExpression + '$', "--objectStores", objectStore])
        if output.strip() == "":
            return []
        return output.strip().split('\n')

    def _eraseLabel(self, objectStore, label):
        run.run(["osmosis", "eraselabel", label, "--objectStores", objectStore])

    def _clearObjectStore(self, objectStore):
        for label in self._list(objectStore):
            logging.info("removing label '%(label)s'", dict(label=label))
            self._eraseLabel(objectStore, label)
