# Poker Analytics Platform — System Architecture

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## 1. Architectural Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S MACHINE                           │
│                                                                 │
│  ┌──────────────────────┐          ┌─────────────────────────┐  │
│  │     FRONTEND          │  HTTP    │       BACKEND           │  │
│  │  React + TypeScript   │◄───────►│   FastAPI + Python      │  │
│  │  Vite dev server      │ REST/WS  │   Uvicorn server        │  │
│  │                       │          │                         │  │
│  │  ┌─────────────────┐  │          │  ┌──────────────────┐   │  │
│  │  │ Feature Modules  │  │          │  │  API Layer       │   │  │
│  │  │ - Dashboard      │  │          │  │  (thin routes)   │   │  │
│  │  │ - Hand Explorer  │  │          │  ├──────────────────┤   │  │
│  │  │ - Player Analysis│  │          │  │  Service Layer   │   │  │
│  │  │ - AI Assistant   │  │          │  │  (business logic)│   │  │
│  │  │ - Import         │  │          │  ├──────────────────┤   │  │
│  │  │ - Session Tracker│  │          │  │  Repository      │   │  │
│  │  └─────────────────┘  │          │  │  Layer (data)     │   │  │
│  │                       │          │  ├──────────────────┤   │  │
│  │  ┌─────────────────┐  │          │  │  Import Engine   │   │  │
│  │  │ State Management │  │          │  ├──────────────────┤   │  │
│  │  │ (Zustand)       │  │          │  │  Analytics Engine│   │  │
│  │  └─────────────────┘  │          │  ├──────────────────┤   │  │
│  │                       │          │  │  AI Service      │   │  │
│  │  ┌─────────────────┐  │          │  └──────────────────┘   │  │
│  │  │ API Client       │  │          │                         │  │
│  │  │ (fetch wrapper)  │  │          │  ┌──────────────────┐   │  │
│  │  └─────────────────┘  │          │  │  Poker Engine     │   │  │
│  └──────────────────────┘          │  │  (pure Python)    │   │  │
│                                    │  └──────────────────┘   │  │
│                                    │                         │  │
│                                    │  ┌──────────────────┐   │  │
│                                    │  │  SQLite Database  │   │  │
│                                    │  │  (single file)    │   │  │
│                                    │  └──────────────────┘   │  │
│                                    └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Process Model

The application runs as a **single process** on the user's machine:

- **Backend:** Uvicorn serves the FastAPI application on `localhost:8000`
- **Frontend:** Vite dev server (development) or static files served by FastAPI (production) on `localhost:5173` / `localhost:8000`
- **Database:** SQLite file on disk; accessed exclusively by the backend process

In production, the frontend is built to static files and served directly by FastAPI, eliminating the need for a separate frontend server.

```
Development:
  Browser :5173 ──► Vite Dev Server ──(proxy)──► FastAPI :8000 ──► SQLite

Production:
  Browser :8000 ──► FastAPI (serves static + API) ──► SQLite
```

---

## 2. Module Architecture

### 2.1 Poker Engine (`poker-engine/`)

The poker engine is a **pure Python library** with zero dependencies outside the Python standard library. It is versioned independently and could be extracted to its own package.

**Public API Surface:**

```
poker-engine/
├── src/
│   ├── __init__.py
│   ├── cards.py          # Card, Rank, Suit, Deck
│   ├── evaluation.py     # HandRank, evaluate(hand, board), compare_hands()
│   ├── equity.py         # EquityCalculator, MonteCarloSimulator
│   ├── ranges.py         # Range, Combo, parse_range()
│   └── game.py           # Action, Street, Position, GameState
```

**Key Types:**

| Type | Description |
|------|-------------|
| `Card` | A single card (rank + suit), immutable, comparable |
| `Rank` | Enum: TWO through ACE |
| `Suit` | Enum: CLUBS, DIAMONDS, HEARTS, SPADES |
| `HandRank` | Enum: HIGH_CARD through ROYAL_FLUSH |
| `HandEvaluation` | NamedTuple: rank + kickers + cards_used |
| `Position` | Enum: EP, MP, CO, BTN, SB, BB (6-max and 9-max variants) |
| `Action` | Immutable: player, action_type, amount, street |
| `Street` | Enum: PREFLOP, FLOP, TURN, RIVER |

**Design Decisions:**
- All public functions are pure — no side effects, no I/O
- Hand evaluation uses a lookup-table approach for speed (precomputed rank tables)
- Monte Carlo simulator accepts a `random.Random` instance for deterministic testing
- Ranges use a 169-combo representation (13×13 matrix)

