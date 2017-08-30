import subprocess
import logging
import os


def fix_env_in_case_of_invalid_locale_name(env):
    """See https://github.com/ros-drivers/hokuyo_node/issues/3"""
    env["LC_ALL"] = "C"


def run(command, cwd=None):
    env = os.environ.copy()
    fix_env_in_case_of_invalid_locale_name(env)
    try:
        return subprocess.check_output(command, cwd=cwd, stderr=subprocess.STDOUT, stdin=open("/dev/null"),
                                       close_fds=True, env=env)
    except subprocess.CalledProcessError as e:
        logging.error("Failed command '%s' output:\n%s" % (command, e.output))
        raise
