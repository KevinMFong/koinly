#!/usr/bin/env python

"""The setup script."""
import os

from setuptools import find_packages, setup

NAME = "koinly"
VERSION = os.environ.get(f"{NAME.upper()}_PACKAGE_VERSION")
HERE = os.path.abspath(os.path.dirname(__file__))
ABOUT = {}
if not VERSION:
    # Load the package's __version__.py module as a dictionary.
    with open(os.path.join(HERE, "src", NAME, "__version__.py")) as f:
        exec(f.read(), ABOUT)
else:
    ABOUT["__version__"] = VERSION

setup(
    name=NAME,
    author="Kevin Fong",
    author_email="22036173+KevinMFong@users.noreply.github.com",
    python_requires="~=3.10",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    description="Koinly command line interface.",
    install_requires=[
        "click~=8.1",
        "marshmallow~=3.19",
        "python-dateutil~=2.8",
        "requests~=2.28",
        "typer[all]~=0.7",
    ],
    license="MIT license",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/KevinMFong/koinly",
    version=ABOUT["__version__"],
    entry_points={
        "console_scripts": [
            "koinly=koinly.cli:app",
        ],
    },
)
