# Poker Analytics Platform — Backend API Design

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## 1. API Principles

### 1.1 Conventions

- **Base URL:** `http://localhost:8000/api`
- **Content-Type:** `application/json` (except file uploads: `multipart/form-data`)
- **Naming:** lowercase, hyphenated (`/hand-players`, not `/handPlayers`)
- **Pagination:** Cursor-based for large collections, offset-based for tables
- **Error format:** Consistent JSON error envelope
- **Timestamps:** ISO 8601 in UTC (`2026-06-15T18:30:00Z`)
- **Versioning:** URL prefix `/api/v1/...` added when breaking changes are needed (not in MVP)

### 1.2 Response Envelope

All successful responses follow this structure:

```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 124583,
    "total_pages": 2492
  }
}
```

All error responses:

```json
{
  "error": {
    "code": "HAND_NOT_FOUND",
    "message": "Hand with ID 12345 was not found",
    "details": {}
  }
}
```

### 1.3 Authentication

No authentication in MVP. The application runs locally on the user's machine. A token-based authentication layer will be added post-MVP when cloud sync is introduced.

---

## 2. API Endpoint Map

```
/api
├── /import
│   ├── POST   /upload                    # Upload hand history files
│   ├── GET    /status/{import_id}        # SSE stream for import progress
│   └── GET    /history                   # Past import logs
│
├── /hands
│   ├── GET    /                          # List hands (paginated, filtered)
│   ├── GET    /{hand_id}                 # Get single hand with full detail
│   └── GET    /{hand_id}/actions         # Get all actions for a hand
│
├── /players
│   ├── GET    /                          # List/search players
│   ├── GET    /{player_id}               # Get player profile
│   ├── GET    /{player_id}/stats         # Get player statistics
│   ├── GET    /{player_id}/stats-by-position  # Position-based stats
│   ├── GET    /{player_id}/leaks         # Leak detection results
│   ├── GET    /{player_id}/trends        # Stat trends over time
│   └── POST   /{player_id}/tags         # Add/remove player tag
│
├── /sessions
│   ├── GET    /                          # List sessions
│   ├── GET    /{session_id}              # Get session detail
│   ├── GET    /{session_id}/hands        # Hands in a session
│   ├── PATCH  /{session_id}              # Update session (notes, boundaries)
│   ├── POST   /merge                     # Merge two sessions
│   └── POST   /split                     # Split a session
│
├── /analytics
│   ├── GET    /summary                   # Dashboard summary stats
│   ├── GET    /profit-over-time          # Profit/loss time series
│   ├── GET    /stats-by-position         # Win rate by position (hero)
│   ├── GET    /stats-by-stake            # Win rate by stake
│   ├── GET    /session-stats             # Per-session stat lines
│   └── GET    /heatmap                   # VPIP/PFR heatmap data
│
├── /ai
│   ├── POST   /query                     # Natural language query
│   ├── GET    /suggestions               # Context-aware suggested questions
│   └── GET    /query-history             # Past AI queries
│
└── /settings
    ├── GET    /                          # Get settings
    └── PUT     /                          # Update settings
```

---

## 3. Detailed Endpoint Specifications

### 3.1 Hand Import

#### `POST /api/import/upload`

Upload one or more hand history files for parsing and storage.

**Request:**
```
Content-Type: multipart/form-data

files: [file1.txt, file2.txt, ...]  (max 10 files, 50 MB each)
site_override?: "pokerstars"         (optional — auto-detected if omitted)
```

**Response (202 Accepted):**
```json
{
  "data": {
    "import_id": "imp_abc123",
    "files_received": 3,
    "status": "processing"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": {
    "code": "UNSUPPORTED_FORMAT",
    "message": "Could not detect hand history format for file 'unknown.txt'",
    "details": {
      "filename": "unknown.txt",
      "tried_formats": ["pokerstars", "ggpoker", "ignition"]
    }
  }
}
```

---

#### `GET /api/import/status/{import_id}`

Server-Sent Events stream for real-time import progress.

**SSE Events:**

```
event: progress
data: {"hands_found": 10000, "hands_processed": 4500, "hands_imported": 4480, "hands_skipped": 15, "hands_error": 5, "current_file": "HH20260615.txt"}

event: error
data: {"hand_number": "2482151401", "line": 452, "message": "Unexpected action format"}

event: complete
data: {"total_imported": 9980, "total_skipped": 15, "total_error": 5, "duration_ms": 1234}
```

