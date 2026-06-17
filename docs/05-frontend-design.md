# Poker Analytics Platform — Frontend Design

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## 1. Page Hierarchy & Routing

```
/                          → Dashboard (default landing)
/import                    → Hand History Import
/hands                     → Hand Explorer (browse, filter, search)
/hands/:handId             → Hand Replay (single hand detail view)
/players                   → Player List (search, browse all players)
/players/:playerId         → Player Profile (deep dive on one player)
/sessions                  → Session Tracker (session list)
/sessions/:sessionId       → Session Detail
/ai-assistant              → AI Assistant (chat interface)
/settings                  → Settings / Preferences
```

### 1.1 Navigation Structure

```
┌──────────────────────────────────────────────────────────────┐
│  SIDEBAR (always visible, collapsible)                       │
│                                                              │
│  📊 Dashboard                                                │
│  📥 Import Hands                                             │
│  🔍 Hand Explorer                                            │
│  👤 Players                                                  │
│  ⏱ Sessions                                                 │
│  🤖 AI Assistant                                             │
│  ⚙ Settings                                                 │
│                                                              │
│  ─────────────────────────────────────                       │
│  Quick Stats (collapsed sidebar shows mini-stats)            │
│  Hands: 124,583                                              │
│  bb/100: 4.2                                                 │
│  Net: +$3,421.50                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Page Designs

### 2.1 Dashboard (`/`)

**Purpose:** At-a-glance overview of performance. First thing the user sees.

```
┌──────────────────────────────────────────────────────────────────┐
│ Dashboard                                    [Date Filter ▼]    │
│                                                      [Stake ▼]  │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ Total    │ │ Net Won  │ │ bb/100   │ │ Hours    │             │
│ │ Hands    │ │          │ │          │ │ Played   │             │
│ │ 124,583  │ │ +$3,421  │ │ +4.2     │ │ 342.5    │             │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Cumulative Profit/Loss (Line Chart)                          │ │
│ │ ████████████████████████████████████████████████████████     │ │
│ │ ██████████░░░░░░░░░█████████████████████████████████████     │ │
│ │ ░░░░░░░░░░█████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     │ │
│ │ Jan    Feb    Mar    Apr    May    Jun                       │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌────────────────────────────┐ ┌──────────────────────────────┐ │
│ │ Recent Sessions (Table)    │ │ Win Rate by Position (Bar)   │ │
│ │ Date     Hands  Result     │ │ BTN ████████████ +8.2        │ │
│ │ Jun 15   842   +$124.50    │ │ CO  ██████████   +5.1        │ │
│ │ Jun 14   631   -$42.30     │ │ MP  ██████       +2.3        │ │
│ │ Jun 13   921   +$281.10    │ │ UTG ████         +0.8        │ │
│ │ Jun 12   412   +$15.20     │ │ SB  ██           -12.4       │ │
│ │                            │ │ BB  ██           -18.2       │ │
│ └────────────────────────────┘ └──────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- `StatCard` — reusable metric card (label, value, optional trend arrow)
- `ProfitLossChart` — Recharts `AreaChart` with cumulative profit line
- `RecentSessionsTable` — TanStack Table with sortable columns
- `PositionWinRateChart` — Recharts `BarChart` horizontal bars
- `GlobalFilterBar` — date range picker + stake dropdown

**Data Dependencies:**
- `GET /api/analytics/summary?date_from=&date_to=&stake=`
- `GET /api/analytics/profit-over-time?date_from=&date_to=&stake=`
- `GET /api/sessions?limit=5`

---

### 2.2 Hand History Import (`/import`)

**Purpose:** Import hand history files from poker sites.

