import argparse
from solvent import submit
from solvent import approve
from solvent import bring
from solvent import localize
from solvent import config
from solvent import fulfillrequirements
from solvent import checkrequirements
from solvent import manifest
from solvent import requirementlabel
import logging

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="cmd")
submitbuildCmd = subparsers.add_parser(
    "submitbuild",
    help="submit the current workspace as a built version of this git project")
submitproductCmd = subparsers.add_parser(
    "submitproduct",
    help="create a specific build product, and submit it in candidate state")
submitproductCmd.add_argument("productname")
submitproductCmd.add_argument("directory")
approveCmd = subparsers.add_parser(
    "approve",
    help="promote a candidate build product to a non candidate. E.g., if "
    "on submitproduct the product was in 'cleancandidate' state, it will "
    "be switched to 'clean' state")
approveCmd.add_argument("--product", default="build")
bringCmd = subparsers.add_parser(
    "bring", help="checkout specific prebuilt build product")
bringCmd.add_argument("--product", required=True)
bringCmd.add_argument("--repositoryBasename", required=True)
bringCmd.add_argument(
    "--hash", default=None,
    help="if not specified, hash a requirement matching the repositoryBasename "
    "must exist in solvent.manifest . Using this specific argument is not "
    "recommended (automatic inspection will not be able to detect the "
    "dependency if it's not updated in the manifest)")
bringCmd.add_argument(
    "--destination", required=True, help="destination directory")
bringlabelCmd = subparsers.add_parser(
    "bringlabel", help="checkout specific label")
bringlabelCmd.add_argument("--label", required=True)
bringlabelCmd.add_argument(
    "--destination", required=True, help="destination directory")
localizeCmd = subparsers.add_parser(
    "localize", help="make sure a specific label exists in local osmosis object "
    "store, or fetch it from the official server (useful for rackattack-virtual)")
localizeCmd.add_argument("--label", required=True)
addRequirementCmd = subparsers.add_parser(
    "addrequirement",
    help="add dependency on build products (not an upseto dependency)")
addRequirementCmd.add_argument("--originURL", required=True)
addRequirementCmd.add_argument("--hash", required=True)
removeRequirementCmd = subparsers.add_parser(
    "removerequirement",
    help="remove the dependency on build products")
removeRequirementCmd.add_argument("--originURLBasename", required=True)
fullfillRequirementsCmd = subparsers.add_parser(
    "fulfillrequirements",
    help="fulfill upseto requirements using ready build products")
checkRequirementsCmd = subparsers.add_parser(
    "checkrequirements",
    help="check upseto and solvent requirements labels exist in either local or "
    "official objects stores")
parser.add_argument(
    "--configurationFile", default="/etc/solvent.conf",
    help="override configuration file location")
subparsers.add_parser(
    "printobjectstores",
    help="print the current configuration in an osmosis --objectStores= "
    "format")
printLabelCmd = subparsers.add_parser(
    "printlabel",
    help="print the current label of a dependency")
printLabelCmd.add_argument("--product", required=True)
printLabelCmd.add_argument("--repositoryBasename", required=True)
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
elif args.cmd == "bringlabel":
    bring.Bring.label(args.label, args.destination)
elif args.cmd == "localize":
    localize.Localize(
        label=args.label).go()
elif args.cmd == "fulfillrequirements":
    fulfillrequirements.FulfillRequirements().go()
elif args.cmd == "checkrequirements":
    checkrequirements.CheckRequirements().go()
elif args.cmd == "addrequirement":
    mani = manifest.Manifest.fromLocalDirOrNew()
    mani.addRequirement(originURL=args.originURL, hash=args.hash)
    mani.save()
elif args.cmd == "removerequirement":
    mani = manifest.Manifest.fromLocalDir()
    mani.delRequirementByBasename(basename=args.originURLBasename)
    mani.save()
elif args.cmd == "printobjectstores":
    print config.objectStoresOsmosisParameter()
elif args.cmd == "printlabel":
    label = requirementlabel.RequirementLabel(
        basename=args.repositoryBasename, product=args.product, hash=None)
    print label.matching()
else:
    raise AssertionError("No such command")