---

#### `GET /api/import/history`

**Query Params:** `?page=1&page_size=20`

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "filename": "HH20260615.txt",
      "site": "pokerstars",
      "hands_found": 10421,
      "hands_imported": 10412,
      "hands_skipped": 9,
      "hands_error": 0,
      "started_at": "2026-06-15T18:30:00Z",
      "completed_at": "2026-06-15T18:30:02Z",
      "status": "completed"
    }
  ],
  "meta": { "page": 1, "page_size": 20, "total": 15, "total_pages": 1 }
}
```

---

### 3.2 Hands

#### `GET /api/hands`

**Query Params:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default 1) |
| `page_size` | int | Items per page (default 50, max 200) |
| `date_from` | ISO date | Filter start date |
| `date_to` | ISO date | Filter end date |
| `stake_sb` | float | Filter by small blind |
| `stake_bb` | float | Filter by big blind |
| `site` | string | Filter by site |
| `position` | string | Filter by hero position |
| `cards` | string | Hole card filter ("AKs", "JJ+", "72o") |
| `player_name` | string | Hands involving a specific player |
| `result_min` | float | Minimum result in bb |
| `result_max` | float | Maximum result in bb |
| `session_id` | int | Filter by session |
| `sort_by` | string | Column to sort by (default: `played_at`) |
| `sort_dir` | string | `asc` or `desc` (default: `desc`) |

**Response:**
```json
{
  "data": [
    {
      "id": 12345,
      "hand_number": "2482151234",
      "site": "pokerstars",
      "table_name": "Azura",
      "stake_sb": 0.05,
      "stake_bb": 0.10,
      "game_type": "NLHE",
      "num_players": 6,
      "played_at": "2026-06-15T18:30:00Z",
      "hero_position": "CO",
      "hero_cards": ["Js", "Ts"],
      "flop_1": "Kh",
      "flop_2": "7d",
      "flop_3": "2c",
      "turn": "Qs",
      "river": "Ad",
      "total_pot": 2.40,
      "rake": 0.05,
      "hero_net_won": 1.24,
      "showdown": 1
    }
  ],
  "meta": { "page": 1, "page_size": 50, "total": 124583, "total_pages": 2492 }
}
```

---

#### `GET /api/hands/{hand_id}`

**Query Params:** `?include_actions=true`

**Response:**
```json
{
  "data": {
    "hand": {
      "id": 12345,
      "hand_number": "2482151234",
      "site": "pokerstars",
      "table_name": "Azura",
      "stake_sb": 0.05,
      "stake_bb": 0.10,
      "game_type": "NLHE",
      "max_players": 6,
      "num_players": 6,
      "played_at": "2026-06-15T18:30:00Z",
      "flop_1": "Kh", "flop_2": "7d", "flop_3": "2c",
      "turn": "Qs", "river": "Ad",
      "total_pot": 2.40,
      "rake": 0.05
    },
    "players": [
      {
        "id": 201,
        "player_name": "Hero",
        "seat_number": 3,
        "position": "CO",
        "hole_card_1": "Js",
        "hole_card_2": "Ts",
        "starting_stack": 10.00,
        "amount_won": 1.24,
        "is_hero": true,
        "is_winner": true,
        "won_at_showdown": true
      },
      {
        "id": 202,
        "player_name": "Villain1",
        "seat_number": 1,
        "position": "MP",
        "hole_card_1": null,
        "hole_card_2": null,
        "starting_stack": 8.50,
        "amount_won": -0.85,
        "is_hero": false,
        "is_winner": false,
        "won_at_showdown": false
      }
    ],
    "actions": [
      {
        "player_name": "Villain1",
        "street": "PREFLOP",
        "action_type": "RAISE",
        "amount": 0.30,
        "is_all_in": false,
        "seq_number": 1
      },
      {
        "player_name": "Hero",
        "street": "PREFLOP",
        "action_type": "CALL",
        "amount": 0.30,
        "is_all_in": false,
        "seq_number": 2
      }
    ]
  }
}
```

---

### 3.3 Players

#### `GET /api/players`

**Query Params:** `?search=&site=&is_hero=&page=1&page_size=50&sort_by=total_hands&sort_dir=desc`

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "AlexTheGreat",
      "site": "pokerstars",
      "total_hands": 4231,
      "first_seen": "2026-01-15T18:30:00Z",
      "last_seen": "2026-06-15T22:10:00Z",
      "is_hero": true,
      "tags": []
    }
  ],
  "meta": { "page": 1, "page_size": 50, "total": 2847, "total_pages": 57 }
}
```

