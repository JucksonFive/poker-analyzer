# Poker Analytics Platform — Database Schema

**Document Version:** 1.0
**Date:** 2026-06-16
**Status:** Draft

---

## 1. Entity Relationship Diagram

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│  Session  │       │     Hand     │       │  Player  │
│           │ 1──┐  │              │  ┌───1│          │
│  id       │    │  │  id          │  │    │  id      │
│  start_   │    │  │  session_id* │  │    │  name    │
│  end_time │    └──│  site        │  │    │  site    │
│  ...      │       │  table_name  │  │    └──────────┘
└──────────┘       │  stake_sb     │  │         │
                   │  stake_bb     │  │         │
                   │  ...          │  │         │
                   └──────────────┘  │         │
                          │          │         │
                          │ 1        │         │
                          │          │         │
                   ┌──────┴──────────┴─┐       │
                   │   HandPlayer      │       │
                   │                   │       │
                   │  hand_id*    ─────┼───────┘
                   │  player_id*  ─────┼── (also joins to player)
                   │  position         │
                   │  hole_card_1      │
                   │  hole_card_2      │
                   │  net_result       │
                   │  is_hero          │
                   └───────────────────┘
                          │
                          │ 1
                          │
                   ┌──────┴──────────┐
                   │    Action       │
                   │                 │
                   │  hand_player_id*│
                   │  street         │
                   │  action_type    │
                   │  amount         │
                   │  seq_num        │
                   └─────────────────┘
```

## 2. Site Format Extensibility

The schema is **site-agnostic**. The `site` column across tables stores a string identifier (`'pokerstars'`, `'ggpoker'`, `'winamax'`, `'partypoker'`, `'ipoker'`, `'ignition'`). No table has site-specific columns. This means:

- Adding a new site format requires **zero schema changes** — only a new parser implementation
- All analytics queries work across sites without modification
- Players are identified by `(name, site)` so the same name on different sites is tracked separately
- Site-specific hand history quirks are handled entirely in the parser layer, never in the database

**MVP format support:** PokerStars, GGPoker, Ignition/Bovada
**Post-MVP format support:** Winamax, PartyPoker, iPoker

## 3. Table Definitions

### 2.1 `sessions`

A session represents a continuous period of play. Hands within 30 minutes of each other are grouped into the same session.

```sql
CREATE TABLE sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    site          TEXT    NOT NULL,              -- 'pokerstars', 'ggpoker', 'ignition'
    table_name    TEXT,                          -- NULL if multi-table session
    stake_sb      REAL    NOT NULL,              -- Small blind amount (e.g., 0.05)
    stake_bb      REAL    NOT NULL,              -- Big blind amount (e.g., 0.10)
    game_type     TEXT    NOT NULL DEFAULT 'NLHE', -- 'NLHE', 'PLO' (future)
    max_players   INTEGER NOT NULL DEFAULT 6,    -- 2, 6, 9
    start_time    TEXT    NOT NULL,              -- ISO 8601 datetime
    end_time      TEXT    NOT NULL,              -- ISO 8601 datetime
    hands_count   INTEGER NOT NULL DEFAULT 0,   -- Denormalized for convenience
    net_result    REAL    NOT NULL DEFAULT 0.0,  -- Denormalized total P/L for hero
    notes         TEXT,                          -- User notes
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_sessions_start_time ON sessions(start_time);
CREATE INDEX idx_sessions_site_stake ON sessions(site, stake_sb, stake_bb);
```

### 2.2 `players`

A player is identified by the tuple `(name, site)`. Names are normalized (lowercase, trimmed) before storage.

```sql
CREATE TABLE players (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,              -- Normalized player name
    site          TEXT    NOT NULL,              -- Site where this name was seen
    first_seen    TEXT    NOT NULL,              -- ISO 8601 of first hand
    last_seen     TEXT    NOT NULL,              -- ISO 8601 of most recent hand
    total_hands   INTEGER NOT NULL DEFAULT 0,   -- Denormalized
    is_hero       INTEGER NOT NULL DEFAULT 0,   -- 1 = this is the app user
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now')),

    UNIQUE(name, site)
);

