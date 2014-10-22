import yaml
import os

LOCAL_OSMOSIS_IF_ROOT = 'localhost:1010'
LOCAL_OSMOSIS_IF_NOT_ROOT = 'localhost:1010'
LOCAL_OSMOSIS = None
OFFICIAL_OSMOSIS = None
OFFICIAL_BUILD = False
WITH_OFFICIAL_OBJECT_STORE = True
CLEAN = False
FORCE = False


def load(filename):
    with open(filename) as f:
        data = yaml.load(f.read())
    if data is None:
        raise Exception("Configuration file must not be empty")
    globals().update(data)
    if 'SOLVENT_CONFIG' in os.environ:
        data = yaml.load(os.environ['SOLVENT_CONFIG'])
        globals().update(data)
    if 'SOLVENT_CLEAN' in os.environ:
        global CLEAN
        CLEAN = True
    if WITH_OFFICIAL_OBJECT_STORE and OFFICIAL_OSMOSIS is None:
        raise Exception("Configuration file must contain 'OFFICIAL_OSMOSIS' field")
    global LOCAL_OSMOSIS
    if LOCAL_OSMOSIS is None:
        if os.getuid() == 0:
            LOCAL_OSMOSIS = LOCAL_OSMOSIS_IF_ROOT
        else:
            LOCAL_OSMOSIS = LOCAL_OSMOSIS_IF_NOT_ROOT


def objectStoresOsmosisParameter():
    if WITH_OFFICIAL_OBJECT_STORE:
        return LOCAL_OSMOSIS + "+" + OFFICIAL_OSMOSIS
    else:
        return LOCAL_OSMOSIS
