from solvent import config
from solvent import run
from upseto import gitwrapper
import logging
import os


class SubmitBuild:
    def __init__(self):
        git = gitwrapper.GitWrapper(os.getcwd())
        self._basename = git.originURLBasename()
        self._state = "officialcandidate" if config.OFFICIAL_BUILD else "cleancandidate"
        self._product = "build"
        self._label = "solvent__%(basename)s__build__%(hash)s__%(state)s" % dict(
            basename=self._basename, hash=git.hash(), state=self._state)
        run.run([
            "python", "-m", "upseto.main", "checkRequirements",
            "--allowNoManifest", "--unsullied", "--gitClean"])

    def go(self):
        run.run([
            "osmosis", "checkin", "..", self._label,
            "--MD5",
            "--serverTCPPort=%d" % config.localOsmosisPort(),
            "--serverHostname=" + config.localOsmosisHostname()])
        run.run([
            "osmosis", "checkin", "..", self._label,
            "--MD5",
            "--serverTCPPort=%d" % config.officialOsmosisPort(),
            "--serverHostname=" + config.officialOsmosisHostname()])
        logging.info("Submitted as '%(label)s'", dict(label=self._label))
