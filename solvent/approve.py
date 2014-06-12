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
        self._fromState = "officialcandidate" if config.OFFICIAL_BUILD else "cleancandidate"
        self._toState = "official" if config.OFFICIAL_BUILD else "clean"
        self._fromLabel = label.label(
            basename=self._basename, product=product, hash=git.hash(), state=self._fromState)
        self._toLabel = label.label(
            basename=self._basename, product=product, hash=git.hash(), state=self._toState)

    def go(self):
        run.run([
            "osmosis", "renamelabel", self._fromLabel, self._toLabel,
            "--serverTCPPort=%d" % config.localOsmosisPort(),
            "--serverHostname=" + config.localOsmosisHostname()])
        run.run([
            "osmosis", "renamelabel", self._fromLabel, self._toLabel,
            "--serverTCPPort=%d" % config.officialOsmosisPort(),
            "--serverHostname=" + config.officialOsmosisHostname()])
        logging.info("Approved as '%(label)s'", dict(label=self._toLabel))