CREATE INDEX idx_players_name ON players(name);
CREATE INDEX idx_players_site ON players(site);
```

### 2.3 `hands`

The central table. Each row is one complete poker hand.

```sql
CREATE TABLE hands (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hand_number     TEXT    NOT NULL,           -- Site-assigned hand ID (string — some sites use alphanumeric)
    site            TEXT    NOT NULL,           -- 'pokerstars', 'ggpoker', 'ignition'
    session_id      INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
    table_name      TEXT    NOT NULL,
    stake_sb        REAL    NOT NULL,
    stake_bb        REAL    NOT NULL,
    game_type       TEXT    NOT NULL DEFAULT 'NLHE',
    max_players     INTEGER NOT NULL,
    num_players     INTEGER NOT NULL,           -- Players dealt in
    hero_id         INTEGER REFERENCES players(id),
    hero_position   TEXT,                        -- Hero's position this hand
    -- Board cards
    flop_1          TEXT,                        -- 2-char card code: 'Ah', 'Ks', 'Td', etc.
    flop_2          TEXT,
    flop_3          TEXT,
    turn            TEXT,
    river           TEXT,
    -- Results
    total_pot       REAL    NOT NULL DEFAULT 0.0,
    rake            REAL    NOT NULL DEFAULT 0.0,
    hero_net_won    REAL    NOT NULL DEFAULT 0.0, -- Denormalized for fast aggregation
    showdown        INTEGER NOT NULL DEFAULT 0,   -- 1 = went to showdown
    -- Metadata
    played_at       TEXT    NOT NULL,            -- ISO 8601 of when the hand was played
    imported_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    raw_text        TEXT,                        -- Original hand history text (optional, for debugging)

    UNIQUE(hand_number, site)
);

-- Performance indexes
CREATE INDEX idx_hands_played_at      ON hands(played_at);
CREATE INDEX idx_hands_session        ON hands(session_id);
CREATE INDEX idx_hands_hero           ON hands(hero_id);
CREATE INDEX idx_hands_stake          ON hands(stake_sb, stake_bb);
CREATE INDEX idx_hands_site_played    ON hands(site, played_at);
CREATE INDEX idx_hands_hero_played    ON hands(hero_id, played_at);

-- FTS5 for text search
CREATE VIRTUAL TABLE hands_fts USING fts5(
    hand_number,
    table_name,
    content='hands',
    content_rowid='id'
);
```

### 2.4 `hand_players`

A player's participation in a specific hand. Links players to hands with position, hole cards, and results.

```sql
CREATE TABLE hand_players (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hand_id         INTEGER NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id       INTEGER NOT NULL REFERENCES players(id),
    seat_number     INTEGER NOT NULL,           -- 1-based seat at the table
    position        TEXT    NOT NULL,            -- 'BTN', 'SB', 'BB', 'UTG', 'MP', 'CO', etc.
    hole_card_1     TEXT,                        -- 2-char card code; NULL if unknown (mucked)
    hole_card_2     TEXT,                        -- 2-char card code; NULL if unknown
    starting_stack  REAL    NOT NULL,
    ending_stack    REAL,
    amount_won      REAL    NOT NULL DEFAULT 0.0, -- Net won this hand
    amount_invested REAL    NOT NULL DEFAULT 0.0, -- Total put into pot
    is_hero         INTEGER NOT NULL DEFAULT 0,   -- 1 = this is the user
    is_winner       INTEGER NOT NULL DEFAULT 0,   -- 1 = won the pot
    won_at_showdown INTEGER NOT NULL DEFAULT 0,   -- 1 = won at showdown (vs without)
    showdown_hand   TEXT,                          -- Best 5-card hand description at showdown
    showdown_rank   INTEGER,                       -- Numeric hand rank (0=high card, 8=straight flush)
    cards_played    INTEGER NOT NULL DEFAULT 0,   -- 1 = saw flop, 2 = saw turn, 3 = saw river

    UNIQUE(hand_id, player_id)
);

