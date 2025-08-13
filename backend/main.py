import pandas as pd
import numpy as np
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, value
import requests
import json


class FPLOptimizer:
    def __init__(self):
        """Initialize the FPL optimizer with current season data"""
        self.base_url = "https://fantasy.premierleague.com/api/"
        self.budget = 100.0  # £100m budget
        self.squad_size = 15
        self.team_limit = 3  # Max 3 players from same team

        # Formation constraints
        self.position_constraints = {
            'GKP': {'min': 2, 'max': 2},
            'DEF': {'min': 5, 'max': 5},
            'MID': {'min': 5, 'max': 5},
            'FWD': {'min': 3, 'max': 3}
        }

        # Starting XI constraints
        self.starting_constraints = {
            'GKP': 1,
            'DEF': {'min': 3, 'max': 5},
            'MID': {'min': 2, 'max': 5},
            'FWD': {'min': 1, 'max': 3}
        }

    def fetch_player_data(self):
        """Fetch current player data from FPL API"""
        try:
            response = requests.get(f"{self.base_url}bootstrap-static/")
            data = response.json()

            # Extract player data
            players_df = pd.DataFrame(data['elements'])
            teams_df = pd.DataFrame(data['teams'])
            positions_df = pd.DataFrame(data['element_types'])

            # Merge team names
            players_df = players_df.merge(
                teams_df[['id', 'name', 'short_name']],
                left_on='team',
                right_on='id',
                suffixes=('', '_team')
            )

            # Merge position names
            players_df = players_df.merge(
                positions_df[['id', 'singular_name_short']],
                left_on='element_type',
                right_on='id',
                suffixes=('', '_pos')
            )

            # Clean and prepare data
            players_df['position'] = players_df['singular_name_short']
            players_df['price'] = players_df['now_cost'] / 10  # Convert to millions
            players_df['team_name'] = players_df['short_name']

            # Select relevant columns
            columns = ['id', 'web_name', 'position', 'team_name', 'price',
                       'total_points', 'points_per_game', 'selected_by_percent',
                       'form', 'value_season', 'minutes', 'goals_scored',
                       'assists', 'clean_sheets', 'bonus']

            return players_df[columns]

        except Exception as e:
            print(f"Error fetching data from FPL API: {e}")
            print("Using sample data instead...")
            return self.create_sample_data()

    def create_sample_data(self):
        """Create sample player data for demonstration"""
        np.random.seed(42)

        # Sample teams
        teams = ['ARS', 'CHE', 'LIV', 'MCI', 'MUN', 'TOT', 'NEW', 'BHA']

        # Generate sample players
        players = []
        player_id = 1

        # Generate players for each position
        for pos, count in [('GKP', 16), ('DEF', 40), ('MID', 40), ('FWD', 24)]:
            for i in range(count):
                team = np.random.choice(teams)

                # Price ranges by position
                if pos == 'GKP':
                    price = np.random.uniform(4.0, 6.5)
                elif pos == 'DEF':
                    price = np.random.uniform(4.0, 7.5)
                elif pos == 'MID':
                    price = np.random.uniform(4.5, 13.0)
                else:  # FWD
                    price = np.random.uniform(4.5, 12.5)

                # Generate performance metrics
                if price > 8:  # Premium players
                    points = np.random.uniform(150, 250)
                    form = np.random.uniform(5, 10)
                elif price > 6:  # Mid-range players
                    points = np.random.uniform(100, 180)
                    form = np.random.uniform(3, 7)
                else:  # Budget players
                    points = np.random.uniform(50, 120)
                    form = np.random.uniform(1, 5)

                players.append({
                    'id': player_id,
                    'web_name': f'Player_{player_id}',
                    'position': pos,
                    'team_name': team,
                    'price': round(price, 1),
                    'total_points': int(points),
                    'points_per_game': round(points / 20, 1),
                    'selected_by_percent': round(np.random.uniform(1, 50), 1),
                    'form': round(form, 1),
                    'value_season': round(points / price, 1),
                    'minutes': int(np.random.uniform(500, 2000)),
                    'goals_scored': int(np.random.uniform(0, 20)) if pos != 'GKP' else 0,
                    'assists': int(np.random.uniform(0, 15)),
                    'clean_sheets': int(np.random.uniform(0, 15)) if pos in ['GKP', 'DEF'] else 0,
                    'bonus': int(np.random.uniform(0, 30))
                })
                player_id += 1

        return pd.DataFrame(players)

    def calculate_player_score(self, players_df, weights=None):
        """Calculate composite score for each player"""
        if weights is None:
            weights = {
                'total_points': 0.3,
                'form': 0.25,
                'value_season': 0.2,
                'points_per_game': 0.15,
                'selected_by_percent': 0.1
            }

        # Normalize metrics
        for metric in weights.keys():
            if metric in players_df.columns:
                players_df[f'{metric}_norm'] = (
                        players_df[metric] / players_df[metric].max()
                )

        # Calculate weighted score
        players_df['score'] = sum(
            players_df[f'{metric}_norm'] * weight
            for metric, weight in weights.items()
            if f'{metric}_norm' in players_df.columns
        )

        return players_df

    def optimize_team(self, players_df, formation='4-4-2'):
        """Optimize team selection using linear programming"""
        # Calculate player scores
        players_df = self.calculate_player_score(players_df)

        # Parse formation
        formation_split = formation.split('-')
        n_def = int(formation_split[0])
        n_mid = int(formation_split[1])
        n_fwd = int(formation_split[2])

        # Create optimization problem
        prob = LpProblem("FPL_Team_Selection", LpMaximize)

        # Decision variables
        players_df['selected'] = [
            LpVariable(f"player_{i}", cat='Binary')
            for i in players_df.index
        ]

        players_df['starting'] = [
            LpVariable(f"starting_{i}", cat='Binary')
            for i in players_df.index
        ]

        # Objective: Maximize total score of starting XI
        prob += lpSum([
            players_df.loc[i, 'score'] * players_df.loc[i, 'starting']
            for i in players_df.index
        ])

        # Constraints

        # 1. Budget constraint
        prob += lpSum([
            players_df.loc[i, 'price'] * players_df.loc[i, 'selected']
            for i in players_df.index
        ]) <= self.budget

        # 2. Squad size constraint
        prob += lpSum([
            players_df.loc[i, 'selected']
            for i in players_df.index
        ]) == self.squad_size

        # 3. Position constraints for squad
        for pos, limits in self.position_constraints.items():
            mask = players_df['position'] == pos
            prob += lpSum([
                players_df.loc[i, 'selected']
                for i in players_df[mask].index
            ]) == limits['min']

        # 4. Starting XI constraints
        prob += lpSum([
            players_df.loc[i, 'starting']
            for i in players_df.index
        ]) == 11

        # Starting XI by position
        for pos, count in [('GKP', 1), ('DEF', n_def), ('MID', n_mid), ('FWD', n_fwd)]:
            mask = players_df['position'] == pos
            prob += lpSum([
                players_df.loc[i, 'starting']
                for i in players_df[mask].index
            ]) == count

        # 5. Can only start if selected
        for i in players_df.index:
            prob += players_df.loc[i, 'starting'] <= players_df.loc[i, 'selected']

        # 6. Team limit constraint
        for team in players_df['team_name'].unique():
            mask = players_df['team_name'] == team
            prob += lpSum([
                players_df.loc[i, 'selected']
                for i in players_df[mask].index
            ]) <= self.team_limit

        # Solve
        prob.solve()

        # Extract results
        if LpStatus[prob.status] == 'Optimal':
            players_df['is_selected'] = players_df['selected'].apply(value)
            players_df['is_starting'] = players_df['starting'].apply(value)

            selected_team = players_df[players_df['is_selected'] == 1].copy()
            selected_team['captain'] = False

            # Auto-select captain (highest scoring starter)
            starting_xi = selected_team[selected_team['is_starting'] == 1]
            if len(starting_xi) > 0:
                captain_idx = starting_xi['score'].idxmax()
                selected_team.loc[captain_idx, 'captain'] = True

            return selected_team, prob.objective.value()
        else:
            return None, None

    def display_team(self, team_df):
        """Display the optimized team in a formatted way"""
        if team_df is None:
            print("No optimal team found!")
            return

        print("\n" + "=" * 60)
        print("OPTIMIZED FANTASY PREMIER LEAGUE TEAM")
        print("=" * 60)

        total_cost = team_df['price'].sum()
        print(f"\nTotal Cost: £{total_cost:.1f}m")
        print(f"Remaining Budget: £{self.budget - total_cost:.1f}m")

        # Starting XI
        print("\n--- STARTING XI ---")
        starting = team_df[team_df['is_starting'] == 1].sort_values(
            ['position', 'score'], ascending=[True, False]
        )

        for pos in ['GKP', 'DEF', 'MID', 'FWD']:
            print(f"\n{pos}:")
            pos_players = starting[starting['position'] == pos]
            for _, player in pos_players.iterrows():
                captain_mark = " (C)" if player['captain'] else ""
                print(f"  {player['web_name']:<15} {player['team_name']:<4} "
                      f"£{player['price']:.1f}m  {player['total_points']:>3}pts  "
                      f"Form: {player['form']:.1f}{captain_mark}")

        # Bench
        print("\n--- BENCH ---")
        bench = team_df[team_df['is_starting'] == 0].sort_values(
            ['position', 'score'], ascending=[True, False]
        )

        for _, player in bench.iterrows():
            print(f"  {player['web_name']:<15} {player['team_name']:<4} "
                  f"£{player['price']:.1f}m  {player['total_points']:>3}pts  "
                  f"Form: {player['form']:.1f}")

        # Team distribution
        print("\n--- TEAM DISTRIBUTION ---")
        team_counts = team_df.groupby('team_name').size().sort_values(ascending=False)
        for team, count in team_counts.items():
            print(f"  {team}: {count} players")

        print("\n" + "=" * 60)


# Example usage
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = FPLOptimizer()

    # Fetch player data (will use sample data if API fails)
    print("Fetching player data...")
    players_df = optimizer.fetch_player_data()
    print(f"Loaded {len(players_df)} players")

    # Optimize team with different formations
    formations = ['4-4-2', '4-3-3', '3-5-2', '3-4-3', '5-3-2']

    best_team = None
    best_score = -1
    best_formation = None

    print("\nOptimizing team selection...")
    for formation in formations:
        print(f"\nTrying formation: {formation}")
        team, score = optimizer.optimize_team(players_df, formation)

        if team is not None and score > best_score:
            best_team = team
            best_score = score
            best_formation = formation
            print(f"  New best score: {score:.2f}")

    print(f"\nBest formation: {best_formation}")
    optimizer.display_team(best_team)

    # Export team to CSV
    if best_team is not None:
        best_team.to_csv('optimized_fpl_team.csv', index=False)
        print("\nTeam exported to 'optimized_fpl_team.csv'")