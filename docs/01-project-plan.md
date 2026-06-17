# Poker Analytics Platform — Project Plan

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## 1. Vision

A desktop-first **Texas Hold'em** analytics application that empowers serious Hold'em players to analyze their hand histories, understand player tendencies, calculate probabilities in real-time, and track long-term performance. The platform combines a rigorous Hold'em poker engine with modern analytics and an AI-powered assistant to surface insights that players would otherwise miss. **This application is exclusively for Texas Hold'em — Omaha and other poker variants are explicitly out of scope for all phases.**

### Elevator Pitch

"Poker Analytics Platform is the bridge between raw Texas Hold'em hand histories and winning poker decisions. Store every hand. Analyze every player. Find every leak. Win more."

---

## 2. Project Scope

### 2.1 In Scope (MVP)

| Area | Description |
|------|-------------|
| Hand History Import | Parse and store **Texas Hold'em only** hand histories from major online platforms. MVP: PokerStars, GGPoker, Ignition/Bovada. Architecture designed to add Winamax, PartyPoker, iPoker, and others with zero schema/API/frontend changes — only a new parser class. |
| Hand History Storage | Full relational storage of every Hold'em hand, action, street, card, and result |
| Poker Engine | **Texas Hold'em only:** hand ranking, equity calculation, outs calculation, Monte Carlo simulation |
| Core Analytics | VPIP, PFR, 3Bet, Fold to 3Bet, CBet, Fold to CBet, Aggression Factor, WTSD, W$SD, bb/100 |
| Player Analysis | Per-player statistics, basic profiling, position-based analysis |
| Dashboard | Session summaries, profit/loss charts, key metric cards |
| Hand Explorer | Browse, filter, search, and replay Hold'em hand histories |
| AI Assistant | Natural language queries over stored data, statistic explanations, basic leak identification |

### 2.2 Out of Scope (All Phases)

- Omaha support (including Omaha Hi/Lo)
- All other non-Hold'em poker variants (Stud, Razz, Draw, mixed games)
- Multi-table tournament ICM calculations
- Real-time HUD overlay
- Cloud sync / multi-device
- Mobile application
- GTO solver integration
- Live hand tracking
- Rakeback / bonus tracking

### 2.3 Future Phases

All future phases remain exclusively Texas Hold'em. Other poker variants are permanently out of scope.