CREATE INDEX idx_handplayers_hand     ON hand_players(hand_id);
CREATE INDEX idx_handplayers_player   ON hand_players(player_id);
CREATE INDEX idx_handplayers_hero     ON hand_players(is_hero) WHERE is_hero = 1;
CREATE INDEX idx_handplayers_position ON hand_players(player_id, position);
CREATE INDEX idx_handplayers_holecards ON hand_players(hole_card_1, hole_card_2)
    WHERE hole_card_1 IS NOT NULL;
```

### 2.5 `actions`

Every action taken by every player on every street. This is the most granular table.

```sql
CREATE TABLE actions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hand_player_id  INTEGER NOT NULL REFERENCES hand_players(id) ON DELETE CASCADE,
    hand_id         INTEGER NOT NULL REFERENCES hands(id) ON DELETE CASCADE,  -- Denormalized for query speed
    street          TEXT    NOT NULL,            -- 'PREFLOP', 'FLOP', 'TURN', 'RIVER'
    action_type     TEXT    NOT NULL,            -- 'POST_SB', 'POST_BB', 'POST_ANTE',
                                                  -- 'FOLD', 'CHECK', 'CALL', 'BET', 'RAISE', 'ALL_IN'
    amount          REAL    NOT NULL DEFAULT 0.0,
    is_all_in       INTEGER NOT NULL DEFAULT 0,
    pot_after       REAL,                         -- Pot size after this action
    seq_number      INTEGER NOT NULL,            -- Global sequence within the hand (starts at 1)
    street_seq      INTEGER NOT NULL,            -- Sequence within the street (starts at 1)
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_actions_hand            ON actions(hand_id);
CREATE INDEX idx_actions_handplayer      ON actions(hand_player_id);
CREATE INDEX idx_actions_player_street   ON actions(hand_player_id, street);
CREATE INDEX idx_actions_hand_seq        ON actions(hand_id, seq_number);
CREATE INDEX idx_actions_type_street     ON actions(action_type, street);
```

### 2.6 `import_logs`

Tracks every import operation for audit and debugging.

```sql
CREATE TABLE import_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        TEXT    NOT NULL,
    file_hash       TEXT,                        -- SHA-256 of file for dedup
    site            TEXT    NOT NULL,
    hands_found     INTEGER NOT NULL DEFAULT 0,
    hands_imported  INTEGER NOT NULL DEFAULT 0,
    hands_skipped   INTEGER NOT NULL DEFAULT 0,  -- Duplicates
    hands_error     INTEGER NOT NULL DEFAULT 0,  -- Parse failures
    errors_json     TEXT,                        -- JSON array of error details
    started_at      TEXT    NOT NULL,
    completed_at    TEXT,
    status          TEXT    NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'failed'
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_import_logs_date ON import_logs(started_at);
```

### 2.7 `player_tags` (Future / Light in MVP)

User-assigned tags/labels for players.

```sql
CREATE TABLE player_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id   INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    tag         TEXT    NOT NULL,                 -- 'fish', 'reg', 'aggro', etc.
    color       TEXT,                             -- Hex color for UI
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),

    UNIQUE(player_id, tag)
);
```

---

## 3. Card Representation

All cards are stored as **2-character strings**:

| Character | Meaning |
|-----------|---------|
| First char | Rank: `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `T`, `J`, `Q`, `K`, `A` |
| Second char | Suit: `c` (clubs), `d` (diamonds), `h` (hearts), `s` (spades) |

Examples: `Ah` = Ace of hearts, `Td` = Ten of diamonds, `2c` = Two of clubs

Board cards are stored as nullable columns. When there is no flop, `flop_1`, `flop_2`, `flop_3` are all NULL. When there is no turn, `turn` is NULL. When there is no river, `river` is NULL.

