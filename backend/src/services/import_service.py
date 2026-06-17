"""Import service — hand history parsing and storage.

ADR-002/Pluggable Importer: Adding a new site format requires only a new parser
class + registry entry. Zero changes to database, API, or frontend.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy.orm import Session

from backend.src.importers.base import AbstractParser
from backend.src.importers.registry import PARSER_REGISTRY


class ImportService:
    """Orchestrates hand history import: detect → parse → validate → store."""

    def __init__(self, db: Session):
        self.db = db

    def detect_format(self, raw_text: str) -> str | None:
        """Auto-detect which poker site format a hand history uses.

        Returns:
            Site name string (e.g., 'PokerStars'), or None if undetected.
        """
        for site_name, parser_cls in PARSER_REGISTRY.items():
            parser = parser_cls()
            if parser.detect_format(raw_text):
                return site_name
        return None

    async def import_file(
        self, file_path: Path, site: str | None = None
    ) -> AsyncIterator[dict]:
        """Import hands from a file, yielding progress events.

        Args:
            file_path: Path to the hand history file.
            site: Site name override, or None for auto-detection.

        Yields:
            Progress dicts with status, counts, and errors.
        """
        # TODO: Implement full import pipeline
        yield {"status": "not_implemented", "hands_processed": 0}

    async def import_text(
        self, raw_text: str, site: str
    ) -> AsyncIterator[dict]:
        """Import hands from raw text content.

        Args:
            raw_text: Raw hand history text.
            site: The poker site format (required).

        Yields:
            Progress dicts with status, counts, and errors.
        """
        # TODO: Implement
        yield {"status": "not_implemented", "hands_processed": 0}
