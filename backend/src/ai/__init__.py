"""AI assistant module — Anthropic API integration.

The AI assistant translates natural language questions into SQL queries,
executes them read-only against the local database, and formats natural
language responses. This is the ONLY module that communicates externally.
"""

from backend.src.ai.assistant import AIAssistant

__all__ = ["AIAssistant"]
