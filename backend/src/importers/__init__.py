"""Hand history importers — pluggable parser architecture.

Adding a new site format requires only:
1. A new parser class implementing AbstractParser
2. A registry entry in registry.py

Zero changes needed to database, API, or frontend.
"""

from backend.src.importers.base import AbstractParser, ParsedAction, ParsedHand, ParsedPlayer
from backend.src.importers.registry import PARSER_REGISTRY

__all__ = [
    "AbstractParser",
    "PARSER_REGISTRY",
    "ParsedAction",
    "ParsedHand",
    "ParsedPlayer",
]
