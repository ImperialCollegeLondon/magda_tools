from pathlib import Path
from setuptools import setup

base_path = Path(__file__).parent

with open(base_path / "requirements.txt") as f:
    requirements = f.readlines()

with open(base_path / "requirements_dev.txt") as f:
    requirements_dev = f.readlines()

description = """This package implements:
1) A class for reading Magda data files in flat file (ffd) format
2) Routines for calculating a handful of spacecraft position properties
   with respect to Saturn
3) An implementation of an arbitrary order B-field spherical harmonic expansion model"""

setup(
    name="magda_tools",
    version="0.1",
    description="A collection of tools for working with MAGDA data files",
    long_description=description,
    url="https://github.com/ImperialCollegeLondon/magda_tools",
    author="Research Software Engineering Group, Imperial College",
    author_email="",
    packages=["magda_tools"],
    python_requires=">=3.7",
    install_requires=requirements,
    tests_require=requirements_dev,
    project_urls={"Source": "https://github.com/ImperialCollegeLondon/magda_tools"},
)
