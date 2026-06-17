# Poker Analytics Platform — MVP Definition

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## 1. MVP Philosophy

The MVP delivers a **complete, usable analytics workflow** for a single-stakes Texas Hold'em cash game player. Every feature in the MVP must work end-to-end with production-quality polish. Nothing is "placeholder." Features that cannot be completed to production quality in 12 weeks are deferred to post-MVP.

### Guiding Rules

- **Complete, not comprehensive.** Fewer features done well > many features done poorly.
- **Single player first.** Multi-player sharing, coaching features, and team accounts are post-MVP.
- **Cash game first.** Tournament support (ICM, payout structures, bubble factors) is post-MVP.
- **Desktop only.** Responsive design is fine, but mobile-specific layouts and touch interactions are post-MVP.

---

## 2. MVP Feature Set

### F1 — Hand History Import

**Priority:** P0 (Critical Path)
**Effort Estimate:** 3 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F1.1 | As a user, I can import PokerStars hand history files (.txt) | File picker accepts .txt; hands are parsed and stored; errors are reported per-hand with line numbers |
| F1.2 | As a user, I can import GGPoker hand history files | Same as F1.1 for GGPoker format |
| F1.3 | As a user, I can import Ignition/Bovada hand history files | Same as F1.1 for Ignition format |
| F1.4 | As a user, I see import progress in real-time | Progress bar shows hands processed / total; estimated time remaining |
| F1.5 | As a user, duplicate hands are silently skipped | Import detects duplicate hand IDs and skips without error |
| F1.6 | As a user, I can import multiple files at once | Multi-file picker or drag-and-drop folder; all files processed sequentially |

**MVP Format Support:**
- PokerStars (Zoom included)
- GGPoker (regular cash)
- Ignition/Bovada (anonymous player mapping)

