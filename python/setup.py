import os

from typing import List
from setuptools import setup, find_packages


with open("VERSION", "r") as f:
    version = f.read().rstrip()

install_requires: List[str] = []
docs_require: List[str] = []
tests_require = ["pytest", "pytest-cov"]

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, "README.md")).read()
except IOError:
    README = ""

try:
    CHANGES = open(os.path.join(here, "CHANGES.txt")).read()
except IOError:
    CHANGES = ""

setup(
    name="snippets",
    version=version,
    description="snippet-stuff",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"testing": tests_require, "docs": docs_require},
    entry_points={"console_scripts": ["snippets = snippets.main:cli"]},
)