```
┌──────────────────────────────────────────────────────────────────┐
│ Import Hands                                                     │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │                                                              │ │
│ │   📁  Drop hand history files here                           │ │
│ │       or click to browse                                     │ │
│ │                                                              │ │
│ │   Supported formats: PokerStars, GGPoker, Ignition/Bovada    │ │
│ │   Max file size: 50 MB per file                              │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ Import History:                                                  │
│ ┌────────┬──────────┬──────────┬──────────┬──────────┬────────┐ │
│ │ File   │ Site     │ Found    │ Imported │ Skipped  │ Errors │ │
│ ├────────┼──────────┼──────────┼──────────┼──────────┼────────┤ │
│ │ HH01   │ PokerSt★ │ 10,421   │ 10,412   │ 9 (dup)  │ 0      │ │
│ │ HH02   │ GGPoker  │ 5,231    │ 5,231    │ 0        │ 0      │ │
│ │ HH03   │ PokerSt★ │ 8,437    │ 8,200    │ 12 (dup) │ 225    │ │ ⚠
│ └────────┴──────────┴──────────┴──────────┴──────────┴────────┘ │
│                                                                  │
│ Import Progress: ████████████████░░░░░░ 78%  (8,234 / 10,500)    │
│ ETA: 2 seconds                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- `DropZone` — drag-and-drop file upload area
- `ImportHistoryTable` — table of past imports with status
- `ImportProgressBar` — real-time progress via SSE
- `ImportErrorPanel` — expandable error details per file

**Data Dependencies:**
- `POST /api/import/upload` (multipart file upload)
- `GET /api/import/status/{import_id}` (SSE for progress)
- `GET /api/import/history` (past import logs)

---

### 2.3 Hand Explorer (`/hands`)

**Purpose:** Browse, filter, search, and explore all imported hands.

```
┌──────────────────────────────────────────────────────────────────┐
│ Hand Explorer                                                    │
│                                                                  │
│ Filters:  [Date Range ▼] [Stake ▼] [Position ▼] [Result ▼]      │
│ Search:   [🔍 Search cards (e.g., "AKs", "JJ+") or players...]   │
│                                                                  │
│ ┌──────┬──────────┬───────┬────────┬────────┬────────┬────────┐  │
│ │ Date │ Hand #   │ Stake │ Cards  │ Pos    │ Result │ Actions│  │
│ ├──────┼──────────┼───────┼────────┼────────┼────────┼────────┤  │
│ │06/15 │2482151234│ 0.05/ │ A♠ K♠  │ CO     │ +$12.4 │  ▶️    │  │
│ │      │          │ 0.10  │        │        │        │        │  │
│ │06/15 │2482151120│ 0.05/ │ Q♥ Q♦  │ BTN    │ +$8.20 │  ▶️    │  │
│ │      │          │ 0.10  │        │        │        │        │  │
│ │06/15 │2482150987│ 0.05/ │ 7♣ 2♠  │ BB     │ -$1.50 │  ▶️    │  │
│ │      │          │ 0.10  │        │        │        │        │  │
│ │06/14 │2482150501│ 0.10/ │ A♦ K♥  │ UTG    │ -$22.0 │  ▶️    │  │
│ │      │          │ 0.25  │        │        │        │        │  │
│ └──────┴──────────┴───────┴────────┴────────┴────────┴────────┘  │
│                                              Page 1 of 2,500 ← → │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- `HandFilterBar` — date, stake, position, result range filters
- `CardSearch` — type-ahead search with card combo shorthand parsing
- `HandsTable` — TanStack Table with virtualized rows for large datasets
- `HandRow` — single row with card suit colors, result coloring (±green/red)

**Data Dependencies:**
- `GET /api/hands?page=&limit=&date_from=&stake=&position=&cards=&player=&result_min=&result_max=`
- `GET /api/hands/{id}` (for quick preview on hover)

---

### 2.4 Hand Replay (`/hands/:handId`)

**Purpose:** Step-by-step visual replay of a single hand.

