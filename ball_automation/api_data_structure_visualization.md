# ESPN Soccer API Data Structure Visualization
## Scottish Premiership Scoreboard

```
ESPN_API_RESPONSE
│
├── 📋 leagues[] (Array of League Objects)
│   │
│   └── League
│       ├── id: "735"
│       ├── uid: "s:600~l:735"
│       ├── name: "Scottish Premiership"
│       ├── abbreviation: "SPFL Premiership"
│       ├── midsizeName: "SCO.1"
│       ├── slug: "sco.1"
│       │
│       ├── 🗓️ season
│       │   ├── year: 2026
│       │   ├── startDate: "2026-06-01T04:00Z"
│       │   ├── endDate: "2027-06-01T03:59Z"
│       │   ├── displayName: "2026-27 Scottish Premiership"
│       │   └── type
│       │       ├── id: "1"
│       │       ├── type: 14300
│       │       ├── name: "First Phase"
│       │       └── abbreviation: "First Phase"
│       │
│       ├── 🎨 logos[] (Multiple logo variations)
│       │   ├── href: URL
│       │   ├── width: 500
│       │   ├── height: 500
│       │   ├── rel: ["full", "default"] or ["full", "dark"]
│       │   └── lastUpdated: timestamp
│       │
│       ├── calendarType: "day"
│       ├── calendarIsWhitelist: true
│       ├── calendarStartDate: "2026-06-01T04:00Z"
│       ├── calendarEndDate: "2027-06-01T03:59Z"
│       │
│       └── 📅 calendar[] (Array of match dates)
│           └── "2026-07-31T07:00Z", "2026-08-01T07:00Z", ...
│
├── 🏟️ season
│   ├── type: 14300
│   └── year: 2026
│
├── 📆 day
│   └── date: "2026-11-28"
│
└── 🎮 events[] (Array of Match Events)
    │
    └── Event (Match)
        ├── id: "401878332"
        ├── uid: "s:600~l:735~e:401878332"
        ├── date: "2026-11-28T15:00Z"
        ├── name: "Dundee at Aberdeen"
        ├── shortName: "DUN @ ABE"
        │
        ├── 🏆 season
        │   ├── year: 2026
        │   ├── type: 14300
        │   └── slug: "first-phase"
        │
        ├── 🎯 competitions[] (Array of Competition Details)
        │   │
        │   └── Competition
        │       ├── id: "401878332"
        │       ├── uid: "s:600~l:735~e:401878332~c:401878332"
        │       ├── date: "2026-11-28T15:00Z"
        │       ├── startDate: "2026-11-28T15:00Z"
        │       ├── attendance: 0
        │       ├── timeValid: true
        │       ├── recent: false
        │       │
        │       ├── 📊 status
        │       │   ├── clock: 0.0
        │       │   ├── displayClock: "0'"
        │       │   └── type
        │       │       ├── id: "1"
        │       │       ├── name: "STATUS_SCHEDULED"
        │       │       ├── state: "pre"
        │       │       ├── completed: false
        │       │       ├── description: "Scheduled"
        │       │       ├── detail: "Sat, November 28th at 10:00 AM EST"
        │       │       └── shortDetail: "Scheduled"
        │       │
        │       ├── 🏟️ venue
        │       │   ├── id: "234"
        │       │   ├── fullName: "Pittodrie Stadium"
        │       │   └── address
        │       │       ├── city: "Aberdeen"
        │       │       └── country: "Scotland"
        │       │
        │       ├── 📐 format
        │       │   └── regulation
        │       │       └── periods: 2
        │       │
        │       ├── altGameNote: "SPFL Premiership"
        │       ├── notes: []
        │       ├── geoBroadcasts: []
        │       ├── broadcasts: []
        │       ├── broadcast: ""
        │       │
        │       ├── ⚽ competitors[] (Home and Away Teams)
        │       │   │
        │       │   ├── Competitor (Home Team)
        │       │   │   ├── id: "263"
        │       │   │   ├── uid: "s:600~t:263"
        │       │   │   ├── type: "team"
        │       │   │   ├── order: 0
        │       │   │   ├── homeAway: "home"
        │       │   │   ├── winner: false
        │       │   │   ├── form: "DWLLL"
        │       │   │   ├── score: "0"
        │       │   │   │
        │       │   │   ├── 📈 records[]
        │       │   │   │   └── Record
        │       │   │   │       ├── name: "All Splits"
        │       │   │   │       ├── type: "total"
        │       │   │   │       ├── summary: "4-2-8"
        │       │   │   │       └── abbreviation: "Total"
        │       │   │   │
        │       │   │   ├── 🎪 team
        │       │   │   │   ├── id: "263"
        │       │   │   │   ├── uid: "s:600~t:263"
        │       │   │   │   ├── abbreviation: "ABE"
        │       │   │   │   ├── displayName: "Aberdeen"
        │       │   │   │   ├── shortDisplayName: "Aberdeen"
        │       │   │   │   ├── name: "Aberdeen"
        │       │   │   │   ├── location: "Aberdeen"
        │       │   │   │   ├── color: "C8142F"
        │       │   │   │   ├── alternateColor: "f9e900"
        │       │   │   │   ├── isActive: true
        │       │   │   │   ├── logo: "https://a.espncdn.com/i/teamlogos/soccer/500/263.png"
        │       │   │   │   │
        │       │   │   │   └── 🔗 links[] (Team Resources)
        │       │   │   │       ├── Clubhouse
        │       │   │   │       ├── Stats
        │       │   │   │       ├── Schedule
        │       │   │   │       └── Squad
        │       │   │   │
        │       │   │   ├── statistics: []
        │       │   │   │
        │       │   │   └── 👥 leaders[] (Top Performers)
        │       │   │       │
        │       │   │       ├── Leader (Goals)
        │       │   │       │   ├── name: "goals"
        │       │   │       │   ├── displayName: "Goals"
        │       │   │       │   ├── abbreviation: "G"
        │       │   │       │   │
        │       │   │       │   └── leaders[]
        │       │   │       │       └── Athlete Leader
        │       │   │       │           ├── displayValue: "6"
        │       │   │       │           ├── value: 6.0
        │       │   │       │           │
        │       │   │       │           ├── 🏃 athlete
        │       │   │       │           │   ├── id: "223369"
        │       │   │       │           │   ├── displayName: "Kevin Nisbet"
        │       │   │       │           │   ├── shortName: "K. Nisbet"
        │       │   │       │           │   ├── fullName: "Kevin Nisbet"
        │       │   │       │           │   ├── jersey: "15"
        │       │   │       │           │   ├── active: true
        │       │   │       │           │   │
        │       │   │       │           │   ├── team
        │       │   │       │           │   │   └── id: "263"
        │       │   │       │           │   │
        │       │   │       │           │   ├── 🔗 links[]
        │       │   │       │           │   │   └── Player Card
        │       │   │       │           │   │
        │       │   │       │           │   └── 📍 position
        │       │   │       │           │       └── abbreviation: "F"
        │       │   │       │           │
        │       │   │       │           └── team
        │       │   │       │               └── id: "263"
        │       │   │       │
        │       │   │       └── Leader (Goals - Duplicate)
        │       │   │           └── [Same structure as above]
        │       │   │
        │       │   └── Competitor (Away Team)
        │       │       └── [Same structure as Home Team]
        │       │
        │       ├── details: []
        │       │
        │       ├── 💰 odds[] (Betting Information)
        │       │   │
        │       │   └── Odd
        │       │       ├── overUnder: 2.5
        │       │       │
        │       │       ├── link
        │       │       │   ├── language: "en-US"
        │       │       │   ├── rel: ["game", "desktop", "bets"]
        │       │       │   ├── href: Betting URL
        │       │       │   ├── text: "Game"
        │       │       │   ├── isExternal: true
        │       │       │   ├── isPremium: false
        │       │       │   └── isHidden: false
        │       │       │
        │       │       ├── provider
        │       │       │   ├── id: "100"
        │       │       │   ├── name: "DraftKings"
        │       │       │   ├── priority: 1
        │       │       │   ├── displayName: "DraftKings"
        │       │       │   └── logos[]
        │       │       │
        │       │       ├── drawOdds
        │       │       │   ├── moneyLine: 280
        │       │       │   └── link (Draw Bet)
        │       │       │
        │       │       ├── total (Over/Under)
        │       │       │   ├── displayName: "Total"
        │       │       │   ├── shortDisplayName: "Total"
        │       │       │   ├── over
        │       │       │   │   ├── open
        │       │       │   │   │   ├── line: "o2.5"
        │       │       │   │   │   └── odds: "-170"
        │       │       │   │   └── close
        │       │       │   │       ├── line: "o2.5"
        │       │       │   │       └── odds: "-165"
        │       │       │   └── under
        │       │       │       ├── open
        │       │       │       │   ├── line: "u2.5"
        │       │       │       │   └── odds: "+115"
        │       │       │       └── close
        │       │       │           ├── line: "u2.5"
        │       │       │           └── odds: "+120"
        │       │       │
        │       │       ├── pointSpread (Home/Away)
        │       │       │   └── [Similar structure to total]
        │       │       │
        │       │       └── moneyline
        │       │           ├── displayName: "Moneyline"
        │       │           ├── home
        │       │           ├── away
        │       │           └── draw
        │       │
        │       ├── wasSuspended: false
        │       ├── playByPlayAvailable: true
        │       └── playByPlayAthletes: true
        │
        ├── status (Match Status Summary)
        │   └── [Same as competition status]
        │
        ├── 🏟️ venue (Venue Summary)
        │   └── displayName: "Pittodrie Stadium"
        │
        └── 🔗 links[] (Match Resources)
            └── Summary Link
                ├── language: "en-US"
                ├── rel: ["summary", "desktop", "event"]
                └── href: "https://www.espn.com/soccer/match/_/gameId/401878332/..."
```

