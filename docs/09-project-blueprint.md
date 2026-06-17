# Poker Analytics Platform — Project Blueprint

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Final Draft
**Next Review:** At implementation start

---

## Executive Summary

The Poker Analytics Platform is a **desktop-first, local-first** application for serious Texas Hold'em players to import, store, analyze, and learn from their hand histories. It combines a rigorously-tested poker engine with modern analytics and an AI-powered query assistant.

**Technology:** React + TypeScript (Vite) frontend, FastAPI + Python backend, SQLite database. Single binary / single command startup in production.

**Timeline:** 12 weeks to MVP.
**MVP Scope:** Hand import (3 formats), poker engine, 15+ core stats, dashboard, hand explorer, player analysis, session tracking, AI assistant.

---

## 1. Architecture at a Glance

```
Browser ──HTTP──► FastAPI (backend) ──SQL──► SQLite (database)
                      │
                      ├──► Importers (pluggable parsers per poker site)
                      ├──► Analytics Engine (pure stat computations)
                      ├──► Poker Engine (pure Python, zero deps)
                      └──► AI Service (natural language → SQL)
```

**Key Architectural Decisions:**
1. Poker engine is a pure library — no database, no HTTP, no I/O
2. All statistics are computed on-the-fly from raw hand data
3. Database schema is site-agnostic — new sites add parsers, never schema changes
4. Frontend is feature-based — each feature self-contained with components/hooks/types
5. Backend layers strictly: API → Services → Repositories → Models → Database

---

## 2. Directory Structure

```
poker_analyrics_platform/
├── docs/                               # All planning & design documents
│   ├── 01-project-plan.md
│   ├── 02-mvp-definition.md
│   ├── 03-system-architecture.md
│   ├── 04-database-schema.md
│   ├── 05-frontend-design.md
│   ├── 06-backend-apis.md
│   ├── 07-development-roadmap.md
│   ├── 08-technical-risks.md
│   └── 09-project-blueprint.md         # ← You are here
│
├── poker-engine/                       # Pure Python poker library
│   ├── src/
│   │   ├── cards.py                    # Card, Rank, Suit, Deck
│   │   ├── evaluation.py              # Hand ranking (5-card + 7-card)
│   │   ├── equity.py                   # Exact + Monte Carlo equity
│   │   ├── ranges.py                   # Range representation
│   │   └── game.py                     # Position, Action, Street
│   └── tests/
│
├── backend/                            # FastAPI application
│   ├── src/
│   │   ├── api/                        # Route handlers (thin)
│   │   │   ├── hands.py
│   │   │   ├── players.py
│   │   │   ├── analytics.py
│   │   │   ├── sessions.py
│   │   │   ├── import_routes.py
│   │   │   ├── ai.py
│   │   │   └── settings.py
│   │   ├── services/                   # Business logic
│   │   │   ├── hand_service.py
│   │   │   ├── player_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── session_service.py
│   │   │   ├── import_service.py
│   │   │   └── ai_service.py
│   │   ├── repositories/               # Data access
│   │   │   ├── base.py
│   │   │   ├── hand_repository.py
│   │   │   ├── player_repository.py
│   │   │   ├── action_repository.py
│   │   │   ├── session_repository.py
│   │   │   └── import_log_repository.py
│   │   ├── models/                     # SQLAlchemy ORM + Pydantic schemas
│   │   │   ├── orm/
│   │   │   │   ├── hand.py
│   │   │   │   ├── player.py
│   │   │   │   ├── action.py
│   │   │   │   └── session.py
│   │   │   └── schemas/
│   │   │       ├── hand.py
│   │   │       ├── player.py
│   │   │       ├── analytics.py
│   │   │       └── common.py
│   │   ├── importers/                  # Pluggable hand history parsers
│   │   │   ├── base.py                 # AbstractParser
│   │   │   ├── registry.py             # Parser registry
│   │   │   ├── pokerstars.py
│   │   │   ├── ggpoker.py
│   │   │   └── ignition.py
│   │   ├── analytics/                  # Stat computation
│   │   │   ├── core_stats.py
│   │   │   ├── position_stats.py
│   │   │   └── leak_detection.py
│   │   ├── ai/
│   │   │   ├── query_engine.py
│   │   │   ├── prompt_templates.py
│   │   │   └── sql_validator.py
│   │   ├── database.py                 # Connection, session, WAL config
│   │   └── main.py                     # FastAPI app factory
│   ├── migrations/                     # Alembic migrations
│   └── tests/
│
├── frontend/                           # React + TypeScript + Vite
│   ├── src/
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   ├── hand-explorer/
│   │   │   ├── player-analysis/
│   │   │   ├── ai-assistant/
│   │   │   ├── import/
│   │   │   └── session-tracker/
│   │   ├── shared/
│   │   │   ├── components/             # DataTable, Chart, StatCard, PokerTable, etc.
│   │   │   ├── hooks/
│   │   │   ├── types/
│   │   │   ├── utils/
│   │   │   └── api/                    # API client
│   │   ├── stores/                     # Zustand stores
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── tests/
│
└── data/                               # SQLite database (gitignored)
    └── poker.db
```