---

#### `GET /api/players/{player_id}/stats`

**Query Params:** `?date_from=&date_to=&stake_sb=&stake_bb=&min_hands=10`

**Response:**
```json
{
  "data": {
    "player_id": 1,
    "total_hands": 4231,
    "vpip": 24.3,
    "pfr": 18.7,
    "three_bet": 6.2,
    "fold_to_three_bet": 62.1,
    "cbet_flop": 58.3,
    "cbet_turn": 42.1,
    "cbet_river": 35.2,
    "fold_to_cbet_flop": 48.2,
    "fold_to_cbet_turn": 32.1,
    "fold_to_cbet_river": 28.4,
    "aggression_factor": 2.8,
    "aggression_frequency": 42.1,
    "wtsd": 28.3,
    "wmsd": 52.1,
    "bb_per_100": 4.2,
    "net_won": 342.50,
    "hours_played": 28.4
  }
}
```

---

#### `GET /api/players/{player_id}/stats-by-position`

**Response:**
```json
{
  "data": {
    "player_id": 1,
    "positions": [
      {
        "position": "BTN",
        "hands": 712,
        "vpip": 28.1,
        "pfr": 22.3,
        "three_bet": 8.1,
        "cbet_flop": 62.1,
        "aggression_factor": 3.2,
        "wtsd": 28.5,
        "wmsd": 54.2,
        "bb_per_100": 12.4,
        "net_won": 88.30
      }
    ]
  }
}
```

---

#### `GET /api/players/{player_id}/leaks`

**Response:**
```json
{
  "data": {
    "player_id": 1,
    "player_type": "LAG",
    "player_type_confidence": 0.85,
    "leaks": [
      {
        "id": "high_fold_to_3bet",
        "category": "preflop",
        "severity": "medium",
        "stat": "fold_to_three_bet",
        "value": 62.1,
        "threshold": 55.0,
        "direction": "above",
        "title": "Folding too often to 3-bets",
        "description": "Your Fold to 3Bet of 62.1% is above the optimal range of 40-55%. This makes you exploitable — opponents can 3-bet you profitably with any two cards.",
        "suggestion": "Consider defending with a wider range: suited connectors, small-medium pairs in position, and strong broadway hands.",
        "related_stats": [
          {"name": "PFR", "value": 18.7},
          {"name": "4Bet", "value": 2.1}
        ]
      }
    ],
    "leak_count": 3
  }
}
```

---

### 3.4 Sessions

#### `GET /api/sessions`

**Query Params:** `?date_from=&date_to=&stake_sb=&stake_bb=&site=&page=1&page_size=20&sort_by=start_time&sort_dir=desc`

**Response:**
```json
{
  "data": [
    {
      "id": 42,
      "site": "pokerstars",
      "table_name": null,
      "stake_sb": 0.05,
      "stake_bb": 0.10,
      "start_time": "2026-06-15T18:00:00Z",
      "end_time": "2026-06-15T21:45:00Z",
      "duration_minutes": 225,
      "hands_count": 842,
      "net_result": 84.50,
      "bb_per_100": 10.0,
      "notes": "Played well, focused session",
      "table_count": 3
    }
  ],
  "meta": { "page": 1, "page_size": 20, "total": 38, "total_pages": 2 }
}
```

---

#### `GET /api/sessions/{session_id}/hands`

**Query Params:** `?page=1&page_size=50`

**Response:** Same structure as `GET /api/hands` response, filtered to the session.

---

#### `PATCH /api/sessions/{session_id}`

**Request:**
```json
{
  "notes": "Updated session notes",
  "start_time": "2026-06-15T17:55:00Z",
  "end_time": "2026-06-15T21:50:00Z"
}
```

**Response:** Updated session object.

---

### 3.5 Analytics

