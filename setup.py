import os
import os.path
from setuptools import setup


BASH_COMPLETION = os.path.expanduser('~/.bash_completion') if os.getuid() != 0 else '/etc/bash_completion.d'
data_files = [
    (BASH_COMPLETION, ['conf/bash_completion.d/solvent.sh']),
]
if os.geteuid() == 0 and not os.path.exists('/etc/solvent.conf'):
    data_files.append(("/etc", ['conf/solvent.conf']))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="solvent",
    version="1.0",
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
        "PyYAML==3.11",
        "upseto",
    ],
    include_package_data=True,
    data_files=data_files,
    scripts=['sh/solvent']
)
