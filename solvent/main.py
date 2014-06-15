import argparse
from solvent import submit
from solvent import approve
from solvent import bring
from solvent import config
from solvent import fulfillrequirements
import logging

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
submitbuildCmd = subparsers.add_parser("submitbuild")
submitproductCmd = subparsers.add_parser("submitproduct")
submitproductCmd.add_argument("productname")
submitproductCmd.add_argument("directory")
approveCmd = subparsers.add_parser("approve")
approveCmd.add_argument("--product", default="build")
bringCmd = subparsers.add_parser("bring")
bringCmd.add_argument("--product", required=True)
bringCmd.add_argument("--repositoryBasename", required=True)
bringCmd.add_argument("--hash", default=None)
bringCmd.add_argument("--destination", required=True)
fullfillRequirementsCmd = subparsers.add_parser("fulfillrequirements")
parser.add_argument("--configurationFile", default="/etc/solvent.conf")
args = parser.parse_args()

config.load(args.configurationFile)
if args.cmd == "submitbuild":
    submit.Submit(product="build", directory="..").go()
elif args.cmd == "submitproduct":
    submit.Submit(product=args.productname, directory=args.directory).go()
elif args.cmd == "approve":
    approve.Approve(product=args.product).go()
elif args.cmd == "bring":
    bring.Bring(
        product=args.product, repositoryBasename=args.repositoryBasename,
        hash=args.hash, destination=args.destination).go()
elif args.cmd == "fulfillrequirements":
    fulfillrequirements.FulfillRequirements().go()
else:
    raise AssertionError("No such command")