---

## 4. Key Analytics Queries

### 4.1 VPIP (Voluntarily Put Money In Pot)

Percentage of hands where the player voluntarily put money in preflop (posted blind does not count as voluntary).

```sql
-- For a specific player
SELECT
    COUNT(*) AS total_hands,
    SUM(CASE WHEN EXISTS (
        SELECT 1 FROM actions a
        WHERE a.hand_player_id = hp.id
          AND a.street = 'PREFLOP'
          AND a.action_type IN ('CALL', 'BET', 'RAISE')
          AND a.amount > 0
    ) THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS vpip
FROM hand_players hp
WHERE hp.player_id = ?
  AND hp.position NOT IN ('SB', 'BB');  -- Exclude blinds unless they voluntarily add more
```

### 4.2 PFR (Preflop Raise)

```sql
SELECT
    COUNT(*) AS total_hands,
    SUM(CASE WHEN EXISTS (
        SELECT 1 FROM actions a
        WHERE a.hand_player_id = hp.id
          AND a.street = 'PREFLOP'
          AND a.action_type IN ('BET', 'RAISE')
    ) THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pfr
FROM hand_players hp
WHERE hp.player_id = ?;
```

### 4.3 3Bet Percentage

```sql
-- Percentage of times player 3bet when facing a raise preflop
SELECT
    COUNT(*) AS opportunities,
    SUM(CASE WHEN has_3bet = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS three_bet_pct
FROM (
    SELECT hp.id,
        CASE WHEN EXISTS (
            SELECT 1 FROM actions a
            WHERE a.hand_player_id = hp.id
              AND a.street = 'PREFLOP'
              AND a.action_type = 'RAISE'
              AND a.seq_number > (
                  SELECT MIN(a2.seq_number) FROM actions a2
                  WHERE a2.hand_id = hp.hand_id
                    AND a2.street = 'PREFLOP'
                    AND a2.action_type = 'RAISE'
                    AND a2.hand_player_id != hp.id
              )
        ) THEN 1 ELSE 0 END AS has_3bet
    FROM hand_players hp
    WHERE hp.player_id = ?
      AND EXISTS (
          SELECT 1 FROM actions a
          WHERE a.hand_id = hp.hand_id
            AND a.street = 'PREFLOP'
            AND a.action_type = 'RAISE'
            AND a.hand_player_id != hp.id
      )
);
```

### 4.4 Aggression Factor

```
(Bets + Raises) / Calls
```

```sql
SELECT
    SUM(CASE WHEN action_type IN ('BET', 'RAISE') THEN 1 ELSE 0 END) * 1.0 /
    NULLIF(SUM(CASE WHEN action_type = 'CALL' THEN 1 ELSE 0 END), 0) AS aggression_factor
FROM actions a
JOIN hand_players hp ON a.hand_player_id = hp.id
WHERE hp.player_id = ?;
```

### 4.5 bb/100 (Big Blinds per 100 Hands)

```sql
SELECT
    SUM(hp.amount_won) / (SELECT DISTINCT stake_bb FROM hands WHERE id = hp.hand_id LIMIT 1)
    / (COUNT(*) / 100.0) AS bb_per_100
FROM hand_players hp
WHERE hp.player_id = ?
  AND hp.is_hero = 1;
```

### 4.6 Profit/Loss Over Time

```sql
SELECT
    DATE(h.played_at) AS day,
    SUM(hp.amount_won) AS net_won,
    COUNT(*) AS hands_played
FROM hand_players hp
JOIN hands h ON hp.hand_id = h.id
WHERE hp.is_hero = 1
GROUP BY DATE(h.played_at)
ORDER BY day;
```

### 4.7 Session Summary

```sql
SELECT
    s.id,
    s.start_time,
    s.end_time,
    s.stake_sb,
    s.stake_bb,
    s.hands_count,
    s.net_result,
    (s.net_result / s.stake_bb) / (s.hands_count / 100.0) AS bb_per_100,
    (strftime('%s', s.end_time) - strftime('%s', s.start_time)) / 3600.0 AS hours
FROM sessions s
ORDER BY s.start_time DESC;
```

