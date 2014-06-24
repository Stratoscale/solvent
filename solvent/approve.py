from solvent import config
from solvent import run
from solvent import label
from upseto import gitwrapper
import logging
import os


class Approve:
    def __init__(self, product):
        self._product = product
        git = gitwrapper.GitWrapper(os.getcwd())
        self._basename = git.originURLBasename()
        if config.OFFICIAL_BUILD:
            self._fromState = "officialcandidate"
            self._toState = "official"
        elif config.CLEAN:
            self._fromState = "cleancandidate"
            self._toState = "clean"
        else:
            raise AssertionError("Must be a clean or official build to use approve")
        hash = git.hash()
        self._fromLabel = label.label(
            basename=self._basename, product=product, hash=hash, state=self._fromState)
        self._toLabel = label.label(
            basename=self._basename, product=product, hash=hash, state=self._toState)

    def go(self):
        run.run([
            "osmosis", "renamelabel", self._fromLabel, self._toLabel,
            "--objectStores=" + config.LOCAL_OSMOSIS])
        if config.WITH_OFFICIAL_OBJECT_STORE:
            run.run([
                "osmosis", "renamelabel", self._fromLabel, self._toLabel,
                "--objectStores=" + config.OFFICIAL_OSMOSIS])
        logging.info("Approved as '%(label)s'", dict(label=self._toLabel))
