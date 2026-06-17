# Poker Analytics Platform — 12-Week Development Roadmap

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## Overview: Three Phases of Development

```
Weeks 1-4  ████████████  FOUNDATION
            Poker engine, database, import pipeline

Weeks 5-8  ████████████  CORE FEATURES
            Analytics, dashboard, hand explorer, session tracking

Weeks 9-12 ████████████  ADVANCED + POLISH
            Player analysis, AI assistant, performance, QA
```

---

## Week-by-Week Breakdown

### Week 1: Project Scaffolding & Poker Engine — Cards & Evaluation

**Theme:** Get the foundation right. The poker engine makes or breaks the entire application.

| Day | Deliverables |
|-----|-------------|
| Mon | Project structure, tooling config (Vite, FastAPI, pytest, vitest, CI), monorepo setup |
| Tue | `poker-engine/` package: Card, Rank, Suit, Deck types; 100% tested |
| Wed | Hand evaluation: 5-card hand ranking; exhaustive test suite (all C(52,5) = 2,598,960 hands) |
| Thu | Hand evaluation: 7-card → best 5-card; performance tuning (target: < 1µs per eval) |
| Fri | Game types: Position, Action, Street, enums and value objects; integration test harness |

**Milestone M1:** Poker engine correctly ranks all 2.6M 5-card hands against known reference data.

**Tests written:** ~200+ unit tests covering every rank, suit, edge case, and exhaustive evaluation.

**Dependencies:** None.
**Blocks:** Weeks 2-12 (everything depends on poker engine correctness).

---

### Week 2: Poker Engine — Equity, Ranges & Monte Carlo

**Theme:** Complete the poker math library. Equity calculation is the hardest algorithmic problem in the engine.

| Day | Deliverables |
|-----|-------------|
| Mon | Equity calculator: heads-up preflop exact equity (enumerate all boards) |
| Tue | Equity calculator: heads-up postflop exact equity |
| Wed | Monte Carlo simulator: range vs range, configurable iterations, reproducible seeds |
| Thu | Range representation: 169-combo matrix, range parser ("AKs, JJ+, 87s+") |
| Fri | Outs calculator; documentation and API reference for the poker engine |

**Milestone M2:** Heads-up equity within 0.01% of PokerStove reference values for all matchups.

**Tests written:** ~150+ unit tests with known equity values as assertions.

**Dependencies:** Week 1.
**Blocks:** Hand replay (needs hand evaluation), analytics validation.

---

### Week 3: Database Schema & ORM Layer

**Theme:** Translate the database design into working code with migrations and repositories.

| Day | Deliverables |
|-----|-------------|
| Mon | SQLAlchemy models for all tables (hands, hand_players, actions, players, sessions, import_logs) |
| Tue | Alembic migration chain (8 migrations), migration tests (upgrade + downgrade) |
| Wed | Repository layer: base repository pattern, HandRepository, PlayerRepository |
| Thu | Repository layer: ActionRepository, SessionRepository, ImportLogRepository |
| Fri | Database utilities: connection management, WAL mode, backup, FTS5 setup, performance tuning |

**Milestone M3:** All tables created via migrations; repositories pass CRUD tests with real SQLite.

**Tests written:** ~100+ integration tests for repositories.

**Dependencies:** Week 1 (poker engine types for card validation).
**Blocks:** Week 4 (import needs storage), Week 5 (analytics needs queries).

---

### Week 4: Hand History Import Pipeline

**Theme:** Build the bridge between raw hand history files and the database. Pluggable from day one.

| Day | Deliverables |
|-----|-------------|
| Mon | AbstractParser interface, ParsedHand canonical model, parser registry |
| Tue | PokerStars parser: full hand history parsing (cash game, all actions, all streets) |
| Wed | GGPoker parser: full hand history parsing |
| Thu | Ignition/Bovada parser: full hand history parsing (anonymous player mapping) |
| Fri | Import service: file upload → format detection → parsing → storage → progress events (SSE) |

**Milestone M4:** 10,000+ hands from each supported site imported correctly with zero data loss.

**Tests written:** ~100+ parser tests with real hand history samples, ~50 import service tests.

**Dependencies:** Week 3 (database ready).
**Blocks:** Week 5+ (analytics and UI need data).

---

### Week 5: Core Analytics Engine

**Theme:** Compute every poker statistic from raw hand data. Pure functions, no HTTP.