### 4.8 Position-Based Stats

```sql
SELECT
    hp.position,
    COUNT(*) AS hands,
    SUM(hp.amount_won) AS net_won,
    AVG(hp.amount_won) AS avg_won_per_hand,
    SUM(CASE WHEN EXISTS (
        SELECT 1 FROM actions a WHERE a.hand_player_id = hp.id
        AND a.street = 'PREFLOP' AND a.action_type IN ('CALL', 'BET', 'RAISE')
    ) THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS vpip
FROM hand_players hp
WHERE hp.player_id = ?
GROUP BY hp.position
ORDER BY
    CASE hp.position
        WHEN 'BTN' THEN 1 WHEN 'CO' THEN 2 WHEN 'MP' THEN 3
        WHEN 'UTG' THEN 4 WHEN 'SB' THEN 5 WHEN 'BB' THEN 6
        ELSE 7
    END;
```

### 4.9 Hand Search by Hole Cards

```sql
SELECT h.*, hp.position, hp.hole_card_1, hp.hole_card_2, hp.amount_won
FROM hands h
JOIN hand_players hp ON h.id = hp.hand_id
WHERE hp.is_hero = 1
  AND hp.hole_card_1 IS NOT NULL
  AND (
      (hp.hole_card_1 LIKE 'A%' AND hp.hole_card_2 LIKE 'K%')
      OR
      (hp.hole_card_1 LIKE 'K%' AND hp.hole_card_2 LIKE 'A%')
  )
ORDER BY h.played_at DESC;
```

---

## 5. Migration Strategy

### 5.1 Tooling

- **Alembic** for migration management
- Each migration is a `.py` file with `upgrade()` and `downgrade()` functions
- Migrations are numbered sequentially

### 5.2 Version Tracking

```sql
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);
```

### 5.3 Migration Policy

1. All schema changes go through Alembic migrations — never manually alter the database
2. Each migration is tested with both `upgrade` and `downgrade` in CI
3. Migration files include data migration logic when needed
4. Breaking schema changes are avoided in MVP — only additive changes

### 5.4 Initial Migration Sequence

```
001_create_players.py
002_create_sessions.py
003_create_hands.py
004_create_hand_players.py
005_create_actions.py
006_create_import_logs.py
007_create_player_tags.py
008_create_fts_indexes.py
```

---

## 6. Performance Considerations

### 6.1 Write Optimization

- Bulk imports use a **single transaction** for all hands in a file
- `PRAGMA journal_mode=WAL` for concurrent reads during writes
- `PRAGMA synchronous=NORMAL` for better write performance (acceptable for local app)
- Foreign key checking disabled during bulk import, re-enabled after

### 6.2 Read Optimization

- Covering indexes for the most common analytics queries
- Denormalized `hero_net_won` on `hands` table avoids joining `hand_players` for dashboard
- Denormalized `hands_count` and `net_result` on `sessions` avoids counting on every dashboard load
- FTS5 index for hand number search and table name search

### 6.3 Database Maintenance

- `PRAGMA optimize` run on application close
- `VACUUM` offered as a manual operation in settings
- Database file size estimate: ~10–20 MB per 100,000 hands

---

## 7. Data Integrity

### 7.1 Constraints

- `UNIQUE(hand_number, site)` prevents duplicate hand imports
- `UNIQUE(hand_id, player_id)` prevents duplicate player entries per hand
- Foreign keys with `ON DELETE CASCADE` ensure referential integrity
- `NOT NULL` on required fields prevents incomplete data

### 7.2 Application-Level Validation

- Poker engine validates card codes before storage
- Import parser validates hand structure before insertion
- Stake, position, and game type values validated against enums

---

*Next: [Frontend Design](./05-frontend-design.md)*
