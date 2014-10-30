from solvent import run
import os


class CommonMistakes:
    def checkDirectoryBeforeSubmission(self, dir):
        under = self.mountedUnder(dir)
        if len(under) > 0:
            message = "there are active mount points mounted under '%s':\n%s" % (
                dir, "\n".join([m['path'] for m in under]))
            raise Exception(
                "Common mistakes protections found the following. Please correct "
                "it, or pass the --noCommonMistakesProtection.\n" + message)

    @classmethod
    def _mount(cls):
        output = run.run(["mount"])
        result = []
        for line in output.strip().split("\n"):
            fields = line.split(" ")
            assert fields[1] == "on", "'mount' output line is in wrong format"
            result.append(dict(type=fields[4], path=fields[2]))
        return result

    @classmethod
    def mountedUnder(cls, dir):
        realPath = os.path.realpath(dir)
        return [m for m in cls._mount() if m['path'].startswith(realPath)]
