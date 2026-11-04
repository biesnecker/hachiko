import os
from distutils.core import setup
from hachiko.version import __version__


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


exec(open("hachiko/version.py").read())

setup(
    name="hachiko",
    version=__version__,
    author="John Biesnecker",
    author_email="jbiesnecker@gmail.com",
    url="https://github.com/biesnecker/hachiko",
    packages=["hachiko"],
    package_dir={"hachiko": "./hachiko"},
    install_requires=["watchdog>=5.0.0"],
    description="Asyncio wrapper around watchdog.",
    license="mit",
    long_description=read("README.txt"),
)