#### `GET /api/analytics/summary`

**Query Params:** `?date_from=&date_to=&stake_sb=&stake_bb=&site=`

**Response:**
```json
{
  "data": {
    "total_hands": 124583,
    "total_sessions": 342,
    "net_won": 3421.50,
    "bb_per_100": 4.2,
    "hours_played": 342.5,
    "win_rate_per_hour": 9.99,
    "winning_sessions_pct": 58.2,
    "best_session": 245.30,
    "worst_session": -180.20,
    "std_dev_bb_per_100": 42.3,
    "all_in_adj_net_won": 3150.20
  }
}
```

---

#### `GET /api/analytics/profit-over-time`

**Query Params:** `?date_from=&date_to=&stake_sb=&stake_bb=&site=&granularity=day`

| `granularity` | Description |
|---------------|-------------|
| `day` | One data point per day |
| `session` | One data point per session |
| `week` | Aggregated by week |
| `month` | Aggregated by month |

**Response:**
```json
{
  "data": {
    "series": [
      {"date": "2026-01-15", "hands": 842, "net_won": 45.20, "cumulative": 45.20},
      {"date": "2026-01-16", "hands": 631, "net_won": -22.30, "cumulative": 22.90},
      {"date": "2026-01-17", "hands": 0, "net_won": 0, "cumulative": 22.90}
    ]
  }
}
```

---

#### `GET /api/analytics/stats-by-position`

**Response:** Same structure as `GET /api/players/{player_id}/stats-by-position`, filtered to hero.

---

#### `GET /api/analytics/session-stats`

**Query Params:** `?date_from=&date_to=&limit=20`

**Response:** Sessions list with computed stat lines.

---

### 3.6 AI Assistant

#### `POST /api/ai/query`

**Request:**
```json
{
  "question": "What's my win rate with pocket pairs this month?",
  "context": {
    "current_page": "dashboard",
    "filters": {
      "date_from": "2026-06-01",
      "date_to": "2026-06-16"
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "id": "q_abc123",
    "question": "What's my win rate with pocket pairs this month?",
    "answer": "Your win rate with pocket pairs (22-AA) in June 2026 is +3.2 bb/100 over 847 hands.\n\nBreakdown by pair:\n• AA: +12.4 bb/100 (42 hands)\n• KK: +10.1 bb/100 (38 hands)\n• ...\n\n⚠️ You're losing with small/medium pairs. Consider folding 22-66 from early position.",
    "sql_used": "SELECT ...",
    "data_tables": [
      {
        "title": "Win Rate by Pocket Pair",
        "columns": ["Pair", "Hands", "bb/100", "Net Won"],
        "rows": [
          ["AA", 42, 12.4, 52.10],
          ["KK", 38, 10.1, 38.40]
        ]
      }
    ],
    "timestamp": "2026-06-16T10:30:00Z"
  }
}
```

---

#### `GET /api/ai/suggestions`

**Query Params:** `?context=dashboard`

**Response:**
```json
{
  "data": {
    "suggestions": [
      "What's my biggest leak right now?",
      "How has my VPIP changed over the last month?",
      "What stakes am I most profitable at?",
      "Show me my win rate by day of week",
      "Who are my biggest losing opponents?"
    ]
  }
}
```

---

### 3.7 Settings

#### `GET /api/settings`

**Response:**
```json
{
  "data": {
    "hero_name": "AlexTheGreat",
    "hero_site": "pokerstars",
    "default_currency": "USD",
    "session_gap_minutes": 30,
    "date_range_default": "last_30_days",
    "ai_enabled": true,
    "database_path": "/home/user/poker_analytics/data/poker.db",
    "theme": "dark"
  }
}
```

#### `PUT /api/settings`

**Request:** Partial settings object (only fields to update).

**Response:** Complete updated settings object.

---

## 4. SSE (Server-Sent Events)

Used for real-time operations:

| Endpoint | Events |
|----------|--------|
| `GET /api/import/status/{import_id}` | `progress`, `error`, `complete` |
| `POST /api/ai/query` (streaming) | `token`, `data_table`, `done` (future enhancement) |

SSE implementation:

```python
# FastAPI SSE pattern
async def import_status_stream(import_id: str):
    async for event in import_service.get_events(import_id):
        yield f"event: {event.type}\ndata: {json.dumps(event.data)}\n\n"
```

