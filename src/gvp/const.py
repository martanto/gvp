# Standard library imports
import os

# Third party imports
from typing_extensions import Tuple

user_directory: str = os.path.join(os.path.expanduser("~"))
gvp_directory: str = os.path.join(user_directory, ".gvp")

COMPARATORS: Tuple = (
    "==",
    "like",
    "equal",
    "eq",
    "sama dengan",
    "!=",
    "ne",
    "not equal",
    "tidak sama dengan",
    ">",
    "gt",
    "greater than",
    "lebih besar",
    "lebih besar dari",
    "<",
    "lt",
    "less than",
    "kurang",
    "kurang dari",
    ">=",
    "gte",
    "greater than equal",
    "lebih besar sama dengan",
    "<=",
    "lte",
    "less than equal",
    "kurang dari sama dengan",
)