### 2.2 Backend (`backend/`)

The backend follows a **layered architecture** with strict dependency direction:

```
api/ ──────► services/ ──────► repositories/ ──────► models/ ──────► database
  │              │                   │
  └──────────────┼───────────────────┘
                 │
          poker-engine/        (pure library, no database access)
```

**Layer Responsibilities:**

| Layer | Responsibility | Must NOT |
|-------|---------------|----------|
| `api/` | HTTP concerns: routing, request parsing, response formatting, status codes | Contain business logic; access database directly |
| `services/` | Business logic, orchestration, validation | Access HTTP concerns; return HTTP-specific types |
| `repositories/` | Data access: queries, inserts, updates, transactions | Contain business rules; call external services |
| `models/` | ORM models (SQLAlchemy), Pydantic schemas | Contain logic beyond basic validation |

### 2.3 Importer Architecture — Pluggable Parsers

The hand history import system uses a **strategy pattern** to support multiple poker site formats. Adding a new site format requires implementing a single parser class — no changes to the database schema, API, or frontend.

```
backend/src/importers/
├── __init__.py
├── base.py              # AbstractParser — defines the interface
├── registry.py          # PARSER_REGISTRY — maps site name → parser class
├── pokerstars.py        # PokerStarsParser
├── ggpoker.py           # GGPokerParser
├── ignition.py          # IgnitionParser
├── winamax.py           # WinamaxParser        (post-MVP)
├── partypoker.py        # PartyPokerParser     (post-MVP)
└── ipoker.py            # IPokerParser         (post-MVP)
```

**AbstractParser Interface:**

```python
class AbstractParser(ABC):
    @property
    @abstractmethod
    def site_name(self) -> str: ...

    @abstractmethod
    def detect_format(self, raw_text: str) -> bool: ...

    @abstractmethod
    def parse_hand(self, raw_text: str) -> ParsedHand: ...

    @abstractmethod
    def parse_file(self, file_path: str) -> Iterator[ParsedHand]: ...
```

**ParsedHand** is a canonical intermediate representation — all parsers produce the same structure regardless of source format:

```python
@dataclass
class ParsedHand:
    hand_number: str
    site: str
    table_name: str
    stake_sb: float
    stake_bb: float
    game_type: str
    max_players: int
    played_at: datetime
    board: BoardCards
    players: list[ParsedPlayer]
    actions: list[ParsedAction]
    total_pot: float
    rake: float
    raw_text: str
```

**Adding a new site format:**

1. Create a new file in `backend/src/importers/` (e.g., `winamax.py`)
2. Implement `AbstractParser` for the new format
3. Register it in `registry.py`
4. No other code changes required — API, frontend, analytics all work automatically

**Supported formats roadmap:**

| Format | Status | Notes |
|--------|--------|-------|
| PokerStars | MVP | Most common format; includes Zoom |
| GGPoker | MVP | Growing market share |
| Ignition/Bovada | MVP | Anonymous tables require special handling |
| Winamax | Post-MVP | French market leader |
| PartyPoker | Post-MVP | Legacy and modern formats |
| iPoker | Post-MVP | Network used by many skins |

### 2.4 Frontend (`frontend/`)

The frontend follows a **feature-based architecture**:

```
frontend/src/
├── features/
│   ├── dashboard/
│   │   ├── components/     # Dashboard-specific components
│   │   ├── hooks/          # Dashboard-specific hooks
│   │   ├── types.ts        # Dashboard-specific types
│   │   ├── api.ts          # Dashboard API calls
│   │   └── index.ts        # Public exports
│   ├── hand-explorer/
│   ├── player-analysis/
│   ├── ai-assistant/
│   ├── import/
│   └── session-tracker/
├── shared/
│   ├── components/         # Reusable UI components
│   │   ├── DataTable/
│   │   ├── Chart/
│   │   ├── StatCard/
│   │   └── PokerTable/     # Visual poker table component
│   ├── hooks/              # Reusable hooks
│   ├── types/              # Shared TypeScript types
│   ├── utils/              # Pure utility functions
│   └── api/                # API client setup
├── stores/                 # Zustand stores
│   ├── useAppStore.ts      # Global app state
│   ├── useImportStore.ts   # Import state
│   └── useFilterStore.ts   # Global filter state
├── App.tsx
└── main.tsx
```

---

## 3. Data Flow

### 3.1 Hand Import Flow