---

## 5. Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `VALIDATION_ERROR` | Request validation failed |
| 400 | `UNSUPPORTED_FORMAT` | Hand history format not recognized |
| 400 | `INVALID_CARD` | Card code format is invalid |
| 400 | `DUPLICATE_IMPORT` | File was already imported (same hash) |
| 404 | `HAND_NOT_FOUND` | Hand ID does not exist |
| 404 | `PLAYER_NOT_FOUND` | Player ID does not exist |
| 404 | `SESSION_NOT_FOUND` | Session ID does not exist |
| 409 | `SESSION_CONFLICT` | Session merge/split would create invalid state |
| 413 | `FILE_TOO_LARGE` | Uploaded file exceeds 50 MB limit |
| 422 | `IMPORT_FAILED` | File could not be parsed |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `AI_UNAVAILABLE` | AI service is not reachable |

---

## 6. Service Layer Design

### 6.1 Service Interfaces

```python
# backend/src/services/interfaces.py

class IHandService(Protocol):
    async def list_hands(self, filters: HandFilters) -> PaginatedResult[HandSummary]: ...
    async def get_hand(self, hand_id: int, include_actions: bool) -> HandDetail: ...
    async def get_hand_actions(self, hand_id: int) -> list[Action]: ...

class IPlayerService(Protocol):
    async def list_players(self, filters: PlayerFilters) -> PaginatedResult[PlayerSummary]: ...
    async def get_player(self, player_id: int) -> PlayerProfile: ...
    async def get_player_stats(self, player_id: int, filters: StatFilters) -> PlayerStats: ...
    async def get_stats_by_position(self, player_id: int, filters: StatFilters) -> list[PositionStats]: ...
    async def get_player_leaks(self, player_id: int) -> LeakAnalysis: ...

class IImportService(Protocol):
    async def upload_files(self, files: list[UploadFile], site_override: str | None) -> ImportResult: ...
    async def get_events(self, import_id: str) -> AsyncIterator[ImportEvent]: ...
    async def get_history(self, page: int, page_size: int) -> PaginatedResult[ImportLog]: ...

class IAnalyticsService(Protocol):
    async def get_summary(self, filters: AnalyticsFilters) -> SummaryStats: ...
    async def get_profit_over_time(self, filters: AnalyticsFilters, granularity: str) -> TimeSeries: ...
    async def get_stats_by_position(self, filters: AnalyticsFilters) -> list[PositionStats]: ...
    async def get_session_stats(self, filters: AnalyticsFilters, limit: int) -> list[SessionStats]: ...

class IAIService(Protocol):
    async def query(self, question: str, context: dict) -> AIResponse: ...
    async def get_suggestions(self, context: str) -> list[str]: ...

class ISessionService(Protocol):
    async def list_sessions(self, filters: SessionFilters) -> PaginatedResult[SessionSummary]: ...
    async def get_session(self, session_id: int) -> SessionDetail: ...
    async def update_session(self, session_id: int, updates: SessionUpdate) -> SessionDetail: ...
    async def merge_sessions(self, session_ids: list[int]) -> SessionDetail: ...
    async def split_session(self, session_id: int, split_point_hand_id: int) -> list[SessionDetail]: ...
```

### 6.2 Dependency Injection

Services are wired via FastAPI's dependency injection:

```python
# backend/src/api/dependencies.py

async def get_hand_service(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> IHandService:
    repo = HandRepository(session)
    return HandService(repo)

# In route:
@router.get("/hands")
async def list_hands(
    filters: Annotated[HandFilters, Query()],
    hand_service: Annotated[IHandService, Depends(get_hand_service)]
):
    return await hand_service.list_hands(filters)
```

---

## 7. Performance & Rate Limiting

| Strategy | Implementation |
|----------|---------------|
| Response caching | In-memory TTL cache for expensive analytics queries (60s TTL) |
| Pagination max | Enforced at repository layer (max 200 per page) |
| File upload limit | 50 MB per file, 10 files per request |
| Import concurrency | Only one import at a time; others queued |
| Database connection | Single connection with WAL mode; connection pool for future |

---

*Next: [Development Roadmap](./07-development-roadmap.md)*
