import pkg_resources

__all__ = [
    "VERSION", "__version__", "__short_version__", "Unit", "load", "export", "CriptDB",
    "User", "Group", "Collection", "Publication", "Experiment", "Material", "Process", "Data",
    "Inventory", "Simulation", "Cond", "Prop", "Ingr", "Iden", "Path", "File"
]

# single-sourcing the package version
__version__ = "0.0.3"

VERSION = __version__
__short_version__ = "0.0.3"


# Units
import pint
u = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
Unit = u.Unit
Quantity = u.Quantity

from pathlib import Path


class CRIPTError(Exception):

    def __init__(self, message):
        self.message = message


class CRIPTWarning(Warning):

    def __init__(self, message):
        self.message = message


# Core CRIPT objects (order important)
from .base import *
from .doc_tools import *
from .cond import *
from .prop import *
from .user import *
from .group import *
from .publication import *
from .collection import *
from .experiment import *
from .inventory import *
from .data import *
from .material import *
from .process import *
from .simulation import *
from .database import *

# Get CRIPT types in a dict
from inspect import getmembers, isclass
cript_types = {pair[0]: pair[1] for pair in getmembers(sys.modules[__name__], isclass) if "cript." in str(pair[1])}
cript_types["Unit"] = Unit
cript_types["Quantity"] = Quantity
cript_types["Path"] = Path

for node in cript_types.values():
    if hasattr(node, "_init_"):
        node._init_()