---

## 3. Database Core

Six primary tables, one virtual FTS5 table:

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `sessions` | Continuous play periods | start_time, end_time, stake, net_result |
| `players` | Player identities | name, site (unique together) |
| `hands` | Individual poker hands | hand_number, board cards, pot, hero_net_won |
| `hand_players` | Player participation in hand | position, hole cards, amount_won |
| `actions` | Every action by every player | street, action_type, amount, seq_number |
| `import_logs` | Import operation audit | filename, hash, counts, status |

**Card format:** 2-character strings (`Ah`, `Kd`, `Ts`, `2c`) — canonical throughout the system.

---

## 4. API Surface (17 Endpoints)

| Module | Endpoints | Purpose |
|--------|-----------|---------|
| Import | `POST /upload`, `GET /status/{id}`, `GET /history` | File upload with SSE progress |
| Hands | `GET /`, `GET /{id}`, `GET /{id}/actions` | Browse, filter, detail, replay |
| Players | `GET /`, `GET /{id}`, `GET /{id}/stats`, `GET /{id}/stats-by-position`, `GET /{id}/leaks` | Player search and deep analysis |
| Sessions | `GET /`, `GET /{id}`, `GET /{id}/hands`, `PATCH /{id}`, `POST /merge`, `POST /split` | Session management |
| Analytics | `GET /summary`, `GET /profit-over-time`, `GET /stats-by-position`, `GET /session-stats` | Dashboard data |
| AI | `POST /query`, `GET /suggestions` | Natural language queries |
| Settings | `GET /`, `PUT /` | Application configuration |

---

## 5. Frontend Pages (9 Routes)

| Route | Page | Priority |
|-------|------|----------|
| `/` | Dashboard — summary cards, P/L chart, recent sessions | P0 |
| `/import` | Hand History Import — drag-drop upload, progress, history | P0 |
| `/hands` | Hand Explorer — filterable, searchable hands table | P0 |
| `/hands/:id` | Hand Replay — visual poker table, action log | P0 |
| `/players` | Player List — search, browse all tracked players | P1 |
| `/players/:id` | Player Profile — stats, position heatmap, leaks | P1 |
| `/players/compare` | Player Comparison — side-by-side stats | P1 |
| `/sessions` | Session Tracker — session list and management | P1 |
| `/ai-assistant` | AI Assistant — chat interface for data queries | P1 |

---

## 6. Poker Engine API (Public Surface)

```python
# cards.py
class Card: ...
class Deck: ...
def card_from_str(s: str) -> Card: ...
def card_to_str(c: Card) -> str: ...

# evaluation.py
class HandRank(Enum): HIGH_CARD, PAIR, TWO_PAIR, TRIPS, STRAIGHT,
                       FLUSH, FULL_HOUSE, QUADS, STRAIGHT_FLUSH, ROYAL_FLUSH
class HandEvaluation(NamedTuple): rank, kickers, cards_used
def evaluate_5(hand: list[Card]) -> HandEvaluation: ...
def evaluate_7(cards: list[Card]) -> HandEvaluation: ...
def compare_hands(h1: HandEvaluation, h2: HandEvaluation) -> int: ...

# equity.py
def exact_equity(hand1: list[Card], hand2: list[Card], board: list[Card]) -> tuple[float, float, float]: ...
def monte_carlo_equity(hand1: list[Card], hand2: list[Card],
                        board: list[Card], iterations: int, seed: int) -> tuple[float, float, float]: ...
def range_vs_range_equity(range1: Range, range2: Range,
                           board: list[Card], iterations: int) -> tuple[float, float]: ...

# ranges.py
class Range: ...
def parse_range(s: str) -> Range: ...  # "AKs, JJ+, 87s+"
def range_to_combos(r: Range) -> list[tuple[Card, Card]]: ...

# game.py
class Position(Enum): ...
class Street(Enum): PREFLOP, FLOP, TURN, RIVER
class ActionType(Enum): FOLD, CHECK, CALL, BET, RAISE, POST_SB, POST_BB, POST_ANTE
```

---

## 7. Development Sequence

```
Foundation (Weeks 1-4)
├── W1: Poker engine — cards + hand evaluation
├── W2: Poker engine — equity + ranges + Monte Carlo
├── W3: Database schema + ORM + migrations + repositories
└── W4: Import pipeline — 3 format parsers + SSE progress

Core (Weeks 5-8)
├── W5: Analytics engine — all 15+ stats
├── W6: Backend API — all endpoints + tests
├── W7: Frontend — dashboard + shared components
└── W8: Frontend — hand explorer + import UI + replay

Advanced + Polish (Weeks 9-12)
├── W9:  Frontend — player analysis + sessions
├── W10: AI assistant — query engine + chat UI
├── W11: Performance optimization + hardening
└── W12: Testing QA + release packaging
```

