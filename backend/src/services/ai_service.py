"""AI service — natural language queries over poker data.

The AI assistant translates user questions into SQL, executes them read-only,
and formats natural language responses. This is the ONLY component that
communicates with an external service (Anthropic API).
"""

from __future__ import annotations

from sqlalchemy.orm import Session


class AIService:
    """Natural language query interface for poker data analysis.

    Flow: User question → SQL generation (via Anthropic) → execute (read-only) →
    format response.
    """

    def __init__(self, db: Session):
        self.db = db

    async def query(self, question: str) -> dict:
        """Process a natural language question about poker data.

        Args:
            question: User's question in natural language.

        Returns:
            {question, answer, sql_used, data} dict.
        """
        # TODO: Implement Anthropic API integration
        return {
            "question": question,
            "answer": "AI assistant not yet implemented.",
            "sql_used": None,
            "data": None,
        }

    async def _generate_sql(self, question: str) -> str:
        """Generate a SQL query from a natural language question.

        Uses the Anthropic API with strict safety constraints:
        read-only, no destructive operations, timeout enforced.
        """
        # TODO: Implement Anthropic API call with safety prompts
        return ""

    def _execute_readonly(self, sql: str) -> list[dict]:
        """Execute a read-only SQL query and return results.

        Enforces read-only at the connection level. Rejects any
        INSERT/UPDATE/DELETE/ALTER/DROP statements.
        """
        # TODO: Implement with read-only connection
        return []

    async def format_response(self, question: str, sql: str, data: list[dict]) -> str:
        """Format query results into a natural language response.

        Uses Anthropic API to convert data rows back to human-readable text.
        """
        # TODO: Implement
        return ""
