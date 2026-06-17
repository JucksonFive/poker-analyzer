"""Parser registry — maps site names to parser classes.

To add a new site format:
1. Create a parser class implementing AbstractParser
2. Add it to the PARSER_REGISTRY dict below
3. Done — the API's /api/import/formats and auto-detection pick it up automatically
"""

from __future__ import annotations

from typing import Type

from backend.src.importers.base import AbstractParser

# Parser classes are imported as they're implemented
# from backend.src.importers.pokerstars import PokerStarsParser
# from backend.src.importers.ggpoker import GGPokerParser
# from backend.src.importers.ignition import IgnitionParser
# from backend.src.importers.winamax import WinamaxParser
# from backend.src.importers.partypoker import PartyPokerParser
# from backend.src.importers.ipoker import IPokerParser

PARSER_REGISTRY: dict[str, Type[AbstractParser]] = {
    # MVP formats
    # "PokerStars": PokerStarsParser,
    # "GGPoker": GGPokerParser,
    # "Ignition": IgnitionParser,
    # Post-MVP formats
    # "Winamax": WinamaxParser,
    # "PartyPoker": PartyPokerParser,
    # "iPoker": IPokerParser,
}
