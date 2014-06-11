import argparse
from solvent import submitbuild
from solvent import config
from solvent import run
from upseto import gitwrapper
import logging

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
submitbuildCmd = subparsers.add_parser("submitbuild")
publish = subparsers.add_parser("publish")
parser.add_argument("--configurationFile", default="/etc/solvent.conf")
args = parser.parse_args()

config.load(args.configurationFile)
if args.cmd == "submitbuild":
    submitbuild.SubmitBuild().go()
else:
    raise AssertionError("No such command")
