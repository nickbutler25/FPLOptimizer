# Fantasy Premier League API Endpoints

**Base URL:** `https://fantasy.premierleague.com/api/`

All endpoints are accessed via `https://fantasy.premierleague.com/api/{endpoint}`

## Public Endpoints (No Authentication Required)

### General Data

#### 1. Bootstrap Static
**Endpoint:** `GET /bootstrap-static/`

**Description:** Core FPL data including all players, teams, gameweeks, and game settings.

**Returns:**
- `events`: All gameweeks with deadlines and stats
- `teams`: All Premier League teams
- `players`: All FPL players with current stats
- `player_types`: Position types (GK, DEF, MID, FWD)
- `phases`: Season phases
- `game_settings`: Game rules and settings

**Example:** `https://fantasy.premierleague.com/api/bootstrap-static/`

---

#### 2. Fixtures
**Endpoint:** `GET /fixtures/`

**Description:** All fixtures for the season.

**Returns:**
- Future fixtures: team info, kickoff times, difficulty ratings
- Past fixtures: team info, statistics (goals, assists, bonus points, etc.)

**Query Parameters:**
- `?event={event_id}` - Filter by specific gameweek

**Examples:**
- All fixtures: `https://fantasy.premierleague.com/api/fixtures/`
- GW 10 fixtures: `https://fantasy.premierleague.com/api/fixtures/?event=10`

---

#### 3. Event Status
**Endpoint:** `GET /event-status/`

**Description:** Current gameweek status including bonus points and league updates.

**Returns:**
- Bonus points being added
- League rankings being updated
- Status of current gameweek

**Example:** `https://fantasy.premierleague.com/api/event-status/`

---

#### 4. Set Piece Notes
**Endpoint:** `GET /team/set-piece-notes/`

**Description:** Information about set piece takers for each Premier League team.

**Returns:**
- Teams with their set piece takers
- Penalty takers
- Free kick takers
- Corner takers

**Example:** `https://fantasy.premierleague.com/api/team/set-piece-notes/`

---

### Player Data

#### 5. Player Summary
**Endpoint:** `GET /element-summary/{player_id}/`

**Description:** Detailed player data including fixtures and history.

**Returns:**
- `fixtures`: Upcoming fixtures with difficulty ratings
- `history`: Current season gameweek-by-gameweek stats
- `history_past`: Previous seasons summary stats

**Example:** `https://fantasy.premierleague.com/api/element-summary/250/`

---

#### 6. Live Gameweek Data
**Endpoint:** `GET /event/{event_id}/live/`

**Description:** Live performance statistics for all players in a specific gameweek.

**Returns:**
- Real-time player stats for the gameweek
- Minutes played
- Goals, assists, bonus points
- ICT stats

**Example:** `https://fantasy.premierleague.com/api/event/10/live/`

---

#### 7. Dream Team
**Endpoint:** `GET /dream-team/{event_id}/`

**Description:** Best performing 11 players for a given gameweek.

**Returns:**
- Top XI formation
- Player IDs and points
- Captain selection

**Example:** `https://fantasy.premierleague.com/api/dream-team/10/`

---

### Manager/Team Data

#### 8. Manager Entry
**Endpoint:** `GET /entry/{manager_id}/`

**Description:** Manager's team summary and overall stats.

**Returns:**
- Manager name and team name
- Overall points and rank
- Current gameweek points and rank
- Team value and bank balance
- Total transfers made
- Favorite team
- Started gameweek

**Example:** `https://fantasy.premierleague.com/api/entry/1881344/`

**Currently Used In:** Your application uses this endpoint to get team data

---

#### 9. Manager History
**Endpoint:** `GET /entry/{manager_id}/history/`

**Description:** Manager's historical performance data.

**Returns:**
- `current`: Gameweek-by-gameweek stats for current season
- `past`: Summary for previous seasons
- `chips`: Chips used and when

**Example:** `https://fantasy.premierleague.com/api/entry/1881344/history/`

---

#### 10. Manager Team Picks
**Endpoint:** `GET /entry/{manager_id}/event/{event_id}/picks/`

**Description:** Manager's team selection for a specific gameweek.

**Returns:**
- `picks`: Array of 15 players with positions
- `entry_history`: Gameweek performance stats
- `automatic_subs`: Auto-substitutions made
- Active chip used

**Example:** `https://fantasy.premierleague.com/api/entry/1881344/event/10/picks/`

**Currently Used In:** Your application uses this endpoint to get team picks

---

#### 11. Manager Transfers
**Endpoint:** `GET /entry/{manager_id}/transfers/`

**Description:** All transfers made by manager in current season.

**Returns:**
- Array of all transfers with dates
- Players transferred in/out
- Transfer cost
- Gameweek of transfer

**Example:** `https://fantasy.premierleague.com/api/entry/1881344/transfers/`

**Currently Implemented In:** Your application has this method but doesn't use it

