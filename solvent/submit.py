from solvent import config
from solvent import run
from solvent import label
from upseto import gitwrapper
import logging
import os


class Submit:
    def __init__(self, product, directory):
        self._product = product
        self._directory = directory
        git = gitwrapper.GitWrapper(os.getcwd())
        self._basename = git.originURLBasename()
        if config.OFFICIAL_BUILD:
            self._state = 'officialcandidate'
        elif config.CLEAN:
            self._state = 'cleancandidate'
        else:
            self._state = 'dirty'
        self._label = label.label(
            basename=self._basename, product=self._product, hash=git.hash(), state=self._state)
        if config.OFFICIAL_BUILD or config.CLEAN:
            run.run([
                "python2", "-m", "upseto.main", "checkRequirements",
                "--allowNoManifest", "--unsullied", "--gitClean"])

    def go(self):
        self._handleCollision(config.LOCAL_OSMOSIS)
        if config.WITH_OFFICIAL_OBJECT_STORE:
            self._handleCollision(config.OFFICIAL_OSMOSIS)
        logging.info("Submitting locally as '%(label)s'", dict(label=self._label))
        self._checkin(config.LOCAL_OSMOSIS)
        if config.WITH_OFFICIAL_OBJECT_STORE:
            logging.info("Submitting to official store as '%(label)s'", dict(label=self._label))
            self._checkin(config.OFFICIAL_OSMOSIS)
        logging.info("Submitted as '%(label)s'", dict(label=self._label))

    def _hasLabel(self, objectStore):
        output = run.run([
            "osmosis", "listlabels", '^' + self._label + '$', "--objectStores", objectStore])
        return len(output.split('\n')) > 1

    def _checkin(self, objectStore):
        run.run([
            "osmosis", "checkin", self._directory, self._label,
            "--MD5",
            "--objectStores", objectStore])

    def _eraseLabel(self, objectStore):
        run.run([
            "osmosis", "eraselabel", self._label,
            "--objectStores", objectStore])

    def _handleCollision(self, objectStore):
        if self._hasLabel(objectStore):
            if config.FORCE:
                self._eraseLabel(objectStore)
            else:
                raise Exception("Object store '%s' already has a label '%s'" % (
                    objectStore, self._label))
