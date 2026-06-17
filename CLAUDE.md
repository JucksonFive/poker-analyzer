# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Poker Analytics Platform — a **desktop-first, local-first** Texas Hold'em analytics application. Players import hand histories, browse/search/replay hands, analyze player tendencies, and get AI-powered insights. All data stored locally in SQLite; the only external dependency is the Anthropic API for the AI assistant.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript 5.4+ (strict), Vite 5.x |
| State | Zustand 4.x (client), TanStack Query 5.x (server cache) |
| UI | Tailwind CSS 3.x, Radix UI, Recharts 2.x, TanStack Table 8.x |
| Backend | FastAPI + Python, Uvicorn, SQLAlchemy 2.0, Alembic |
| Database | SQLite (WAL mode, single file at `data/poker.db`) |
| Testing | Pytest (Python), Vitest + Testing Library (React), Playwright (E2E) |
| Linting | Ruff (Python), Prettier + ESLint (TypeScript) |

## Architecture (5 Key ADRs)

**ADR-001: SQLite for all data** — local-first, zero-config, single file. WAL mode for concurrent reads during writes.

**ADR-002: Pure poker engine** — standalone Python library (`poker-engine/`) with zero external dependencies. No database, HTTP, or I/O. 100% testable in isolation.

**ADR-003: Derived statistics** — stats are always computed on-the-fly from raw hand data. Never pre-computed and stored. Cache is optional and always discardable.

**ADR-004: Feature-based frontend** — `frontend/src/features/<name>/` contains all components, hooks, types, and tests for that feature. Shared code in `shared/`.

**ADR-005: Backend as local server** — FastAPI runs on `localhost:8000`. Dev: Vite proxies to it. Production: FastAPI serves built frontend static files directly (single process).

## Layer Discipline

```
API routes (thin — no business logic, no direct DB)
  → Services (all business logic, orchestration)
    → Repositories (data access only, no business rules)
      → SQLAlchemy ORM models → SQLite
```

- Services return domain objects, never ORM objects
- Repositories return ORM objects, accept domain filters
- The poker engine is a pure library imported by backend services; it knows nothing about the app

## Pluggable Import Architecture

Adding a new poker site format requires **only** a new parser class implementing `AbstractParser` in `backend/src/importers/` plus a registry entry. Zero changes to database schema, API, or frontend. The canonical `ParsedHand` intermediate representation is site-agnostic.

## Database (6 tables + FTS5)

`sessions`, `players` (unique on name+site), `hands` (unique on hand_number+site), `hand_players`, `actions`, `import_logs`. All cards stored as 2-char strings: rank (`2`–`9`,`T`,`J`,`Q`,`K`,`A`) + suit (`c`,`d`,`h`,`s`). e.g. `Ah`, `Td`.

## Design Documents (`docs/`)

All planning/design documents live in `docs/`. The 9 core documents (01–09) plus `agent-prompts.md`:

| Doc | Contents |
|-----|----------|
| `01-project-plan.md` | Vision, scope, personas, constraints, success metrics |
| `02-mvp-definition.md` | 32 user stories (8 features), acceptance criteria, dependency map |
| `03-system-architecture.md` | Architecture diagrams, data flows, ADRs, tech choices |
| `04-database-schema.md` | Full DDL, indexes, example analytics queries, card format |
| `05-frontend-design.md` | All 9 page designs, component specs, state stores, UI principles |
| `06-backend-apis.md` | All 17+ endpoints with request/response schemas, error codes |
| `07-development-roadmap.md` | 12-week schedule with milestones M1–M12 and dependencies |
| `08-technical-risks.md` | Risk matrix (15 risks scored), mitigations, contingencies |
| `09-project-blueprint.md` | Executive summary — the best entry point for understanding the project |

**Reading order for newcomers:** Start with `09-project-blueprint.md`, then `03-system-architecture.md`.

## Current State

This project is in **pre-implementation planning**. No application code exists yet. All design documents are finalized (v1.0, dated 2026-06-16). The 12-week build begins with Week 1: project scaffolding + poker engine (cards + hand evaluation).

## Implementation Order (Critical Path)

Weeks 1-2 (poker engine) are the critical path — every other module depends on the engine being correct. Build order:
1. Poker engine — cards, hand evaluation, equity, ranges
2. Database — ORM models, migrations, repositories
3. Import pipeline — 3 format parsers (PokerStars, GGPoker, Ignition)
4. Analytics engine — all 15+ stats
5. Backend API — all endpoints
6. Frontend — dashboard, hand explorer, player analysis, AI assistant
7. Performance optimization, QA, release

## Code Quality Standards

- **Python:** Type hints on all public functions. Pydantic for cross-layer data. Ruff formatting. All async DB operations.
- **TypeScript:** Strict mode, no `any`. Feature modules export via `index.ts`. Zustand stores fully typed.
- **General:** No commented-out code. Named constants (no magic numbers). Functions ≤ ~30 lines. Consistent poker terminology across the entire codebase.