```
User selects files
       │
       ▼
┌─────────────────┐
│  Frontend        │  POST /api/import/upload  (multipart file)
│  Import Feature  │──────────────────────────────────────┐
└─────────────────┘                                      │
       ▲                                                 ▼
       │                                   ┌─────────────────────────┐
       │  SSE: import progress             │  API Layer              │
       │  (hands_processed, errors)        │  /api/import/upload     │
       │                                   └───────────┬─────────────┘
       │                                               │
       │                                               ▼
       │                                   ┌─────────────────────────┐
       │                                   │  Import Service         │
       │                                   │  - Detect format        │
       │                                   │  - Parse hands          │
       │                                   │  - Validate duplicates  │
       │                                   │  - Emit progress events │
       │                                   └───────────┬─────────────┘
       │                                               │
       │                                               ▼
       │                                   ┌─────────────────────────┐
       │                                   │  Repository Layer       │
       │                                   │  - Insert hands         │
       │                                   │  - Insert actions       │
       │                                   │  - Insert players       │
       │                                   │  - COMMIT transaction   │
       │                                   └───────────┬─────────────┘
       │                                               │
       │                                               ▼
       │                                   ┌─────────────────────────┐
       │                                   │  SQLite                 │
       │                                   │  hands, actions,        │
       │                                   │  players, sessions      │
       │                                   └─────────────────────────┘
```

### 3.2 Analytics Query Flow

```
┌──────────────────┐
│ Dashboard Page    │  GET /api/analytics/summary?date_from=...&stake=...
│ (loads on mount)  │────────────────────────────────────────────┐
└──────────────────┘                                            │
       ▲                                                        ▼
       │                                          ┌─────────────────────────┐
       │  JSON response                           │  Analytics Service       │
       │  { total_hands, net_won, bb_per_100 }    │  - Build SQL query       │
       │                                          │  - Execute via repo      │
       │                                          │  - Format response       │
       │                                          └───────────┬─────────────┘
       │                                                      │
       │                                                      ▼
       │                                          ┌─────────────────────────┐
       │                                          │  Repository              │
       │                                          │  raw SQL aggregation     │
       │                                          └───────────┬─────────────┘
       │                                                      │
       │                                                      ▼
       │                                          ┌─────────────────────────┐
       │                                          │  SQLite                 │
       │                                          │  SELECT SUM, COUNT,     │
       │                                          │  GROUP BY               │
       │                                          └─────────────────────────┘
```

### 3.3 AI Assistant Flow

```
┌──────────────────┐
│ AI Assistant UI   │  POST /api/ai/query  { question: "What's my VPIP..." }
│ (chat interface)  │────────────────────────────────────────────────────┐
└──────────────────┘                                                    │
       ▲                                                                ▼
       │                                                  ┌─────────────────────────┐
       │  { answer, data, sql_used }                       │  AI Service              │
       │                                                  │  1. Parse user question  │
       │                                                  │  2. Generate SQL query   │
       │                                                  │  3. Execute via repo     │
       │                                                  │  4. Format natural       │
       │                                                  │     language answer      │
       │                                                  └───────────┬─────────────┘
       │                                                              │
       │                                                              ▼
       │                                                  ┌─────────────────────────┐
       │                                                  │  Anthropic API           │
       │                                                  │  (cloud — only external  │
       │                                                  │   dependency)            │
       │                                                  └─────────────────────────┘
```

---

## 4. Technology Choices & Rationale

### 4.1 Frontend

| Choice | Rationale | Alternatives Considered |
|--------|-----------|------------------------|
| **React 18** | Mature ecosystem, large talent pool, excellent for data-heavy SPAs | Svelte (smaller ecosystem), Vue (less typing support) |
| **TypeScript** | Type safety across the stack; critical for complex poker data structures | JavaScript (rejected — too error-prone for poker math) |
| **Vite** | Fast dev server, excellent TypeScript support, simple configuration | Webpack (complex), esbuild (less feature-rich) |
| **Zustand** | Minimal boilerplate, TypeScript-first, no providers needed | Redux Toolkit (heavier), Jotai (less proven), Context (perf issues) |
| **TanStack Table** | Headless table with sorting, filtering, pagination built-in | AG Grid (too heavy), custom (reinventing wheel) |
| **Recharts** | React-native charting, good customization, active maintenance | D3 (too low-level), Chart.js (less React-native), ECharts (heavier) |

### 4.2 Backend

| Choice | Rationale | Alternatives Considered |
|--------|-----------|------------------------|
| **FastAPI** | Native async, automatic OpenAPI docs, Pydantic integration, fast | Flask (no async), Django (too heavy for local app) |
| **SQLAlchemy 2.0** | Mature ORM with excellent SQLite support, migration tooling | Raw SQL (error-prone), Peewee (less features) |
| **Alembic** | De facto migration tool for SQLAlchemy | Custom migrations (unnecessary) |
| **Uvicorn** | Fast ASGI server, pairs perfectly with FastAPI | Gunicorn (WSGI), Hypercorn (less popular) |

