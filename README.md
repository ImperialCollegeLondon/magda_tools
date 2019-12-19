# MAGDA Processing Library

Routines used by the [Cassini Magnetometer Data
Archive](https://magda.imperial.ac.uk/) (MAGDA) for data processing
and plotting that may be of general use for working with MAGDA data in
flat file format.

This package implements:
1. A class for reading Magda data files in flat file (ffd) format
2. Routines for calculating a handful of spacecraft position
   properties with respect to Saturn
3. An implementation of an arbitrary order B-field spherical harmonic
   expansion model

# Installation

## From Github

> pip install git+https://github.com/ImperialCollegeLondon/magda_tools

## From Local Copy of Source

> pip install .

or:
> python setup.py install

You can run the tests with:
> python setup.py test

# Usage

Some simple scripts demonstrating the capabilities of the package are
provided in the [examples directory](examples/) of the source
repository. These are the recommended introduction to use of this
package. Some examples additionally require matplotlib to be
installed.
