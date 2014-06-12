import argparse
from solvent import submitbuild
from solvent import approve
from solvent import config
from solvent import fulfillrequirements
import logging

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
submitbuildCmd = subparsers.add_parser("submitbuild")
approveCmd = subparsers.add_parser("approve")
approveCmd.add_argument("--product", default="build")
publish = subparsers.add_parser("publish")
fullfillRequirementsCmd = subparsers.add_parser("fulfillrequirements")
parser.add_argument("--configurationFile", default="/etc/solvent.conf")
args = parser.parse_args()

config.load(args.configurationFile)
if args.cmd == "submitbuild":
    submitbuild.SubmitBuild().go()
elif args.cmd == "approve":
    approve.Approve(product=args.product).go()
elif args.cmd == "fulfillrequirements":
    fulfillrequirements.FulfillRequirements().go()
else:
    raise AssertionError("No such command")