| Phase | Features |
|-------|----------|
| Phase 2 | Tournament tracking (Hold'em MTT), ICM calculations, multi-site session merging |
| Phase 3 | Real-time HUD overlay, live hand import watcher |
| Phase 4 | Cloud sync, mobile companion app |
| Phase 5 | GTO solver integration, advanced range analysis |

---

## 3. Stakeholders & Personas

### 3.1 Primary Personas

**Alex — The Serious Recreational Player**
- Plays 10–20 hours/week online (Texas Hold'em)
- 50,000+ hand database
- Wants to find leaks and improve win rate
- Technical comfort: moderate (comfortable with PokerTracker/HoldemManager)
- Key need: "Where am I losing money?"

**Jordan — The Semi-Professional**
- Plays 30–50 hours/week across multiple sites (Texas Hold'em)
- 500,000+ hand database
- Needs fast search across large datasets
- Uses advanced stats (range vs range, positional heat maps)
- Key need: "Who are the fish at my tables and how do I exploit them?"

**Taylor — The Coach**
- Reviews hands for multiple students (Texas Hold'em)
- Needs to annotate hands and share analysis
- Uses player comparison tools
- Key need: "Show me exactly where my student deviates from optimal"

### 3.2 Secondary Personas

- **The Casual Player** — Plays occasionally, wants basic tracking and a clean dashboard
- **The Data Scientist** — Wants raw data export for custom analysis in Python/R

---

## 4. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hand import accuracy | > 99.9% | Automated reconciliation against known hand histories |
| Hand ranking accuracy | 100% | Exhaustive unit test suite against known poker test vectors |
| Query performance (100k hands) | < 500ms for dashboard load | Instrumented API timing |
| AI assistant response time | < 3 seconds | Measured end-to-end |
| Test coverage (poker engine) | 100% | Line + branch coverage |
| Test coverage (overall) | > 85% | Line coverage |

---

## 5. High-Level Project Structure

```
poker_analyrics_platform/
├── docs/                           # All project documentation
│   ├── 01-project-plan.md
│   ├── 02-mvp-definition.md
│   ├── 03-system-architecture.md
│   ├── 04-database-schema.md
│   ├── 05-frontend-design.md
│   ├── 06-backend-apis.md
│   ├── 07-development-roadmap.md
│   ├── 08-technical-risks.md
│   └── 09-project-blueprint.md
├── poker-engine/                   # Pure Python Texas Hold'em engine (zero deps outside stdlib)
│   ├── src/
│   │   ├── cards/                  # Card, Deck, CardSet
│   │   ├── hands/                  # Hand ranking, comparison
│   │   ├── equity/                 # Equity calculators, Monte Carlo
│   │   ├── ranges/                 # Range representation and combinatorics
│   │   └── game/                   # Game state, actions, rules
│   └── tests/
├── backend/                        # FastAPI application
│   ├── src/
│   │   ├── api/                    # Route handlers (thin layer)
│   │   ├── services/               # Business logic
│   │   ├── repositories/           # Data access layer
│   │   ├── models/                 # Pydantic models & SQLAlchemy ORM
│   │   ├── importers/              # Hand history parsers
│   │   ├── analytics/              # Stat computation engine
│   │   └── ai/                     # AI assistant service
│   └── tests/
├── frontend/                       # React + TypeScript + Vite
│   ├── src/
│   │   ├── features/               # Feature-based modules
│   │   │   ├── dashboard/
│   │   │   ├── hand-explorer/
│   │   │   ├── player-analysis/
│   │   │   ├── session-tracker/
│   │   │   ├── ai-assistant/
│   │   │   └── import/
│   │   ├── shared/                 # Shared components, hooks, utilities
│   │   ├── stores/                 # State management
│   │   └── api/                    # API client layer
│   └── tests/
└── data/                           # SQLite database (gitignored)
```

---

## 6. Key Principles

1. **Poker engine is pure.** It knows nothing about databases, HTTP, or UIs. It takes inputs and returns outputs. 100% testable without infrastructure. The engine implements **Texas Hold'em only** — no Omaha, Stud, or other variants.

2. **Every hand is immutable.** Once stored, a hand record never changes. Corrections create new records. This ensures auditability and reproducible analytics.

3. **Analytics are derived, not stored.** Raw hand data is the source of truth. Statistics are computed on demand with aggressive caching where needed, but the cache is always discardable.

4. **Domain-driven boundaries.** The codebase speaks poker language: `Hand`, `Street`, `Action`, `Position`, `Board`, `Range` — not `HandRecord`, `ActionRow`, or other generic names.

5. **Feature-based frontend.** Each feature folder contains everything that feature needs: components, hooks, types, tests. Shared code lives in `shared/`.

6. **Thin API layer.** Route handlers delegate to services immediately. Services contain all business logic and are independently testable.

---

## 7. Team Structure (Agent Roles)

| Role | Responsibility |
|------|---------------|
| Product Owner | Prioritize features, define user stories, validate MVP scope |
| Senior Lead | Architecture decisions, code review standards, technical direction |
| Poker Domain Expert | Validate Texas Hold'em math, hand ranking correctness, stat definitions |
| Database Architect | Schema design, query optimization, migration strategy |
| Backend Developer | API implementation, service layer, importers, analytics engine |
| Frontend Developer | UI components, state management, data visualization |
| Data Analyst | Stat computation algorithms, trend detection, leak detection rules |
| Security Agent | Input validation, SQL injection prevention, data integrity |
| Test Writer | Test strategy, test data generation, coverage enforcement |
| QA Agent | Integration testing, cross-browser validation, performance testing |
| Documentation Agent | API docs, user guides, developer onboarding |

---

## 8. Constraints

| Constraint | Rationale |
|------------|-----------|
| Local-first | All data stored locally; no server dependency for core functionality |
| SQLite only | Single-file database; no PostgreSQL/MySQL in MVP |
| Desktop browser target | Chrome, Firefox, Edge — no mobile layout in MVP |
| Offline capable | All core features work without internet (AI assistant excepted) |
| Max 100MB memory idle | Application should run on 8GB RAM machines comfortably |
| Import throughput | At least 10,000 hands/second during bulk import |

---

## 9. Communication Plan

- All architecture decisions documented in ADRs (Architecture Decision Records)
- API contracts defined in OpenAPI 3.1 specification
- Database schema versioned with migration files
- Component library documented with Storybook
- Weekly milestone reviews against the 12-week roadmap

---

*Next: [MVP Definition](./02-mvp-definition.md)*
