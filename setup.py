import os
import os.path
from setuptools import setup
from os.path import expanduser

data_files = []

# add in case we are running as root
if os.geteuid() == 0:
    data_files += [
        ('/etc/bash_completion.d', ['conf/bash_completion.d/solvent.sh']),
    ]
    if not os.path.exists("/etc/solvent.conf"):
        data_files += [
            ("/etc", ['conf/solvent.conf']),
        ]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="solvent",
    version="1.1",
    author="Shlomo Matichin",
    author_email="shlomi@stratoscale.com",
    description=(
        "Manage official build product flow, using osmosis as a transport"),
    keywords="git repos repositories scm buildproducts build products",
    url="http://packages.python.org/solvent",
    packages=['solvent'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    install_requires=[
    ],
    include_package_data=True,
    data_files=data_files,
    scripts=['sh/solvent']
)
