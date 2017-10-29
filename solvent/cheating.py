import argparse
from solvent import label
from solvent import config
from solvent import run
from strato.racktest.infra import gitwrapper
import logging
import os


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
changeStateCmd = subparsers.add_parser("changestate")
changeStateCmd.add_argument("--basename", default=None)
changeStateCmd.add_argument("--hash", default=None)
changeStateCmd.add_argument("--product", required=True)
changeStateCmd.add_argument("--fromState", required=True)
changeStateCmd.add_argument("--toState", required=True)
parser.add_argument("--configurationFile", default="/etc/solvent.conf")
args = parser.parse_args()

config.load(args.configurationFile)
if args.cmd == "changestate":
    hash = args.hash
    if hash is None:
        git = gitwrapper.GitWrapper(os.getcwd())
        hash = git.hash()
    basename = args.basename
    if basename is None:
        git = gitwrapper.GitWrapper(os.getcwd())
        basename = git.originURLBasename()
    fromLabel = label.label(basename=basename, product=args.product, hash=hash, state=args.fromState)
    toLabel = label.label(basename=basename, product=args.product, hash=hash, state=args.toState)
    run.run([
        "osmosis", "renamelabel", fromLabel, toLabel,
        "--objectStores=" + config.LOCAL_OSMOSIS])
    if config.WITH_OFFICIAL_OBJECT_STORE:
        run.run([
            "osmosis", "renamelabel", fromLabel, toLabel,
            "--objectStores=" + config.OFFICIAL_OSMOSIS])
else:
    raise AssertionError("No such command")
