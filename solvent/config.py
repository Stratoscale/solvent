import yaml

LOCAL_OSMOSIS = 'localhost:1010'
OFFICIAL_OSMOSIS = None
OFFICIAL_BUILD = False


def load(filename):
    with open(filename) as f:
        data = yaml.load(f.read())
    if data is None:
        raise Exception("Configuration file must not be empty")
    globals().update(data)
    if OFFICIAL_OSMOSIS is None:
        raise Exception("Configuration file must contain 'OFFICIAL_OSMOSIS' field")


def localOsmosisHostname():
    return LOCAL_OSMOSIS.split(":")[0]


def localOsmosisPort():
    return int(LOCAL_OSMOSIS.split(":")[1])


def officialOsmosisHostname():
    return OFFICIAL_OSMOSIS.split(":")[0]


def officialOsmosisPort():
    return int(OFFICIAL_OSMOSIS.split(":")[1])
