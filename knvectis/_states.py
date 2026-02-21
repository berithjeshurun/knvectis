# knvectis/_states.py
from enum import Enum, Flag, auto
from typing import Any, Optional, List, Dict, Set, Union, Callable

__all__ = [
    "TraversalMode",
    "RelationshipType",
    "MatchLevel",
    "PruneFrom",
    "PruneType",
    "NotifyMode"
]

# HeHeHe :)
class TraversalMode(Enum):
    FRONT_FOOTPRINT = "front"      # Root -> Leaves (causal flow)
    REVERSE_FOOTPRINT = "reverse"  # Leaves -> Root (dependency flow) 
    TRANSVERSE = "transverse"      # Cross-hierarchical connections

class RelationshipType(Enum):
    INFLUENCES = "influences"
    DEPENDS_ON = "depends_on"
    REFERENCES = "references"
    EXTENDS = "extends"
    CONTRADICTS = "contradicts"

class MatchLevel(Enum):
    LEAF = 3
    BRANCH = 2
    TREE = 1


class PruneFrom(Enum):
    FORWARD = auto()
    BACKWARD = auto()

class PruneType(Enum):
    DISCARD = auto()
    DESTROY = auto()

class NotifyMode(Enum):
    RAISE = auto()
    CALL = auto()
    SUPPRESS = auto()
