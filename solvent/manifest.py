import yaml
import os
import re
from upseto import gitwrapper


class Manifest:
    _FILENAME = "solvent.manifest"

    def __init__(self, data):
        assert isinstance(data, dict)
        assert 'requirements' in data
        self._data = data
        self._assertValid()

    def requirements(self):
        return self._data['requirements'] # pragma: no cover

    def save(self):
        with open(self._FILENAME, "w") as f:
            f.write(yaml.dump(self._data, default_flow_style=False))

    def addRequirement(self, originURL, hash):
        GIT_URL = r'((file|git|ssh|http(s)?)|(git@[\w.]+))(:(//)?)([\w.@\:/-~]+)'
        if re.match(GIT_URL, originURL) is None:
            raise Exception("'%s' is in invalid format for a git repo" % originURL)
        if len(hash.decode('hex')) != 20:
            raise Exception("'%s' is in invalid format for a git hash" % hash)
        for requirement in self._data['requirements']:
            if originURL == requirement['originURL']:
                requirement['hash'] = hash
                return
        self._data['requirements'].append(
            dict(originURL=originURL, hash=hash))

    def findRequirementByBasename(self, basename):
        for requirement in self._data['requirements']:
            if gitwrapper.originURLBasename(requirement['originURL']) == basename:
                return requirement
        raise Exception("Origin URL with the basename '%s' was not found in requirement list", basename)

    def delRequirementByBasename(self, basename):
        self._data['requirements'].remove(self.findRequirementByBasename(basename))

    def _assertValid(self):
        requirements = set()
        for requirement in self._data['requirements']:
            if requirement['originURL'] in requirements:
                raise Exception(
                    "'%s' located twice in requirement list" % requirement['originURL'])  # pragma: no cover
            requirements.add(requirement['originURL'])

    @classmethod
    def fromDir(cls, directory):
        filename = os.path.join(directory, cls._FILENAME)
        with open(filename) as f:
            data = yaml.load(f.read())
        return cls(data)

    @classmethod
    def fromDirOrNew(cls, directory):
        if cls._exists(directory):
            return cls.fromDir(directory)
        else:
            return cls(dict(requirements=[]))

    @classmethod
    def fromLocalDir(cls):
        return cls.fromDir('.')

    @classmethod
    def fromLocalDirOrNew(cls):
        return cls.fromDirOrNew('.')

    @classmethod
    def _exists(cls, directory):
        return os.path.exists(os.path.join(directory, cls._FILENAME))