| Day | Deliverables |
|-----|-------------|
| Mon | Stat calculator: VPIP, PFR, 3Bet, Fold to 3Bet — SQL query + validation |
| Tue | Stat calculator: CBet (flop/turn/river), Fold to CBet (flop/turn/river) |
| Wed | Stat calculator: Aggression Factor, Aggression Frequency, WTSD, W$SD |
| Thu | Stat calculator: bb/100, hourly rate, standard deviation, all-in adjusted EV |
| Fri | Position-based stats; stat computation validation against manually verified hand samples |

**Milestone M5:** All 15+ core statistics computed correctly against a verified 10,000-hand test dataset.

**Tests written:** ~80+ analytics tests with curated hand datasets and known stat values.

**Dependencies:** Week 4 (import data needed for testing).
**Blocks:** Week 6 (API serves analytics), Week 8 (dashboard displays them).

---

### Week 6: Backend API — Core Endpoints

**Theme:** Wire up the service and API layers. Thin routes, thick services.

| Day | Deliverables |
|-----|-------------|
| Mon | FastAPI app setup, middleware (CORS, error handling, logging), API docs (OpenAPI) |
| Tue | Hand endpoints: list, get, actions; Player endpoints: list, get, stats |
| Wed | Analytics endpoints: summary, profit-over-time, stats-by-position, session-stats |
| Thu | Session endpoints: list, get, update, merge, split |
| Fri | Import endpoints: upload, status (SSE), history; Settings endpoints |

**Milestone M6:** All API endpoints documented, tested, and returning correct data against test database.

**Tests written:** ~120+ API integration tests (pytest + httpx TestClient).

**Dependencies:** Week 5 (analytics engine), Week 4 (import), Week 3 (database).
**Blocks:** Week 7+ (frontend needs APIs).

---

### Week 7: Frontend — Foundation & Dashboard

**Theme:** Stand up the React application and build the primary landing page.

| Day | Deliverables |
|-----|-------------|
| Mon | Vite + React + TypeScript setup; routing, layout shell, sidebar navigation |
| Tue | Shared components: StatCard, DataTable, Chart wrapper, CardDisplay, PokerTable |
| Wed | API client layer (TanStack Query setup, typed API functions, error handling) |
| Thu | Dashboard page: stat cards, profit/loss chart, recent sessions table |
| Fri | Dashboard page: position win rate chart, global filter bar, responsive polish |

**Milestone M7:** Dashboard renders with real data from the backend; all charts interactive.

**Tests written:** ~60+ component tests (Vitest + Testing Library), ~10 E2E tests (Playwright).

**Dependencies:** Week 6 (API ready).
**Blocks:** None (parallel with Week 8 frontend work).

---

### Week 8: Frontend — Hand Explorer & Import UI

**Theme:** Hand browsing, searching, and the import experience.

| Day | Deliverables |
|-----|-------------|
| Mon | Hand Explorer: filter bar, hands table with virtualized rows, pagination |
| Tue | Hand Explorer: card search with combo shorthand parsing ("AKs", "JJ+", "72o") |
| Wed | Hand Replay page: poker table visualization, action log, street navigation |
| Thu | Hand Replay page: animated action playback, prev/next navigation |
| Fri | Import page: drag-and-drop zone, file validation, progress bar (SSE), import history |

**Milestone M8:** User can import hands, browse them, filter by any criteria, and replay any hand.

**Tests written:** ~70+ component tests, ~15 E2E tests.

**Dependencies:** Week 7 (frontend foundation).
**Blocks:** None.

---

### Week 9: Frontend — Player Analysis & Sessions

**Theme:** Deep player profiling, comparisons, and session management.

| Day | Deliverables |
|-----|-------------|
| Mon | Player list page: search, sort, filter by site/stats |
| Tue | Player profile page: stat overview, position heatmap, player type badge |
| Wed | Player profile page: leak cards, trend indicators; Player compare view |
| Thu | Session tracker page: session list, session detail, session hands |
| Fri | Session management: edit notes, adjust boundaries, merge/split sessions |

**Milestone M9:** Complete player analysis workflow — find a player, analyze them, identify leaks.

**Tests written:** ~60+ component tests, ~10 E2E tests.

**Dependencies:** Week 7-8 (shared components, API client).
**Blocks:** None.

---

### Week 10: AI Assistant

**Theme:** Natural language interface for querying poker data.

