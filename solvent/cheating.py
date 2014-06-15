import argparse
from solvent import label
from solvent import config
from solvent import run
from upseto import gitwrapper
import logging
import os


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
changeStateCmd = subparsers.add_parser("changestate")
changeStateCmd.add_argument("--product", required=True)
changeStateCmd.add_argument("--fromState", required=True)
changeStateCmd.add_argument("--toState", required=True)
parser.add_argument("--configurationFile", default="/etc/solvent.conf")
args = parser.parse_args()

config.load(args.configurationFile)
if args.cmd == "changestate":
    git = gitwrapper.GitWrapper(os.getcwd())
    fromLabel = label.label(
        basename=git.originURLBasename(), product=args.product, hash=git.hash(), state=args.fromState)
    toLabel = label.label(
        basename=git.originURLBasename(), product=args.product, hash=git.hash(), state=args.toState)
    run.run([
        "osmosis", "renamelabel", fromLabel, toLabel,
        "--objectStores=" + config.LOCAL_OSMOSIS])
    if config.WITH_OFFICIAL_OBJECT_STORE:
        run.run([
            "osmosis", "renamelabel", fromLabel, toLabel,
            "--objectStores=" + config.OFFICIAL_OSMOSIS])
else:
    raise AssertionError("No such command")
