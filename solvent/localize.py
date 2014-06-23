from solvent import config
from solvent import run
import logging


class Localize:
    def __init__(self, label):
        self._label = label

    def go(self):
        existing = run.run(["osmosis", "listlabels", self._label, "--objectStores", config.LOCAL_OSMOSIS])
        if len(existing.strip()) > 0:
            logging.info("label '%(label)s' already exists in local osmosis object store", dict(
                label=self._label))
            return
        if not config.WITH_OFFICIAL_OBJECT_STORE:
            raise Exception("No official object store in configuration to fetch out of")
        logging.info("fetching label '%(label)s' from official object store", dict(
            label=self._label))
        run.run([
            "osmosis", "transfer", self._label,
            "--objectStores", config.OFFICIAL_OSMOSIS,
            "--transferDestination", config.LOCAL_OSMOSIS])
