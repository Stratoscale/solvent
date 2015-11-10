import os
from setuptools import setup


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
)
