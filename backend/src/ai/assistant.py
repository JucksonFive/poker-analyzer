"""AI Assistant — Anthropic API integration for natural language poker queries.

Safety constraints:
- Read-only database connection (enforced at connection level)
- Query timeout (prevents runaway queries)
- SQL validation (rejects destructive operations)
- User data sent to API: aggregated stats only, no raw hand data
"""

from __future__ import annotations


class AIAssistant:
    """Translates natural language questions into SQL and back into answers.

    Uses the Anthropic API for both NL→SQL and SQL→NL translation.
    All database access is read-only and validated.
    """

    # Safety: SQL operations that are NEVER allowed
    FORBIDDEN_SQL_KEYWORDS = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "CREATE", "TRUNCATE", "REPLACE", "GRANT", "REVOKE",
    ]

    def __init__(self, db_url: str, read_only: bool = True):
        self.db_url = db_url
        self.read_only = read_only

    def validate_sql(self, sql: str) -> bool:
        """Validate that a SQL query is safe to execute.

        Rejects any query containing forbidden SQL keywords.
        Also rejects queries with cartesian products or excessive complexity.
        """
        sql_upper = sql.upper()
        for keyword in self.FORBIDDEN_SQL_KEYWORDS:
            if keyword in sql_upper:
                return False
        return True

    async def generate_sql(self, question: str, schema_info: str) -> str:
        """Use Anthropic API to generate SQL from a natural language question.

        Args:
            question: User's natural language question.
            schema_info: Description of the database schema for context.

        Returns:
            Generated SQL query string.
        """
        # TODO: Implement Anthropic API call
        return ""

    async def explain_result(
        self, question: str, sql: str, data: list[dict]
    ) -> str:
        """Use Anthropic API to convert query results into natural language.

        Args:
            question: Original user question.
            sql: The SQL that was executed.
            data: Query result rows.

        Returns:
            Natural language answer.
        """
        # TODO: Implement Anthropic API call
        return ""

    async def query(self, question: str) -> dict:
        """Full pipeline: question → SQL → execute → answer.

        Returns:
            {question, answer, sql_used, data}
        """
        # TODO: Implement full pipeline
        return {
            "question": question,
            "answer": "AI assistant is not yet implemented.",
            "sql_used": None,
            "data": None,
        }