```
┌──────────────────────────────────────────────────────────────────┐
│ ◀ Back to Explorer            Hand #2482151234 — Jun 15, 2026   │
│                                                                  │
│ ┌────────────────────────────────────┐ ┌───────────────────────┐ │
│ │         Poker Table Visual          │ │  Hand Details         │ │
│ │                                    │ │                       │ │
│ │  [SB]  400      [BB]  600         │ │  Stake: $0.05/$0.10   │ │
│ │  (Player3)      (Player4)    🟢    │ │  Table: Azura         │ │
│ │                                    │ │  Players: 6           │ │
│ │                                    │ │                       │ │
│ │         🃏🃏🃏🃏🃏  Board           │ │  Hero: J♠ T♠ (CO)    │ │
│ │         K♥ 7♦ 2♣ Q♠ A♦           │ │                       │ │
│ │                                    │ │  Preflop:             │ │
│ │  [CO]  Hero                        │ │  UTG folds            │ │
│ │  J♠ T♠     +$12.40                │ │  MP raises to $0.30   │ │
│ │                                    │ │  Hero calls $0.30     │ │
│ │         [BTN]  0                   │ │  BTN folds            │ │
│ │         (Player2)                  │ │  SB folds             │ │
│ │                                    │ │  BB calls $0.20       │ │
│ │  [MP]  0     [UTG]  0              │ │                       │ │
│ │  (Player1)   (Player5)            │ │  ▶ Flop: K♥ 7♦ 2♣    │ │
│ │                                    │ │  BB checks            │ │
│ └────────────────────────────────────┘ │  MP bets $0.45        │ │
│                                        │  Hero calls $0.45     │ │
│  [◀ Prev Hand]  [▶ Next Hand]         │  BB folds             │ │
│                                        │  ...                  │ │
│                                        └───────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- `PokerTable` — visual poker table with seats, cards, chips
- `ActionLog` — scrollable action-by-action timeline
- `StreetSelector` — tabs to jump to specific street
- `HandNavigator` — prev/next hand buttons

**Data Dependencies:**
- `GET /api/hands/{id}?include_actions=true`

---

### 2.5 Player Profile (`/players/:playerId`)

**Purpose:** Deep-dive analysis of a single player.

```
┌──────────────────────────────────────────────────────────────────┐
│ ◀ Back to Players          Player: "AlexTheGreat" (PokerStars)   │
│                                                    [Tag: 🐟 Fish]│
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ Hands    │ │ VPIP     │ │ PFR      │ │ 3Bet     │             │
│ │ 4,231    │ │ 24.3%    │ │ 18.7%    │ │ 6.2%     │             │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ Fold2 3B │ │ CBet F   │ │ AF       │ │ W$SD     │             │
│ │ 62.1%    │ │ 58.3%    │ │ 2.8      │ │ 52.1%    │             │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘             │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Stats by Position (Heatmap Table)                            │ │
│ │         VPIP   PFR   3Bet   CBet   AF    W$SD   bb/100       │ │
│ │ BTN     28.1   22.3   8.1   62.1   3.2   54.2   +12.4       │ │
│ │ CO      24.3   20.1   6.2   58.3   2.8   52.1   +5.2        │ │
│ │ MP      21.2   17.4   5.1   55.4   2.5   50.3   +2.1        │ │
│ │ UTG     18.4   15.2   4.2   52.1   2.1   48.2   +0.8        │ │
│ │ SB      22.1    8.3   4.8   48.2   2.3   47.2   -8.2        │ │
│ │ BB      20.3    5.2   3.2   42.1   1.8   46.1   -14.3       │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Player Type: LAG (Loose-Aggressive)                          │ │
│ │ VPIP > 22% and PFR > 15% and AF > 2.5                        │ │
│ │                                                              │ │
│ │ ⚠ Leak: High Fold to 3Bet (62.1%)                            │ │
│ │   Consider defending wider vs aggressive 3-bettors            │ │
│ │                                                              │ │
│ │ ⚠ Leak: Losing from SB (-8.2 bb/100)                         │ │
│ │   Tighten SB opening range; avoid completing with weak hands  │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- `PlayerStatCard` — individual stat display
- `PositionHeatmap` — color-coded stat-by-position table
- `PlayerTypeBadge` — TAG/LAG/Nit badge
- `LeakCard` — individual leak finding with explanation

**Data Dependencies:**
- `GET /api/players/{id}/stats`
- `GET /api/players/{id}/stats-by-position`
- `GET /api/players/{id}/profile`
- `GET /api/players/{id}/leaks`

---

### 2.6 AI Assistant (`/ai-assistant`)

**Purpose:** Natural language interface for querying poker data.