---

### League Data

#### 12. Classic League Standings
**Endpoint:** `GET /leagues-classic/{league_id}/standings/`

**Description:** Classic league standings and rankings.

**Returns:**
- League information
- Standings with team IDs, names, ranks, and points
- Pagination support

**Query Parameters:**
- `?page_standings=2` - Pagination

**Example:** `https://fantasy.premierleague.com/api/leagues-classic/12345/standings/`

---

#### 13. Head-to-Head League Matches
**Endpoint:** `GET /leagues-h2h-matches/league/{league_id}/`

**Description:** Head-to-head league match data.

**Returns:**
- Match results
- Team scores
- Upcoming fixtures

**Query Parameters:**
- `?page={page_number}` - Pagination
- `?event={event_id}` - Filter by gameweek

**Example:** `https://fantasy.premierleague.com/api/leagues-h2h-matches/league/12345/`

---

#### 14. Cup Status
**Endpoint:** `GET /league/{league_id}/cup-status/`

**Description:** Cup competition status for a league.

**Returns:**
- Cup matches
- Qualification status
- Round information

**Example:** `https://fantasy.premierleague.com/api/league/12345/cup-status/`

---

### Statistics

#### 15. Most Valuable Teams
**Endpoint:** `GET /stats/most-valuable-teams/`

**Description:** Top 5 most valuable FPL teams.

**Returns:**
- Team IDs
- Team values
- Manager names

**Example:** `https://fantasy.premierleague.com/api/stats/most-valuable-teams/`

---

#### 16. Best Leagues
**Endpoint:** `GET /stats/best-leagues/`

**Description:** Best leagues ranked by average score of top players.

**Returns:**
- League information
- Average scores
- Rankings

**Example:** `https://fantasy.premierleague.com/api/stats/best-leagues/`

---

## Authentication Required Endpoints

These endpoints require FPL account authentication and will return **403 Forbidden** without proper credentials:

### 17. My Team
**Endpoint:** `GET /my-team/{manager_id}/`

**Description:** Current team with transfer information **for the authenticated user only**.

**Returns:**
- `transfers`: Object with `limit` (free transfers), `cost`, `made`, `bank`, `value`
- Current team picks
- Chips available

**Example:** `https://fantasy.premierleague.com/api/my-team/1881344/`

**Status:** ❌ **Not accessible without authentication** - Returns 403 Forbidden

**Note:** This endpoint contains the `transfers.limit` field which shows free transfers available, but cannot be accessed publicly.

---

### 18. Latest Transfers
**Endpoint:** `GET /entry/{manager_id}/transfers-latest/`

**Description:** Recent gameweek transfers for authenticated user.

**Status:** ❌ **Requires authentication**

---

### 19. Current User
**Endpoint:** `GET /me/`

**Description:** Authenticated user's manager data.

**Status:** ❌ **Requires authentication**

---

## Endpoints Currently Used in Your Application

### Backend Implementation

Your application currently implements these FPL API endpoints:

1. **`/bootstrap-static/`** - Implemented in `FPLClient.get_bootstrap_static()`
2. **`/entry/{id}/`** - Implemented in `FPLClient.get_entry()` ✅ **Used for team data**
3. **`/entry/{id}/event/{event}/picks/`** - Implemented in `FPLClient.get_entry_picks()` ✅ **Used for team picks**
4. **`/entry/{id}/transfers/`** - Implemented in `FPLClient.get_entry_transfers()` (not currently used)
5. **`/my-team/{id}/`** - Implemented in `FPLClient.get_my_team()` ❌ **Returns 403 - Cannot use**

---

## Notes

- The FPL API is unofficial and not documented by the Premier League
- No authentication is required for most endpoints
- No API key is required (your app's API key is for your own backend, not FPL)
- Rate limiting may apply (though not officially documented)
- Some endpoints require authentication via FPL login cookies
- All responses are in JSON format
- The API may change without notice as it's not an official public API

---

## Potential Additions to Your Application

Based on the available endpoints, you could add:

1. **Player Search/Browse** - Using `/bootstrap-static/` players array
2. **Manager History** - Using `/entry/{id}/history/` to show past performance
3. **League Standings** - Using `/leagues-classic/{id}/standings/`
4. **Fixtures** - Using `/fixtures/` to show upcoming matches
5. **Live Scores** - Using `/event/{id}/live/` for real-time gameweek stats
6. **Player Details** - Using `/element-summary/{player_id}/` for individual player stats
7. **Dream Team** - Using `/dream-team/{event_id}/` to show top performers
8. **Set Piece Takers** - Using `/team/set-piece-notes/` for transfer planning

---

## References

- FPL Website: https://fantasy.premierleague.com
- Community Documentation: https://www.oliverlooney.com/blogs/FPL-APIs-Explained
- API Base URL: https://fantasy.premierleague.com/api/