---

## 8. Critical Path

```
Poker Engine (W1-2) → Database (W3) → Import (W4) → Analytics (W5) → API (W6)
                                                                          │
                                                    Frontend (W7-9) ◄────┘
                                                          │
                                                    AI (W10) → Perf (W11) → Release (W12)
```

**If the poker engine is delayed, everything is delayed.** Week 1-2 are the most critical.

---

## 9. Top 5 Technical Risks

1. **AI generates incorrect SQL** (Score 16) — Mitigated by read-only DB, SQL validation, transparency
2. **Scope creep delays MVP** (Score 16) — Mitigated by strict MVP definition, no new features after Week 8
3. **Hand evaluation bugs** (Score 15) — Mitigated by exhaustive testing against known reference
4. **SQLite performance at scale** (Score 12) — Mitigated by aggressive indexing, WAL mode, benchmarks
5. **Hand history format variations** (Score 12) — Mitigated by lenient parsing, format auto-detection

---

## 10. Testing Strategy

| Layer | Tool | Coverage Target | Strategy |
|-------|------|-----------------|----------|
| Poker engine | pytest | 100% (line + branch) | Exhaustive enumeration + property-based |
| Services | pytest | > 90% | Unit tests with mocked repositories |
| Repositories | pytest | > 90% | Integration tests against real SQLite |
| API endpoints | pytest + httpx | > 90% | Integration tests with TestClient |
| Frontend components | Vitest + Testing Library | > 85% | Component tests with mocked API |
| Frontend E2E | Playwright | Critical paths | Full user flows against running app |
| Performance | Custom benchmark | Import + query targets | Weekly benchmark runs in CI |

---

## 11. Code Quality Standards

### 11.1 Python (Backend + Poker Engine)

- Type hints on all public functions
- Pydantic for all data models crossing layer boundaries
- Services return domain objects, never ORM objects
- Repositories return ORM objects, accept domain filters
- All async database operations
- Ruff for linting + formatting

### 11.2 TypeScript (Frontend)

- Strict mode enabled
- No `any` types (eslint rule)
- Feature modules have explicit public API via `index.ts`
- Zustand stores typed with full TypeScript inference
- TanStack Query keys typed as const tuples
- Prettier + ESLint for code style

### 11.3 General

- No commented-out code merged to main
- No magic numbers — named constants
- Descriptive variable names (no single-letter except loop indices)
- Functions do one thing (max ~30 lines)
- Poker terms used consistently across the entire codebase

---

## 12. Definition of Done

A feature is **done** when:
1. Code is written and self-reviewed
2. Unit tests pass (> target coverage for the layer)
3. Integration tests pass (where applicable)
4. E2E tests pass (for user-facing features)
5. No linting errors or warnings
6. Code reviewed by at least one other developer
7. Documentation updated (API docs, user-facing strings)
8. Feature flag removed (if used during development)

The MVP is **done** when:
1. All 32 MVP user stories pass acceptance criteria
2. A fresh install can import 100,000+ hands without errors
3. All performance targets are met
4. Test coverage > 85% overall, 100% for poker engine
5. Cross-browser testing passes (Chrome, Firefox, Edge)
6. User documentation is complete

---

## 13. Post-MVP Roadmap

| Priority | Feature | Rationale |
|----------|---------|-----------|
| 1 | Winamax parser | French market coverage |
| 2 | PartyPoker parser | Large player base |
| 3 | iPoker parser | Network with many skins |
| 4 | Tournament support | Different game format, high demand |
| 5 | Omaha support | Growing variant |
| 6 | Hand annotation & sharing | Coaching use case |
| 7 | Advanced leak detection | Deeper analysis |
| 8 | Real-time HUD | In-game decision support |
| 9 | Cloud sync | Multi-device access |
| 10 | GTO solver integration | Advanced study |

---

## 14. Key Documents Index

| Document | Purpose |
|----------|---------|
| [01-project-plan.md](./01-project-plan.md) | Vision, scope, stakeholders, success metrics |
| [02-mvp-definition.md](./02-mvp-definition.md) | Feature list, user stories, acceptance criteria |
| [03-system-architecture.md](./03-system-architecture.md) | Architecture, data flow, technology choices, ADRs |
| [04-database-schema.md](./04-database-schema.md) | Tables, indexes, queries, migration strategy |
| [05-frontend-design.md](./05-frontend-design.md) | Pages, components, state management, UI principles |
| [06-backend-apis.md](./06-backend-apis.md) | Endpoints, request/response schemas, service interfaces |
| [07-development-roadmap.md](./07-development-roadmap.md) | 12-week schedule, milestones, dependencies |
| [08-technical-risks.md](./08-technical-risks.md) | Risk catalog, scores, mitigations |

---

*End of Project Blueprint. Ready for implementation.*