### 4.3 Database

| Choice | Rationale | Alternatives Considered |
|--------|-----------|------------------------|
| **SQLite** | Zero configuration, single file, perfect for local-first, excellent read performance | PostgreSQL (requires server), DuckDB (columnar — wrong access pattern) |

### 4.4 Testing

| Choice | Rationale |
|--------|-----------|
| **Pytest** | Standard for Python; fixtures, parametrize, plugins |
| **Vitest** | Vite-native, Jest-compatible, fast |
| **Playwright** | Cross-browser E2E; better reliability than Cypress for complex interactions |

---

## 5. Key Design Decisions

### ADR-001: SQLite for All Data

**Decision:** Use SQLite as the sole database.

**Rationale:**
- Local-first architecture requires no server installation
- Single file simplifies backup, migration, and portability
- SQLite read performance is excellent for single-user workloads
- WAL mode enables concurrent reads during writes
- Eliminates infrastructure dependencies

**Trade-off:** Limited write concurrency. Acceptable because there is exactly one writer (the backend process) and writes are infrequent after initial import.

### ADR-002: Pure Poker Engine

**Decision:** The poker engine is a standalone Python library with zero external dependencies.

**Rationale:**
- Poker logic must be 100% testable without database, HTTP, or UI infrastructure
- Enables exhaustive testing (test every possible 5-card hand = 2.6M combinations)
- Can be reused if the project expands to other interfaces
- Clear boundary: the engine knows nothing about "users", "sessions", or "analytics"

### ADR-003: Derived Statistics

**Decision:** Statistics are computed on-the-fly from raw hand data. They are never pre-computed and stored.

**Rationale:**
- Raw hand data is immutable — it's the single source of truth
- Pre-computed stats can become stale or inconsistent
- SQLite aggregation is fast enough for MVP scale (< 1M hands)
- Caching can be added transparently at the repository or service layer

**Trade-off:** Complex queries may be slower than pre-computed values. Mitigated by: (a) SQLite's excellent aggregation performance, (b) materialized views or cache layer if needed post-MVP.

### ADR-004: Feature-Based Frontend

**Decision:** Frontend code is organized by feature, not by type (components/hooks/utils/etc.).

**Rationale:**
- Features are independently understandable
- Reduces cross-feature coupling
- Makes it obvious where new code belongs
- Each feature can be developed, tested, and even lazy-loaded independently

### ADR-005: Backend as Local Server

**Decision:** The backend runs as a local HTTP server, not an embedded Python process.

**Rationale:**
- Clean separation between frontend and backend
- Backend can be tested independently with HTTP clients
- Enables future split to client-server if needed
- FastAPI + Uvicorn startup time is negligible (< 1 second)
- Frontend dev with Vite proxy is standard and well-supported

**Trade-off:** Slightly more complex startup (two processes in dev). Mitigated by a startup script and single-process production mode.

---

## 6. Security Architecture

### 6.1 Threat Model

The application runs entirely on the user's machine. The primary threats are:

| Threat | Mitigation |
|--------|-----------|
| Malicious hand history files | Input validation, strict parsing, file size limits |
| SQL injection via AI-generated queries | Parameterized queries, read-only AI database user |
| Data loss | Automatic backup on import, export functionality |
| Supply chain attacks | Dependency pinning, SBOM, regular audits |

### 6.2 Data Protection

- No data leaves the user's machine except AI queries (sent to Anthropic API)
- AI queries include only aggregated statistics, not raw hand data
- User can disable AI features entirely
- Database file permissions set to user-only (600)

---

## 7. Performance Architecture

### 7.1 Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| Dashboard load (100k hands) | < 500ms | SQL aggregation, minimal joins |
| Hand import | > 10,000 hands/sec | Bulk inserts, single transaction |
| Hand search | < 200ms | Full-text search index (FTS5) |
| Equity calculation | < 100ms | Lookup tables, efficient algorithms |
| AI response | < 3s | Streaming response, efficient prompt design |

### 7.2 Caching Strategy

- **No cache** in MVP for analytics — SQLite aggregation is the target performance
- If needed: in-memory LRU cache at the service layer for expensive stat computations
- Frontend: TanStack Query provides request-level caching with stale-while-revalidate

---

*Next: [Database Schema](./04-database-schema.md)*
