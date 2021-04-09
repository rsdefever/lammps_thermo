LAMMPS Thermo
=============
|License|

.. |Codecov| image:: https://codecov.io/gh/rsdefever/ele/branch/master/graph/badge.svg
.. |Azure| image:: https://dev.azure.com/rdefever/ele/_apis/build/status/rsdefever.ele?branchName=master
.. |License| image:: https://img.shields.io/github/license/rsdefever/lammps_thermo

Overview
~~~~~~~~

**LAMMPSThermo** is a lightweight class to extract and manipulate thermodynamic
info from lammps log files. The goal is to make for easy averaging
(via e.g., `numpy`) and plotting (via, e.g., `matplotlib`) of
thermodynamic properties from LAMMPS simulations.

Warning
~~~~~~~

**LAMMPSThermo** is still in early development (0.x releases). The API may
change unexpectedly.

Usage
~~~~~

**LAMMPSThermo** only supports a few modes of use. You can load a LAMMPS
log file into the LAMMPSThermo class and then retrieve properties.

.. code-block:: python

  import lammps_thermo
  # Create the LAMMPSThermo object
  thermo = lammps_thermo.load("example.log")
  # Extract the volume data (assuming it exists in the log file)
  volume = thermo.prop("Volume")

The ``prop`` method will return a numpy array of with the requested property.
You can also specify multiple properties at once.

.. code-block:: python

  data = thermo.prop(["Step", "Volume"])

If ``Step`` or ``Time`` data exist in the log file, you can request only certain time/step bounds:

.. code-block:: python

  volume = thermo.prop("Volume", time_start=1000.0, time_end=10000.0)
  volume = thermo.prop("Volume", step_start=1000, step_end=10000)


Installation
~~~~~~~~~~~~

Installation from source is currently the only option. You can use conda to get the requirements.

.. code-block:: bash

  git clone git@github.com:rsdefever/lammps_thermo
  cd lammps_thermo
  conda create --name lt --file requirements.txt
  conda activate lt
  pip install .
  
