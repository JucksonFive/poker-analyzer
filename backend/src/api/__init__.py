"""API layer — thin route handlers, no business logic.

Each route handler:
1. Parses/validates the request
2. Delegates to a service
3. Formats the response (status code, JSON)
"""