```
┌──────────────────────────────────────────────────────────────────┐
│ 🤖 AI Assistant                                                  │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │                                                              │ │
│ │  You: What's my win rate with pocket pairs this month?       │ │
│ │                                                              │ │
│ │  ┌──────────────────────────────────────────────────────┐    │ │
│ │  │ AI: Your win rate with pocket pairs (22-AA) in June  │    │ │
│ │  │ 2026 is +3.2 bb/100 over 847 hands.                  │    │ │
│ │  │                                                      │    │ │
│ │  │ Breakdown by pair:                                   │    │ │
│ │  │ • AA: +12.4 bb/100 (42 hands)                        │    │ │
│ │  │ • KK: +10.1 bb/100 (38 hands)                        │    │ │
│ │  │ • QQ: +7.2 bb/100 (35 hands)                         │    │ │
│ │  │ • JJ: +4.8 bb/100 (41 hands)                         │    │ │
│ │  │ • TT-22: -1.2 bb/100 (691 hands)                     │    │ │
│ │  │                                                      │    │ │
│ │  │ ⚠ You're losing with small/medium pairs. Consider    │    │ │
│ │  │ folding 22-66 from early position.                   │    │ │
│ │  └──────────────────────────────────────────────────────┘    │ │
│ │                                                              │ │
│ │  ┌──────────────────────────────────────────────────────┐    │ │
│ │  │ Suggested questions:                                  │    │ │
│ │  │ • "What's my biggest leak right now?"                 │    │ │
│ │  │ • "Show me my redline vs blueline trend"              │    │ │
│ │  │ • "Who are my most profitable opponents?"             │    │ │
│ │  └──────────────────────────────────────────────────────┘    │ │
│ │                                                              │ │
│ │  [Type your question...]                              [Send] │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- `ChatWindow` — scrollable message list with user/AI bubbles
- `ChatInput` — text input with send button and suggested questions
- `DataCard` — inline data display (tables, charts) within AI responses
- `SuggestionChips` — clickable suggested questions

**Data Dependencies:**
- `POST /api/ai/query` — sends question, receives answer with optional embedded data
- `GET /api/ai/suggestions` — context-aware suggested questions

---

### 2.7 Player Compare (`/players/compare?p1=&p2=`)

**Purpose:** Side-by-side comparison of two players.

```
┌──────────────────────────────────────────────────────────────────┐
│ Player Comparison                                                │
│                                                                  │
│ [Player A: AlexTheGreat ▼]  vs  [Player B: SolidReg ▼]          │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Stat          │ AlexTheGreat      │ SolidReg          │ Diff  │ │
│ ├───────────────┼───────────────────┼───────────────────┼───────┤ │
│ │ Hands         │ 4,231             │ 12,843            │       │ │
│ │ VPIP          │ 24.3%             │ 18.2%             │ +6.1% │ │
│ │ PFR           │ 18.7%             │ 14.8%             │ +3.9% │ │
│ │ 3Bet          │ 6.2%              │ 5.1%              │ +1.1% │ │
│ │ Fold to 3Bet  │ 62.1% 🟡          │ 48.2%             │ +13.9%│ │
│ │ AF            │ 2.8               │ 2.4               │ +0.4  │ │
│ │ W$SD          │ 52.1%             │ 55.8%             │ -3.7% │ │
│ │ bb/100        │ +4.2              │ +8.1              │ -3.9  │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Shared Component Library

### 3.1 Core Components

| Component | Description | Props |
|-----------|-------------|-------|
| `StatCard` | Single metric with label, value, trend | `label`, `value`, `formattedValue`, `trend?` ('up','down','flat'), `color?` |
| `DataTable` | Sortable, filterable, paginated table | `columns`, `data`, `sortable`, `onRowClick` |
| `Chart` | Wrapper around Recharts with consistent styling | `type`, `data`, `config` |
| `PokerTable` | Visual representation of a poker table | `seats`, `board`, `pot`, `currentStreet` |
| `CardDisplay` | Single card with suit color | `card` (2-char code), `size` ('sm','md','lg'), `faceDown?` |
| `PlayerBadge` | Player type indicator | `playerType` ('tag','lag','nit','station','maniac','unknown') |
| `PositionBadge` | Position indicator | `position` ('BTN','CO','MP','UTG','SB','BB') |
| `FilterBar` | Global filter controls | `filters`, `onChange` |
| `EmptyState` | Shown when no data | `title`, `description`, `action?` |

