"""
Unit and regression test for the lammps_thermo package.
"""

# Import package, test suite, and other packages as needed
import lammps_thermo
import pytest
import sys

def test_lammps_thermo_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "lammps_thermo" in sys.modules
