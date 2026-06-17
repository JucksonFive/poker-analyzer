# Poker Analytics Platform — Technical Risks

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## Risk Matrix

Each risk is evaluated on:
- **Probability (P):** 1 (low) to 5 (high)
- **Impact (I):** 1 (low) to 5 (critical)
- **Risk Score:** P × I

---

## 1. Poker Engine Risks

### R1: Incorrect Hand Evaluation

| Attribute | Value |
|-----------|-------|
| **Probability** | 3 |
| **Impact** | 5 |
| **Score** | 15 (CRITICAL) |
| **Description** | Hand ranking produces wrong results for edge cases (e.g., wheel straights, Ace-low straights, kicker comparisons, full house tie-breakers). Could silently corrupt all downstream analytics. |

**Mitigation:**
- Exhaustive 5-card evaluation testing against known reference (2.6M hands)
- Compare 7-card evaluation results against multiple independent implementations
- Property-based testing: random hands must produce consistent rankings
- Fuzz testing with millions of random 7-card combinations

**Detection:** Continuous integration runs exhaustive test suite on every commit.

**Contingency:** Fall back to a well-tested open-source hand evaluator (e.g., `treys`, `pokerlib`) while fixing.

---

### R2: Monte Carlo Simulation Inaccuracy

| Attribute | Value |
|-----------|-------|
| **Probability** | 2 |
| **Impact** | 3 |
| **Score** | 6 (MEDIUM) |
| **Description** | Monte Carlo results diverge from exact equity by more than acceptable margin, or convergence is too slow for practical use. |

**Mitigation:**
- Validate MC results against exact enumeration for heads-up preflop
- Use deterministic seeding for reproducibility
- Implement convergence detection (stop when variance drops below threshold)
- Document confidence intervals in the UI

**Detection:** Automated tests comparing MC results to exact calculations at various iteration counts.

---

### R3: Card Representation Ambiguity

| Attribute | Value |
|-----------|-------|
| **Probability** | 2 |
| **Impact** | 4 |
| **Score** | 8 (HIGH) |
| **Description** | Different sites represent cards differently. Unicode suits, mixed case, abbreviated notations cause parsing errors or incorrect comparisons. |

**Mitigation:**
- Canonical 2-character card format used throughout the system
- All inputs normalized at the parser boundary
- Validation reject invalid card representations early
- Suite of malformed hand history tests

---

## 2. Database Risks

### R4: SQLite Performance at Scale

| Attribute | Value |
|-----------|-------|
| **Probability** | 3 |
| **Impact** | 4 |
| **Score** | 12 (HIGH) |
| **Description** | SQLite degrades with very large datasets (1M+ hands). Dashboard queries exceed 500ms target. FTS5 search becomes slow. |

**Mitigation:**
- WAL mode enables concurrent reads
- Aggressive indexing strategy with covering indexes
- Denormalized summary columns on `hands` and `sessions` tables
- Performance tested from day one with synthetic datasets (100k, 500k, 1M hands)
- Query plan analysis (`EXPLAIN QUERY PLAN`) for all analytics queries
- Materialized views with manual refresh as fallback (post-MVP if needed)

**Detection:** Performance benchmarks in CI with large test datasets.

**Contingency:** Implement caching layer for expensive analytics queries. Add a "compact database" option.

---

### R5: Database Corruption

| Attribute | Value |
|-----------|-------|
| **Probability** | 2 |
| **Impact** | 5 |
| **Score** | 10 (HIGH) |
| **Description** | Application crash, system power loss, or disk error corrupts the SQLite file. All stored hand data is lost. |

**Mitigation:**
- WAL mode is crash-safe by design
- Automatic `PRAGMA integrity_check` on startup
- Automatic backup created before each import operation
- Manual backup/restore functionality exposed in settings
- Database stored in user's home directory (not temp)

**Detection:** Integrity check at startup; user notification if corruption detected.

**Contingency:** Restore from automatic backup. Export all data to JSON as last resort.

---

### R6: Migration Failures

| Attribute | Value |
|-----------|-------|
| **Probability** | 2 |
| **Impact** | 4 |
| **Score** | 8 (HIGH) |
| **Description** | Alembic migration fails in production, leaving database in inconsistent state. User cannot start the application. |

**Mitigation:**
- Every migration tested with upgrade AND downgrade in CI
- Migrations tested against snapshots of real user databases
- Database backup automatically created before migrations run
- Application refuses to start if migration fails (explicit error message)

---

## 3. Import & Parsing Risks

### R7: Hand History Format Variations

| Attribute | Value |
|-----------|-------|
| **Probability** | 4 |
| **Impact** | 3 |
| **Score** | 12 (HIGH) |
| **Description** | Poker sites change hand history formats without notice. Edge cases (split pots, all-in situations, disconnected players, time banks) cause parse failures. Regional differences in formatting exist. |

**Mitigation:**
- Robust, lenient parsing — skip unrecognized lines, don't fail
- Detailed error reporting with hand number and line number
- Format auto-detection with fallback chain
- Test suite with real hand histories from each site (including edge cases)
- Error-tolerant: hands that fail to parse are skipped with logging, not crashing
- Anonymous table support built into parser architecture

**Detection:** Parse success rate tracked per import; drops below 99% trigger investigation.

**Contingency:** User can manually tag format. Community-contributed parser updates (future).

---

### R8: Duplicate Hand Detection Failure

| Attribute | Value |
|-----------|-------|
| **Probability** | 3 |
| **Impact** | 3 |
| **Score** | 9 (HIGH) |
| **Description** | Duplicate hands are imported, skewing all statistics. A player's VPIP is inflated because the same hand is counted twice. |