## Data Structure Summary

### Root Level Keys:
| Key | Type | Description |
|-----|------|-------------|
| `leagues` | Array | Contains league information and metadata |
| `season` | Object | Current season info |
| `day` | Object | Current day/date information |
| `events` | Array | Array of match/event objects |

### League Object Contains:
- League identification (id, uid, name, abbreviation)
- Season details with start/end dates
- Logo resources (full size, dark mode variants)
- Calendar: Array of scheduled match dates
- Match schedule metadata

### Event (Match) Object Contains:
- Match identifiers and metadata
- Competitor array (home and away teams)
- Competition details including:
  - Match status (scheduled, in progress, final)
  - Venue information
  - Betting odds from multiple providers
  - Team records and statistics
  - Top performers/leaders

### Competitor (Team) Object Contains:
- Team identification and branding
  - Team colors (primary and alternate)
  - Team logo URL
  - Team abbreviation and full name
- Team resources (links to clubhouse, stats, squad, schedule)
- Current season record (wins, draws, losses)
- Top scorers and leaders
- Form string (recent match results: W/D/L)

### Key Betting Information:
- **Moneyline**: Win/Loss odds for home, away, and draw
- **Point Spread**: Handicap betting options
- **Over/Under**: Total goals betting
- Multiple providers available (DraftKings shown)
- Both opening and closing odds included

## Data Types Used:

| Type | Examples |
|------|----------|
| **Status Types** | SCHEDULED, IN_PROGRESS, FINAL, SUSPENDED |
| **Team Reference** | home, away |
| **Record Types** | "Total", "All Splits" (W-D-L format) |
| **Timestamps** | ISO 8601 format (UTC) |
| **Numerical** | Scores, odds, counts as strings or numbers |
| **Boolean** | timeValid, isActive, completed, isExternal |

## Common Use Cases:

1. **Display Match Scoreboard**: Extract event name, status, score, teams
2. **Team Analytics**: Access records, form string, top players
3. **Betting Integration**: Use odds objects for sportsbook links
4. **Schedule Navigation**: Use calendar array and events
5. **Team Information**: Access team colors, logos, links for branding
6. **Player Statistics**: Access leaders array for top performers