| Day | Deliverables |
|-----|-------------|
| Mon | AI service: prompt engineering, SQL generation from natural language, response formatting |
| Tue | AI service: context injection (active filters, hero stats), safety constraints (read-only SQL) |
| Wed | AI chat UI: chat window, message bubbles, streaming text, data table rendering |
| Thu | AI chat UI: suggested questions, error states, loading states, offline mode |
| Fri | AI integration testing: accuracy validation on 100+ known queries, prompt tuning |

**Milestone M10:** AI correctly answers 90%+ of natural language questions in the test suite.

**Tests written:** ~50+ AI service tests, ~30 UI tests.

**Dependencies:** Week 5 (analytics engine), Week 6 (API).
**Blocks:** None.

---

### Week 11: Performance Optimization & Hardening

**Theme:** Make it fast, make it robust. Hit the performance targets.

| Day | Deliverables |
|-----|-------------|
| Mon | Import performance: batch inserts, transaction tuning, target >10k hands/sec |
| Tue | Query performance: index optimization, query plan analysis, N+1 elimination |
| Wed | Frontend performance: bundle size audit, code splitting, lazy loading, memo optimization |
| Thu | Error handling audit: every error path covered, user-friendly messages, recovery options |
| Fri | Database: VACUUM, backup/restore, integrity checks, corruption recovery |

**Milestone M11:** All performance targets met; import > 10k hands/sec; dashboard < 500ms.

**Tests written:** Performance benchmark suite, stress tests.

**Dependencies:** All prior weeks.
**Blocks:** Week 12 (final QA).

---

### Week 12: Testing, QA & Release Preparation

**Theme:** Final quality pass. Ship a polished MVP.

| Day | Deliverables |
|-----|-------------|
| Mon | End-to-end test suite: all critical user flows automated with Playwright |
| Tue | Cross-browser testing (Chrome, Firefox, Edge); edge case testing (empty DB, 1M+ hands) |
| Wed | Bug fixes from QA; accessibility pass (keyboard navigation, screen reader, color contrast) |
| Thu | Documentation: user guide, developer setup guide, API reference finalization |
| Fri | Release packaging: single-command install, desktop launcher, versioned release |

**Milestone M12:** MVP shipped. All P0 and P1 features complete. Test coverage > 85%.

**Tests written:** ~50+ E2E tests covering all critical user flows.

**Dependencies:** All prior weeks.

---

## Dependency Graph

```
Week 1 (Engine 1) ──► Week 2 (Engine 2) ──► Week 3 (DB) ──► Week 4 (Import)
                                                                 │
                                                                 ▼
                        Week 5 (Analytics) ◄─────────────────────┘
                             │
                             ▼
                        Week 6 (API) ──► Week 7 (Dashboard) ──► Week 8 (Explorer)
                             │                                        │
                             │                                        ▼
                             └──────────────────────────────► Week 9 (Players)
                                                                      │
                                                                      ▼
                        Week 10 (AI) ◄────────────────────────────────┘
                             │
                             ▼
                        Week 11 (Performance) ──► Week 12 (QA/Release)
```

---

## Resource Allocation

| Role | Weeks Active | Primary Focus |
|------|-------------|---------------|
| Senior Lead | 1-12 (full-time) | Architecture oversight, code review, technical decisions |
| Poker Domain Expert | 1-2, 5, 10 (part-time) | Poker engine validation, stat definitions, AI prompt design |
| Backend Developer | 1-6, 10-11 | Poker engine, database, API, AI service |
| Frontend Developer | 7-9, 10-11 | All UI features, AI chat UI |
| Data Analyst | 5, 9-10 | Stat computation, leak detection rules, AI accuracy |
| Test Writer | 1-12 (full-time) | Test strategy, test data generation, automation |
| QA Agent | 11-12 | Integration testing, cross-browser, performance |
| Database Architect | 3-4 | Schema review, query optimization |
| Security Agent | 6, 10-11 | API security, AI safety, data protection |
| Documentation Agent | 12 | User guide, developer docs |

---

## Risk Buffer

Each week has 1 day of buffer built in (5 working days modeled, 4 days of feature work expected). Additionally:

- **Week 11** can absorb Week 6-10 overflow (performance work can be reduced)
- **Week 12** can absorb Week 10-11 overflow (some polish can slip to post-MVP)
- **Critical path risk:** Weeks 1-4 are the tightest; if the poker engine runs behind, everything shifts

---

*Next: [Technical Risks](./08-technical-risks.md)*