**Mitigation:**
- `UNIQUE(hand_number, site)` constraint at database level
- File-level SHA-256 hash to detect re-imports of the same file
- Import history shows skipped duplicate count prominently
- "Import again" always safe — duplicates silently skipped

**Detection:** Skipped count monitored; anomalously low skip rate for known re-imports flagged.

---

## 4. Frontend Risks

### R9: Performance with Large Datasets

| Attribute | Value |
|-----------|-------|
| **Probability** | 3 |
| **Impact** | 3 |
| **Score** | 9 (HIGH) |
| **Description** | Hand explorer table rendering 500,000+ rows causes browser lag. Charts rendering thousands of data points freeze the UI. |

**Mitigation:**
- Virtual scrolling for large tables (TanStack Virtual or react-window)
- Server-side pagination — frontend never loads all hands at once
- Chart data aggregation at the API level (not client-side)
- Debounced filter inputs
- Progressive loading for hand replay (load actions on demand)

**Detection:** Performance profiling with React DevTools; Lighthouse audits.

---

### R10: Browser Compatibility

| Attribute | Value |
|-----------|-------|
| **Probability** | 2 |
| **Impact** | 2 |
| **Score** | 4 (LOW) |
| **Description** | Visual inconsistencies across Chrome, Firefox, Edge. CSS Grid/Flexbox bugs in older browsers. |

**Mitigation:**
- Target modern browsers only (last 2 versions)
- CSS reset/normalize
- Cross-browser E2E tests with Playwright
- Feature detection before using cutting-edge APIs

---

## 5. AI Assistant Risks

### R11: Incorrect SQL Generation

| Attribute | Value |
|-----------|-------|
| **Probability** | 4 |
| **Impact** | 4 |
| **Score** | 16 (CRITICAL) |
| **Description** | AI generates SQL that returns wrong results, misleads user about their statistics. User makes strategy decisions based on incorrect data. |

**Mitigation:**
- Read-only database connection for AI queries — cannot modify data
- SQL validation before execution (only SELECT, no DDL/DML)
- Display the generated SQL alongside the answer (transparency)
- Rate limiting: max 10 concurrent AI queries
- Query timeout: 5 seconds max execution time
- User-visible warning: "AI-generated analysis — verify against raw data"
- Result sanity checks: returned values must be within reasonable poker ranges

**Detection:** AI test suite with expected results; user feedback mechanism.

**Contingency:** Disable AI features remotely if accuracy drops below threshold.

---

### R12: AI Service Availability

| Attribute | Value |
|-----------|-------|
| **Probability** | 2 |
| **Impact** | 2 |
| **Score** | 4 (LOW) |
| **Description** | Anthropic API is unreachable. AI assistant is the only feature that depends on external services. |

**Mitigation:**
- Graceful degradation: AI tab shows "AI Assistant Unavailable" with retry button
- All other features work offline
- User can disable AI features entirely in settings
- Connection status indicator in AI tab

---

## 6. Project Risks

### R13: Scope Creep

| Attribute | Value |
|-----------|-------|
| **Probability** | 4 |
| **Impact** | 4 |
| **Score** | 16 (CRITICAL) |
| **Description** | "Let's add Omaha support" or "HUD would be easy now" during development. Core features delayed. MVP never ships. |

**Mitigation:**
- MVP definition is a living document but changes require explicit approval
- "Post-MVP" label on all deferred features in the backlog
- Weekly milestone review against the 12-week plan
- Hard rule: no new features after Week 8

---

### R14: Poker Domain Knowledge Gap

| Attribute | Value |
|-----------|-------|
| **Probability** | 3 |
| **Impact** | 4 |
| **Score** | 12 (HIGH) |
| **Description** | Developers misunderstand poker concepts. Stats are defined wrong. Edge cases in hand ranking are missed. Product is technically sound but poker-wrong. |

**Mitigation:**
- Poker Domain Expert reviews all engine code and stat definitions
- Reference implementations used for validation (not for copying)
- Test cases derived from widely-accepted poker resources
- Every stat definition documented with precise poker meaning and edge cases

---

### R15: Test Data Scarcity

| Attribute | Value |
|-----------|-------|
| **Probability** | 3 |
| **Impact** | 3 |
| **Score** | 9 (HIGH) |
| **Description** | Insufficient real hand history samples for testing. Test data doesn't cover edge cases. Bugs ship because test coverage looks good but data is shallow. |

**Mitigation:**
- Curated test hand histories with known edge cases (split pots, all-ins, disconnects)
- Synthetic hand generator that creates realistic test data at scale
- Property-based testing: generate random hands, verify invariants
- Minimum hand count for analytics testing: 10,000 hands

---

## Risk Summary (Sorted by Score)

| Rank | Risk | Score | Area |
|------|------|-------|------|
| 1 | R11: Incorrect SQL Generation | 16 | AI |
| 2 | R13: Scope Creep | 16 | Project |
| 3 | R1: Incorrect Hand Evaluation | 15 | Poker Engine |
| 4 | R4: SQLite Performance at Scale | 12 | Database |
| 5 | R7: Hand History Format Variations | 12 | Import |
| 6 | R14: Poker Domain Knowledge Gap | 12 | Project |
| 7 | R5: Database Corruption | 10 | Database |
| 8 | R3: Card Representation Ambiguity | 8 | Poker Engine |
| 9 | R6: Migration Failures | 8 | Database |
| 10 | R8: Duplicate Hand Detection | 9 | Import |
| 11 | R9: Frontend Performance | 9 | Frontend |
| 12 | R15: Test Data Scarcity | 9 | Project |
| 13 | R2: Monte Carlo Inaccuracy | 6 | Poker Engine |
| 14 | R10: Browser Compatibility | 4 | Frontend |
| 15 | R12: AI Service Availability | 4 | AI |

---

*Next: [Project Blueprint](./09-project-blueprint.md)*