**Designed for Extension (Post-MVP):**
The import architecture uses a pluggable parser pattern. The database schema is entirely site-agnostic. Adding Winamax, PartyPoker, or iPoker support requires only a new parser class implementing `AbstractParser` — zero database schema changes, zero API changes, zero frontend changes. See [System Architecture](./03-system-architecture.md#23-importer-architecture--pluggable-parsers) for details.

---

### F2 — Hand History Browser

**Priority:** P0 (Critical Path)
**Effort Estimate:** 2 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F2.1 | As a user, I can browse all imported hands in a table | Table shows: date, stake, position, hole cards, result, net won; sortable columns |
| F2.2 | As a user, I can filter hands by date range | Date picker filters the table in real-time |
| F2.3 | As a user, I can filter hands by stake/limit | Dropdown populated from available stakes in the database |
| F2.4 | As a user, I can search hands by card combination | Search "AKs" returns all hands with Ace-King suited |
| F2.5 | As a user, I can view a full hand replay | Replay view shows: each street's board cards, each player's actions in sequence, pot size progression |
| F2.6 | As a user, I can search hands by player name | Type-ahead search returns all hands involving that player |

---

### F3 — Dashboard

**Priority:** P0 (Critical Path)
**Effort Estimate:** 2 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F3.1 | As a user, I see a summary dashboard on launch | Dashboard shows: total hands, total profit/loss, bb/100, hours played, recent sessions |
| F3.2 | As a user, I see a profit/loss chart over time | Interactive line chart; x=date, y=cumulative profit; zoomable |
| F3.3 | As a user, I see a session breakdown table | Table of sessions: date, duration, hands, result, bb/100, stake |
| F3.4 | As a user, I can filter dashboard by date range | Global date filter affects all dashboard widgets |
| F3.5 | As a user, I can filter dashboard by stake | Stake filter affects all dashboard widgets |

---

### F4 — Poker Engine

**Priority:** P0 (Critical Path)
**Effort Estimate:** 3 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F4.1 | Hand ranking correctly evaluates all 7,462 distinct 5-card hands | Unit tests exhaustively verify ranking against known-good reference data |
| F4.2 | Hand ranking correctly evaluates 7-card hands (best 5 of 7) | Exhaustive or comprehensive random testing against reference |
| F4.3 | Equity calculator computes heads-up all-in equity | Result within 0.1% of known values for all common matchups |
| F4.4 | Monte Carlo simulator runs range vs range equity | Configurable iteration count; results converge within acceptable variance |
| F4.5 | Outs calculator identifies correct outs for drawing hands | Verified against known poker test cases |

---

### F5 — Core Analytics

**Priority:** P0 (Critical Path)
**Effort Estimate:** 2 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F5.1 | As a user, I see VPIP and PFR for any player | Stats computed from stored hands; displayed as percentage |
| F5.2 | As a user, I see 3Bet and Fold to 3Bet stats | Computed from stored hands |
| F5.3 | As a user, I see CBet and Fold to CBet stats by street | Flop/Turn/River breakdown |
| F5.4 | As a user, I see Aggression Factor | (Bets + Raises) / Calls |
| F5.5 | As a user, I see WTSD, W$SD, and bb/100 | Accurate to stored hand data |
| F5.6 | As a user, I can view stats by position | EP/MP/CO/BTN/SB/BB breakdown |
| F5.7 | As a user, I can view stats by session | Per-session stat lines |

---

### F6 — Player Analysis

**Priority:** P1 (High)
**Effort Estimate:** 2 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F6.1 | As a user, I can search for and view a player profile | Profile shows all stats, hand count, net result |
| F6.2 | As a user, I see position-based stats for any player | Stat grid with rows=stat, columns=position |
| F6.3 | As a user, I get an automatic player type classification | TAG, LAG, Nit, Calling Station, Maniac based on stat thresholds |
| F6.4 | As a user, I see basic leak indicators | "VPIP too high from EP" style warnings with supporting data |
| F6.5 | As a user, I can compare two players side-by-side | Side-by-side stat table |

---

### F7 — AI Assistant

**Priority:** P1 (High)
**Effort Estimate:** 2 weeks

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F7.1 | As a user, I can ask natural language questions about my data | "What's my win rate this month?" returns correct answer with data |
| F7.2 | As a user, I can ask the AI to find leaks | AI analyzes stats and returns actionable findings |
| F7.3 | As a user, the AI explains poker statistics | "What does VPIP mean?" returns clear explanation |
| F7.4 | As a user, the AI can query specific hands | "Show me my biggest losing hands this month" returns hand list |

---

### F8 — Session Tracking

**Priority:** P1 (High)
**Effort Estimate:** 1 week

| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| F8.1 | As a user, hands are automatically grouped into sessions | Hands within 30 minutes of each other belong to same session |
| F8.2 | As a user, I can manually adjust session boundaries | Merge/split sessions |
| F8.3 | As a user, I can add session notes | Free-text notes field per session |

---

## 3. User Flows

### Primary Flow: Import → Analyze → Improve

```
1. User opens app → sees empty dashboard with import CTA
2. User imports hand history files → sees import progress
3. Import completes → dashboard populates with summary stats
4. User browses dashboard → notices negative trend in recent sessions
5. User opens Player Analysis → views own stats → sees "Fold to 3Bet too high (78%)" leak indicator
6. User asks AI Assistant: "Show me all hands where I folded to a 3bet preflop"
7. AI returns filtered hand list → user replays key hands
8. User identifies pattern → adjusts strategy
9. User imports next session → tracks improvement in Fold to 3Bet stat
```

### Secondary Flow: Hand Review

```
1. User finishes session → imports new hands
2. User navigates to Hand Explorer
3. Filters for biggest losing hands (>= 50bb lost)
4. Replays each hand step-by-step
5. Tags hands for later review
6. Shares interesting hands with coach (future feature)
```

---

## 4. What MVP Explicitly Excludes

| Feature | Reason for Deferral |
|---------|-------------------|
| Tournament support | Adds ICM, payout structures, blind level tracking — significant complexity |
| Omaha support | Different hand ranking rules, different equity calculation needs |
| Real-time HUD | Requires screen overlay tech, live hand detection — separate engineering effort |
| Cloud sync | Requires auth, conflict resolution, infrastructure — post-MVP |
| Mobile app | Separate UI design and development effort |
| Hand annotation/sharing | Coaching features — valuable but not core to single-user analytics |
| Custom stat builder | Power user feature — predefined stats cover 90% of needs |
| GTO solver integration | Massive complexity; separate product |
| Rakeback tracking | Data model complexity for minimal analytics value in MVP |

---

## 5. MVP Success Criteria

The MVP is **done** when:

1. A user can import 100,000+ hands from all three supported formats without errors
2. All core statistics (VPIP, PFR, 3Bet, CBet, AF, WTSD, W$SD, bb/100) are computed correctly
3. The dashboard shows accurate, interactive profit/loss charts
4. The hand explorer allows filtering, searching, and replaying any hand
5. The AI assistant can answer natural language questions about the user's data
6. The poker engine passes exhaustive hand-ranking tests
7. The application runs offline with all data stored locally
8. Import throughput exceeds 10,000 hands/second

---

## 6. Feature Dependency Map

```
Hand History Import ──────┬──► Dashboard
                          │
                          ├──► Hand Explorer
                          │
                          ├──► Core Analytics ──► Player Analysis
                          │
                          ├──► Session Tracking
                          │
                          └──► AI Assistant (queries stored data)

Poker Engine ─────────────┬──► Core Analytics (hand evaluation for stats)
                          │
                          └──► Hand Explorer (replay hand rankings)
```

---

*Next: [System Architecture](./03-system-architecture.md)*
