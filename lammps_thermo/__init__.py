"""
lammps_thermo
Lightweight class to extract and manipulate thermo info from lammps log files
"""

# Add imports here
from .lammps_thermo import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
