import yaml
import os
from upseto import gitwrapper


class Manifest:
    _FILENAME = "solvent.manifest"

    def __init__(self, data, originURL):
        assert isinstance(data, dict)
        assert 'requirements' in data
        self._data = data
        self._originURL = originURL
        self._assertValid()

    def save(self):
        with open(self._FILENAME, "w") as f:
            f.write(yaml.dump(self._data, default_flow_style=False))

    @classmethod
    def _fromDir(cls, directory):
        filename = os.path.join(directory, cls._FILENAME)
        with open(filename) as f:
            data = yaml.load(f.read())
        return cls(data, cls._originURL(directory))

    @classmethod
    def _fromDirOrNew(cls, directory):
        if cls._exists(directory):
            return cls.fromDir(directory)
        else:
            return cls(dict(requirements=[]), cls._originURL(directory))

    @classmethod
    def fromLocalDir(cls):
        return cls._fromDir('.')

    @classmethod
    def fromLocalDirOrNew(cls):
        return cls._fromDirOrNew('.')

    @classmethod
    def _exists(cls, directory):
        return os.path.exists(os.path.join(directory, cls._FILENAME))

    def _assertValid(self):
        pass

    @classmethod
    def _originURL(self, directory):
        return gitwrapper.GitWrapper(directory).originURL()