### 3.2 Card Display System

Cards are rendered consistently everywhere using the `CardDisplay` component:

```
A♠  K♥  Q♦  J♣  T♠  9♥  8♦  7♣  6♠  5♥  4♦  3♣  2♠
🅰♤  🅺♡  🆀♢  🅹♧  🆃♤  9♡  8♢  7♧  6♤  5♡  4♢  3♧  2♤
```

- Spades (♠) and Clubs (♣): **black/dark**
- Hearts (♥) and Diamonds (♦): **red**
- Face-down cards: blue/gray patterned back
- Small variant: text-only for tables
- Large variant: card-shaped with suit icon for replays

---

## 4. State Management

### 4.1 Store Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Zustand Stores                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ useAppStore  │  │useFilterStore│  │useImportStore│       │
│  │              │  │              │  │              │       │
│  │ - appStatus  │  │ - dateRange  │  │ - status     │       │
│  │ - heroPlayer │  │ - stake      │  │ - progress   │       │
│  │ - dbStats    │  │ - position   │  │ - errors     │       │
│  │ - settings   │  │ - playerId   │  │ - history    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ useUIStore   │  │useAIStore    │                         │
│  │              │  │              │                         │
│  │ - sidebarOpen│  │ - messages   │                         │
│  │ - theme      │  │ - isLoading  │                         │
│  │ - activePage │  │ - suggestions│                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Server State (TanStack Query)

All API data uses TanStack Query for caching and synchronization:

```typescript
// Example: Dashboard data
function useDashboardSummary(filters: GlobalFilters) {
  return useQuery({
    queryKey: ['dashboard', 'summary', filters],
    queryFn: () => api.getDashboardSummary(filters),
    staleTime: 60_000,  // 1 minute before refetch
  });
}
```

### 4.3 State Flow Pattern

```
User Action → Zustand Action → Optimistic UI Update
                            → API Call (TanStack Query)
                                → Invalidate Queries
                                → UI Re-renders with Server Data
```

---

## 5. UI/UX Principles

### 5.1 Design Language

- **Dark theme default** — poker players play at night; dark UI reduces eye strain
- **Green accents** — poker table green (#2E7D32) as primary accent color
- **Red/Green semantics** — losses in red (#EF5350), wins in green (#4CAF50)
- **Monospace for data** — all numbers, stats, and card codes use monospace font
- **Suit colors** — hearts/diamonds red, spades/clubs white/light

### 5.2 Responsiveness

- Desktop-first: optimized for 1440px and 1920px widths
- Minimum supported width: 1024px
- Sidebar collapses to icon-only below 1280px
- Tables use horizontal scroll below 1200px

### 5.3 Interaction Patterns

- **Progressive disclosure:** Show top-level stats, click to drill down
- **Inline expansion:** Expand table rows for quick preview instead of navigating away
- **Keyboard shortcuts:**
  - `Ctrl+K` — global search/command palette
  - `←` `→` — navigate between hands in replay
  - `Space` — advance one action in replay
  - `Ctrl+I` — open import dialog

---

## 6. Frontend Technology Stack

| Library | Version | Purpose |
|---------|---------|---------|
| React | 18.3+ | UI framework |
| TypeScript | 5.4+ | Type safety |
| Vite | 5.x | Build tool & dev server |
| React Router | 6.x | Client-side routing |
| Zustand | 4.x | Client state management |
| TanStack Query | 5.x | Server state & caching |
| TanStack Table | 8.x | Data tables |
| Recharts | 2.x | Charts & data visualization |
| Tailwind CSS | 3.x | Utility-first CSS |
| Radix UI | latest | Accessible headless UI primitives |
| Lucide React | latest | Icon library |

---

*Next: [Backend APIs](./06-backend-apis.md)*
