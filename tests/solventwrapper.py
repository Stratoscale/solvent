import subprocess


configurationFile = None


def _config():
    global configurationFile
    return " --configurationFile=%s " % configurationFile


def configureAsOfficial():
    with open(configurationFile, "a") as f:
        f.write("OFFICIAL_BUILD: Yes\n")


def run(where, arguments):
    try:
        output = subprocess.check_output(
            "coverage run --parallel-mode -m solvent.main " + _config() + arguments,
            cwd=where.directory(), shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output


def upseto(where, arguments):
    try:
        output = subprocess.check_output(
            "python -m upseto.main " + arguments, cwd=where.directory(),
            shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output


def runShouldFail(where, arguments, partOfErrorMessage):
    try:
        output = subprocess.check_output(
            "coverage run --parallel-mode -m solvent.main " + _config() + arguments,
            cwd=where.directory(), shell=True, stderr=subprocess.STDOUT, close_fds=True)
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
    try:
        output = subprocess.check_output(
            commandLine,
            cwd=where, shell=True, stderr=subprocess.STDOUT, close_fds=True)
    except subprocess.CalledProcessError as e:
        print e.output
        raise
    return output
