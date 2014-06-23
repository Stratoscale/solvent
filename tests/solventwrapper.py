import subprocess
import os


configurationFile = None


def _config():
    global configurationFile
    return " --configurationFile=%s " % configurationFile


def configureAsOfficial():
    with open(configurationFile, "a") as f:
        f.write("OFFICIAL_BUILD: Yes\n")


def configureAsNonOfficial():
    with open(configurationFile) as f:
        contents = f.read()
    with open(configurationFile, "w") as f:
        for line in contents.strip().split("\n"):
            if line.startswith("OFFICIAL_BUILD:"):
                continue
            f.write(line + "\n")


def configureNoOfficial():
    with open(configurationFile, "a") as f:
        f.write("WITH_OFFICIAL_OBJECT_STORE: No\n")


def run(where, arguments, env=dict()):
    environment = dict(os.environ)
    environment.update(env)
    if not isinstance(where, str):
        where = where.directory()
    try:
        output = subprocess.check_output(
            "coverage run --parallel-mode -m solvent.main " + _config() + arguments,
            cwd=where, shell=True, stderr=subprocess.STDOUT, close_fds=True, env=environment)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output


def upseto(where, arguments):
    if not isinstance(where, str):
        where = where.directory()
    try:
        output = subprocess.check_output(
            "python -m upseto.main " + arguments, cwd=where,
            shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output


def runShouldFail(where, arguments, partOfErrorMessage, env=dict()):
    environment = dict(os.environ)
    environment.update(env)
    if not isinstance(where, str):
        where = where.directory()
    try:
        output = subprocess.check_output(
            "coverage run --parallel-mode -m solvent.main " + _config() + arguments,
            cwd=where, shell=True, stderr=subprocess.STDOUT, close_fds=True, env=environment)
    except subprocess.CalledProcessError as e:
        if partOfErrorMessage in e.output.lower():
            return
        else:
            print e.output
            raise Exception((
                "Expected solvent command '%s' to fail with the error '%s', "
                "but it failed with '%s'") % (arguments, partOfErrorMessage, e.output))
    print output
    raise Exception("Expected solvent command '%s' to fail, but it didn't" % arguments)


def runWhatever(where, commandLine):
    if not isinstance(where, str):
        where = where.directory()
    try:
        output = subprocess.check_output(
            commandLine,
            cwd=where, shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output
