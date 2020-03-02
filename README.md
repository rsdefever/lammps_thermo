lammps_thermo
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.org/REPLACE_WITH_OWNER_ACCOUNT/lammps_thermo.svg?branch=master)](https://travis-ci.org/REPLACE_WITH_OWNER_ACCOUNT/lammps_thermo)
[![codecov](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/lammps_thermo/branch/master/graph/badge.svg)](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/lammps_thermo/branch/master)

Lightweight class to extract and manipulate thermo info from lammps log files. Makes for easy averaging (via e.g., `numpy`) and plotting (via, e.g., `matplotlib`) of thermo properties from LAMMPS simulations.

## WARNING: IN EARLY DEVELOPMENT

## Installation and requirements
Developed for Python 3. Requires `numpy`.

To install, clone the repository to your location of choice and then perform a `pip install`:

	git clone git@github.com:rsdefever/lammps_thermo.git
	cd lammps_thermo/
	pip install .

To check if the installation was sucessful, simply try to import the module from the Python interpreter. In Python:

	import lammps_thermo
	help(lammps_thermo.LAMMPSThermo)

If the doc strings for the `LAMMPSThermo` class print, you are probably good to go.

## Basic usage

LAMMPS thermo info is loaded from a LAMMPS log file:

    filename = PATH_TO_LOGFILE
    thermo = lammps_thermo.load(filename)

The thermo data is stored in a numpy array accessible
via the `data` attribute:

    thermo.data

A list of the thermo properties (extracted from the header of the
thermo section of the log file) is available via the
`available_props()` function:

    thermo.available_props()

To extract a property, e.g., volume, use:

    thermo.prop('Volume')

The data will be returned as a numpy array of shape `(thermo.data.shape[0],1)`
Note the string must match the LAMMPS thermo header. No unit conversions
are performed so all properties remain in the units output by LAMMPS.

You also may specify mulitple properties at once using a list:

    thermo.prop(['Step','Temp'])

The `prop()` function will then return a numpy array of shape
`(thermo.data.shape[0],2)`. A time range may also be specified
with the `tstart` and `tend` parameters. Note that the `Time`
column must be present in the LAMMPS data file in order to use
these options.


Doc strings are available via `help()`.

## A few more details

The default parameters assume that the header for the
thermo data section of the log file starts with the
keyword `Step`, and that the keyword `Step` does not
appear as the first word of any line in the log file
prior to the header. The keyword can be modified to,
e.g., `Time` with the following:

    thermo = lammps_thermo.LAMMPSThermo(filename,start_keyword='Time')

If the required keyword appears as the first word of a line
in the log file before the thermo header, or if there are multiple
thermo sections in the log file and you wish to read a later
section, you may skip the `start_keyword` a specified number of times:

    thermo = lammps_thermo.LAMMPSThermo(filename,start_keyword='Time',skip_sections=2)

The default parameters also assume that the line following
the end of the section of the log file with the thermo data
begins with the word `Loop`. Again, this keyword can be modified:

    thermo = lammps_thermo.LAMMPSThermo(filename,end_keyword='Custom')

If the log file is incomplete, i.e., there is no `end_keyword` because
the thermo data runs to the end of file, use `end_keyword=None` and we
will assume the thermo data runs until the end of file. Note that the
last line is __not__ loaded in under such circumstances, to safeguard
against an incomplete line (i.e., if the simulation is actively running).


### Copyright

Copyright (c) 2019, Ryan S. DeFever


#### Acknowledgements

Project based on the
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.1.
