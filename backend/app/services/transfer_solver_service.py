"""Transfer solver service using CVXPY for optimizing FPL transfers."""

import logging
from typing import Dict, List, Optional
import cvxpy as cp
import numpy as np

from app.services.expected_points_service import ExpectedPointsService
from app.services.player_service import PlayerService
from app.models.player import Player
from app.models.team_pick import TeamPick

logger = logging.getLogger(__name__)


class TransferSolution:
    """Result of transfer optimization."""

    def __init__(
        self,
        gameweek: int,
        transfers_in: List[Dict],
        transfers_out: List[Dict],
        expected_points: float,
        transfer_cost: int,
        free_transfers_used: int,
        free_transfers_remaining: int,
    ):
        """Initialize transfer solution.

        Args:
            gameweek: Gameweek number (offset from current, 0-indexed)
            transfers_in: List of player IDs and names being transferred in
            transfers_out: List of player IDs and names being transferred out
            expected_points: Expected points for this gameweek
            transfer_cost: Points penalty for paid transfers
            free_transfers_used: Number of free transfers used
            free_transfers_remaining: Free transfers remaining after this gameweek
        """
        self.gameweek = gameweek
        self.transfers_in = transfers_in
        self.transfers_out = transfers_out
        self.expected_points = expected_points
        self.transfer_cost = transfer_cost
        self.free_transfers_used = free_transfers_used
        self.free_transfers_remaining = free_transfers_remaining


class TransferPlan:
    """Complete N-week transfer plan."""

    def __init__(
        self,
        weekly_solutions: List[TransferSolution],
        total_expected_points: float,
        total_transfer_cost: int,
        current_expected_points: float,
    ):
        """Initialize transfer plan.

        Args:
            weekly_solutions: List of weekly transfer solutions
            total_expected_points: Total expected points across all weeks (after transfer costs)
            total_transfer_cost: Total points penalty from all transfers
            current_expected_points: Expected points with current squad (no transfers)
        """
        self.weekly_solutions = weekly_solutions
        self.total_expected_points = total_expected_points
        self.total_transfer_cost = total_transfer_cost
        self.current_expected_points = current_expected_points
        self.improvement = total_expected_points - current_expected_points


class TransferSolverService:
    """Service for optimizing FPL transfers using CVXPY."""

    # Squad constraints
    SQUAD_SIZE = 15
    STARTING_XI_SIZE = 11
    NUM_GK = 2
    NUM_DEF = 5
    NUM_MID = 5
    NUM_FWD = 3
    MAX_PLAYERS_PER_TEAM = 3

    # Valid formations: (GK, DEF, MID, FWD)
    VALID_FORMATIONS = [
        (1, 3, 4, 3),
        (1, 3, 5, 2),
        (1, 4, 3, 3),
        (1, 4, 4, 2),
        (1, 4, 5, 1),
        (1, 5, 3, 2),
        (1, 5, 4, 1),
    ]

    # Transfer rules
    TRANSFER_PENALTY = 4  # Points deducted per paid transfer
    FREE_TRANSFERS_PER_WEEK = 1
    MAX_FREE_TRANSFERS = 5

    def __init__(
        self,
        expected_points_service: ExpectedPointsService,
        player_service: PlayerService,
    ):
        """Initialize transfer solver service.

        Args:
            expected_points_service: Service for calculating expected points
            player_service: Service for player data
        """
        self.expected_points_service = expected_points_service
        self.player_service = player_service

    async def solve_transfers(
        self,
        current_squad: List[TeamPick],
        num_gameweeks: int = 5,
        free_transfers: int = 3,
        budget: float = 100.0,
        discount_factor: float = 0.9,
    ) -> TransferPlan:
        """Solve optimal transfers for N gameweeks.

        Args:
            current_squad: Current squad of 15 players
            num_gameweeks: Number of gameweeks to optimize (default 5)
            free_transfers: Current number of free transfers available (default 3)
            budget: Total budget in millions (default 100.0)
            discount_factor: Discount factor for future gameweeks (default 0.9)

        Returns:
            Complete transfer plan with weekly recommendations
        """
        logger.info(
            f"Starting transfer optimization for {num_gameweeks} gameweeks, "
            f"{free_transfers} free transfers, £{budget}m budget"
        )

        # Get all players and expected points
        all_players = await self.player_service.get_all_players()
        logger.info(f"Retrieved {len(all_players)} players from database")

        # Get expected points for next N gameweeks
        expected_points_map = await self.expected_points_service.calculate_expected_points_next_n_gameweeks(
            num_gameweeks
        )

        # Create player lookup
        player_lookup = {p.id: p for p in all_players}

        # Extract current squad player IDs
        current_squad_ids = [pick.element for pick in current_squad]

        # Calculate selling prices for current squad
        selling_prices = self._calculate_selling_prices(current_squad, player_lookup)

        # Calculate available budget including bank and selling prices
        total_available_budget = self._calculate_total_budget(
            current_squad, selling_prices, budget
        )

        logger.info(f"Total available budget: £{total_available_budget:.1f}m")

        # Build optimization model
        solution = self._solve_cvxpy_model(
            all_players=all_players,
            expected_points_map=expected_points_map,
            current_squad_ids=current_squad_ids,
            selling_prices=selling_prices,
            total_budget=total_available_budget,
            num_gameweeks=num_gameweeks,
            initial_free_transfers=free_transfers,
            discount_factor=discount_factor,
        )

        # Extract transfer plan from solution
        transfer_plan = self._extract_transfer_plan(
            solution=solution,
            all_players=all_players,
            expected_points_map=expected_points_map,
            current_squad_ids=current_squad_ids,
            num_gameweeks=num_gameweeks,
            initial_free_transfers=free_transfers,
        )

        logger.info(
            f"Optimization complete. Total improvement: {transfer_plan.improvement:.1f} points"
        )

        return transfer_plan

    def _calculate_selling_prices(
        self, current_squad: List[TeamPick], player_lookup: Dict[int, Player]
    ) -> Dict[int, float]:
        """Calculate selling price for each player in current squad.

        FPL rules:
        - If player price increased: sell at purchase price + half of profit
        - If player price decreased: sell at current price (full loss)

        Args:
            current_squad: Current squad picks
            player_lookup: Dictionary of all players

        Returns:
            Dictionary mapping player ID to selling price in millions
        """
        selling_prices = {}

        for pick in current_squad:
            player_id = pick.element
            player = player_lookup.get(player_id)

            if not player:
                logger.warning(f"Player {player_id} not found in player lookup")
                selling_prices[player_id] = 0.0
                continue

            current_price = player.now_cost / 10.0  # Convert to millions
            purchase_price = (pick.purchase_price or player.now_cost) / 10.0

            if current_price >= purchase_price:
                # Half profit rule
                profit = current_price - purchase_price
                selling_price = purchase_price + (profit / 2.0)
            else:
                # Full loss
                selling_price = current_price

            selling_prices[player_id] = selling_price

        return selling_prices

    def _calculate_total_budget(
        self,
        current_squad: List[TeamPick],
        selling_prices: Dict[int, float],
        bank: float,
    ) -> float:
        """Calculate total available budget including bank and all player values.

        Args:
            current_squad: Current squad picks
            selling_prices: Selling price for each player
            bank: Money in bank (in millions)

        Returns:
            Total budget in millions
        """
        total = bank

        for pick in current_squad:
            player_id = pick.element
            total += selling_prices.get(player_id, 0.0)

        return total

    def _solve_cvxpy_model(
        self,
        all_players: List[Player],
        expected_points_map: Dict[int, List[float]],
        current_squad_ids: List[int],
        selling_prices: Dict[int, float],
        total_budget: float,
        num_gameweeks: int,
        initial_free_transfers: int,
        discount_factor: float,
    ) -> Dict:
        """Solve CVXPY optimization model.

        Args:
            all_players: All available players
            expected_points_map: Expected points per gameweek for each player
            current_squad_ids: Current squad player IDs
            selling_prices: Selling prices for current squad
            total_budget: Total budget in millions
            num_gameweeks: Number of gameweeks
            initial_free_transfers: Starting free transfers
            discount_factor: Discount factor for future gameweeks

        Returns:
            Solution dictionary with decision variables
        """
        logger.info("Building CVXPY optimization model...")

        num_players = len(all_players)
        player_ids = [p.id for p in all_players]
        player_id_to_idx = {pid: idx for idx, pid in enumerate(player_ids)}

        # Player attributes as numpy arrays
        player_costs = np.array([p.now_cost / 10.0 for p in all_players])  # in millions
        player_teams = np.array([p.team for p in all_players])
        player_positions = np.array([p.element_type for p in all_players])  # 1=GK, 2=DEF, 3=MID, 4=FWD

        # Expected points matrix: (num_players x num_gameweeks)
        expected_points_matrix = np.zeros((num_players, num_gameweeks))
        for player in all_players:
            idx = player_id_to_idx[player.id]
            points_list = expected_points_map.get(player.id, [0.0] * num_gameweeks)
            expected_points_matrix[idx, :] = points_list[:num_gameweeks]

        # Discount factors for each gameweek
        discount_factors = np.array([discount_factor ** gw for gw in range(num_gameweeks)])

        # Current squad binary vector
        current_squad_vector = np.zeros(num_players)
        for pid in current_squad_ids:
            if pid in player_id_to_idx:
                current_squad_vector[player_id_to_idx[pid]] = 1

        # Decision variables
        # squad[i, t] = 1 if player i is in squad at gameweek t
        squad = cp.Variable((num_players, num_gameweeks), boolean=True)

        # starting[i, t] = 1 if player i starts at gameweek t
        starting = cp.Variable((num_players, num_gameweeks), boolean=True)

        # transfers_in[i, t] = 1 if player i is transferred in at gameweek t
        transfers_in = cp.Variable((num_players, num_gameweeks), boolean=True)

        # transfers_out[i, t] = 1 if player i is transferred out at gameweek t
        transfers_out = cp.Variable((num_players, num_gameweeks), boolean=True)

        # free_transfers_remaining[t] = number of free transfers available at gameweek t
        free_transfers_remaining = cp.Variable(num_gameweeks + 1, integer=True)

        # paid_transfers[t] = number of paid transfers at gameweek t
        paid_transfers = cp.Variable(num_gameweeks, integer=True)

        # Constraints
        constraints = []

        # Initial squad constraint
        constraints.append(squad[:, 0] == current_squad_vector)

        # Initial free transfers
        constraints.append(free_transfers_remaining[0] == initial_free_transfers)

        # Squad evolution constraints
        for t in range(num_gameweeks):
            if t > 0:
                # Squad continuity: squad[t] = squad[t-1] + transfers_in[t] - transfers_out[t]
                constraints.append(
                    squad[:, t] == squad[:, t - 1] + transfers_in[:, t] - transfers_out[:, t]
                )

            # Squad size
            constraints.append(cp.sum(squad[:, t]) == self.SQUAD_SIZE)

            # Position constraints
            constraints.append(cp.sum(squad[:, t] * (player_positions == 1)) == self.NUM_GK)
            constraints.append(cp.sum(squad[:, t] * (player_positions == 2)) == self.NUM_DEF)
            constraints.append(cp.sum(squad[:, t] * (player_positions == 3)) == self.NUM_MID)
            constraints.append(cp.sum(squad[:, t] * (player_positions == 4)) == self.NUM_FWD)

            # Max players per team
            for team_id in range(1, 21):  # 20 Premier League teams
                constraints.append(
                    cp.sum(squad[:, t] * (player_teams == team_id)) <= self.MAX_PLAYERS_PER_TEAM
                )

            # Starting XI constraints
            constraints.append(cp.sum(starting[:, t]) == self.STARTING_XI_SIZE)
            constraints.append(starting[:, t] <= squad[:, t])  # Can only start if in squad

            # Starting XI position constraints (at least one valid formation)
            # We'll use a simplified constraint: require minimum players per position
            constraints.append(cp.sum(starting[:, t] * (player_positions == 1)) == 1)  # Exactly 1 GK
            constraints.append(cp.sum(starting[:, t] * (player_positions == 2)) >= 3)  # At least 3 DEF
            constraints.append(cp.sum(starting[:, t] * (player_positions == 4)) >= 1)  # At least 1 FWD

            # Transfer constraints
            num_transfers = cp.sum(transfers_in[:, t])
            constraints.append(cp.sum(transfers_out[:, t]) == num_transfers)  # Equal in/out

            # CRITICAL: Can only transfer out players currently in squad
            if t > 0:
                constraints.append(transfers_out[:, t] <= squad[:, t - 1])
            else:
                # First gameweek - can only transfer out players from initial squad
                constraints.append(transfers_out[:, t] <= current_squad_vector)

            # CRITICAL: Can only transfer in players NOT in squad
            if t > 0:
                constraints.append(transfers_in[:, t] <= 1 - squad[:, t - 1])
            else:
                constraints.append(transfers_in[:, t] <= 1 - current_squad_vector)

            # Position balance: transfers in/out must maintain position counts
            # For each position, transfers_in for that position == transfers_out for that position
            for position in range(1, 5):  # 1=GK, 2=DEF, 3=MID, 4=FWD
                constraints.append(
                    cp.sum(transfers_in[:, t] * (player_positions == position)) ==
                    cp.sum(transfers_out[:, t] * (player_positions == position))
                )

            # Free transfer mechanics (reformulated for MILP)
            # Constraints for paid transfers: paid = max(0, num_transfers - free_available)
            if t > 0:
                free_available = free_transfers_remaining[t - 1]
            else:
                free_available = initial_free_transfers

            # paid_transfers[t] >= 0
            constraints.append(paid_transfers[t] >= 0)
            # paid_transfers[t] >= num_transfers - free_available
            constraints.append(paid_transfers[t] >= num_transfers - free_available)
            # paid_transfers[t] <= num_transfers (can't pay more than total transfers)
            constraints.append(paid_transfers[t] <= num_transfers)

            # Free transfers remaining constraints
            # free_remaining[t] = min(MAX, free_available - num_transfers + free_available + 1)
            # Simplified: free_remaining[t] = free_available + 1 - min(num_transfers, free_available)
            # Which equals: free_available + 1 - num_transfers + paid_transfers[t]

            if t < num_gameweeks:  # Not the last week
                # Calculate: new_free = free_available + 1 - (num_transfers - paid_transfers)
                # Which simplifies to: new_free = free_available + 1 - num_transfers + paid_transfers
                constraints.append(
                    free_transfers_remaining[t] == free_available + self.FREE_TRANSFERS_PER_WEEK - num_transfers + paid_transfers[t]
                )
                # Cap at maximum
                constraints.append(free_transfers_remaining[t] <= self.MAX_FREE_TRANSFERS)
                constraints.append(free_transfers_remaining[t] >= 0)

        # Budget constraint (total cost of any squad must not exceed total budget)
        for t in range(num_gameweeks):
            constraints.append(cp.sum(squad[:, t] * player_costs) <= total_budget)

        # Objective: Maximize discounted expected points minus transfer penalties
        # Also add small value for having banked free transfers (flexibility bonus)
        total_points = 0
        FT_FLEXIBILITY_VALUE = 0.5  # Small bonus per banked FT (encourages saving when marginal gains)

        for t in range(num_gameweeks):
            # Expected points from starting XI
            gameweek_points = cp.sum(starting[:, t] * expected_points_matrix[:, t])

            # Transfer penalty
            transfer_penalty = self.TRANSFER_PENALTY * paid_transfers[t]

            # Flexibility bonus: small linear bonus for banked FTs
            # This encourages saving FTs when the transfer gain is small
            # Only apply to weeks before the last (no value in saving FTs at the end)
            if t < num_gameweeks - 1:
                # Bonus for each FT above 1 (having 2 FT = +0.5 points, 3 FT = +1.0 points, etc.)
                ft_bonus = FT_FLEXIBILITY_VALUE * cp.maximum(0, free_transfers_remaining[t] - 1)
                total_points += discount_factors[t] * (gameweek_points - transfer_penalty + ft_bonus)
            else:
                # Last week - no bonus for saving FTs
                total_points += discount_factors[t] * (gameweek_points - transfer_penalty)

        objective = cp.Maximize(total_points)

        # Solve
        problem = cp.Problem(objective, constraints)
        logger.info("Solving optimization problem...")

        # Get list of available solvers
        try:
            from cvxpy import installed_solvers
            available_solvers = installed_solvers()
            logger.info(f"Available solvers: {available_solvers}")
        except:
            available_solvers = []

        # Try multiple solvers in order of preference
        solvers_to_try = []

        # Add solvers that are actually installed
        if cp.GLPK_MI in available_solvers or "GLPK_MI" in available_solvers:
            solvers_to_try.append((cp.GLPK_MI, "GLPK_MI"))
        if cp.CBC in available_solvers or "CBC" in available_solvers:
            solvers_to_try.append((cp.CBC, "CBC"))
        if cp.SCIP in available_solvers or "SCIP" in available_solvers:
            solvers_to_try.append((cp.SCIP, "SCIP"))
        if cp.ECOS_BB in available_solvers or "ECOS_BB" in available_solvers:
            solvers_to_try.append((cp.ECOS_BB, "ECOS_BB"))

        # Always try default solver as fallback
        if not solvers_to_try:
            logger.warning("No specific solvers found, trying default solver")
            solvers_to_try.append((None, "DEFAULT"))

        solved = False
        last_error = None

        for solver, solver_name in solvers_to_try:
            try:
                logger.info(f"Trying solver: {solver_name}")
                if solver is None:
                    # Try default solver
                    problem.solve(verbose=False)
                else:
                    problem.solve(solver=solver, verbose=False)

                if problem.status in ["optimal", "optimal_inaccurate"]:
                    logger.info(f"✓ Solved with {solver_name}! Status: {problem.status}, Value: {problem.value}")
                    solved = True
                    break
                else:
                    logger.warning(f"Solver {solver_name} finished with status: {problem.status}")
                    last_error = f"Solver {solver_name} status: {problem.status}"
            except Exception as e:
                logger.warning(f"Solver {solver_name} failed: {e}")
                last_error = str(e)
                continue

        if not solved:
            error_msg = (
                f"No suitable CVXPY solver found or all solvers failed. "
                f"Available solvers: {available_solvers}. "
                f"Please ensure dependencies are properly installed:\n"
                "  pip install cvxpy numpy\n"
                "For mixed-integer problems, install:\n"
                "  pip install cvxopt\n"
                "Or for better performance:\n"
                "  conda install -c conda-forge glpk\n"
                f"Last error: {last_error}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Return solution
        return {
            "squad": squad.value,
            "starting": starting.value,
            "transfers_in": transfers_in.value,
            "transfers_out": transfers_out.value,
            "free_transfers_remaining": free_transfers_remaining.value,
            "paid_transfers": paid_transfers.value,
            "player_ids": player_ids,
            "expected_points_matrix": expected_points_matrix,
            "discount_factors": discount_factors,
        }

    def _extract_transfer_plan(
        self,
        solution: Dict,
        all_players: List[Player],
        expected_points_map: Dict[int, List[float]],
        current_squad_ids: List[int],
        num_gameweeks: int,
        initial_free_transfers: int,
    ) -> TransferPlan:
        """Extract transfer plan from CVXPY solution.

        Args:
            solution: CVXPY solution dictionary
            all_players: All players
            expected_points_map: Expected points map
            current_squad_ids: Current squad IDs
            num_gameweeks: Number of gameweeks
            initial_free_transfers: Initial free transfers

        Returns:
            Transfer plan with weekly solutions
        """
        player_lookup = {p.id: p for p in all_players}
        player_ids = solution["player_ids"]

        weekly_solutions = []
        total_transfer_cost = 0
        total_expected_points = 0

        free_transfers = initial_free_transfers

        for t in range(num_gameweeks):
            # Extract transfers
            transfers_in_indices = np.where(solution["transfers_in"][:, t] > 0.5)[0]
            transfers_out_indices = np.where(solution["transfers_out"][:, t] > 0.5)[0]

            transfers_in_list = []
            for idx in transfers_in_indices:
                player_id = player_ids[idx]
                player = player_lookup[player_id]
                transfers_in_list.append({
                    "player_id": player_id,
                    "player_name": player.web_name,
                    "position": player.position,
                    "position_id": player.element_type,  # For sorting: 1=GK, 2=DEF, 3=MID, 4=FWD
                    "cost": player.now_cost / 10.0,
                })

            transfers_out_list = []
            for idx in transfers_out_indices:
                player_id = player_ids[idx]
                player = player_lookup[player_id]
                transfers_out_list.append({
                    "player_id": player_id,
                    "player_name": player.web_name,
                    "position": player.position,
                    "position_id": player.element_type,  # For sorting: 1=GK, 2=DEF, 3=MID, 4=FWD
                })

            # Sort by position (GK → DEF → MID → FWD)
            transfers_in_list.sort(key=lambda x: x["position_id"])
            transfers_out_list.sort(key=lambda x: x["position_id"])

            # Remove position_id before storing (only needed for sorting)
            for transfer in transfers_in_list:
                del transfer["position_id"]
            for transfer in transfers_out_list:
                del transfer["position_id"]

            # Calculate expected points for this gameweek
            starting_indices = np.where(solution["starting"][:, t] > 0.5)[0]
            gameweek_expected_points = sum(
                solution["expected_points_matrix"][idx, t] for idx in starting_indices
            )

            # Transfer costs
            num_transfers = len(transfers_in_list)
            free_used = min(num_transfers, free_transfers)
            paid = max(0, num_transfers - free_used)
            transfer_cost = paid * self.TRANSFER_PENALTY

            # Update free transfers
            # Calculate what's left AFTER this gameweek's transfers
            if num_transfers > 0:
                # Made transfers: remaining = current - used
                free_transfers_remaining_this_week = free_transfers - free_used
            else:
                # No transfers: keep current amount
                free_transfers_remaining_this_week = free_transfers

            # For NEXT gameweek planning, add 1 FT (capped at max)
            free_transfers = min(self.MAX_FREE_TRANSFERS, max(1, free_transfers_remaining_this_week + 1))

            # Track totals
            total_transfer_cost += transfer_cost
            total_expected_points += solution["discount_factors"][t] * (gameweek_expected_points - transfer_cost)

            weekly_solutions.append(
                TransferSolution(
                    gameweek=t,
                    transfers_in=transfers_in_list,
                    transfers_out=transfers_out_list,
                    expected_points=gameweek_expected_points,
                    transfer_cost=transfer_cost,
                    free_transfers_used=free_used,
                    free_transfers_remaining=free_transfers_remaining_this_week,
                )
            )

        # Calculate current expected points (no transfers)
        current_expected_points = self._calculate_current_expected_points(
            current_squad_ids, expected_points_map, solution["discount_factors"], num_gameweeks
        )

        return TransferPlan(
            weekly_solutions=weekly_solutions,
            total_expected_points=total_expected_points,
            total_transfer_cost=total_transfer_cost,
            current_expected_points=current_expected_points,
        )

    def _calculate_current_expected_points(
        self,
        current_squad_ids: List[int],
        expected_points_map: Dict[int, List[float]],
        discount_factors: np.ndarray,
        num_gameweeks: int,
    ) -> float:
        """Calculate expected points with current squad (no transfers).

        This is a simplified calculation assuming best starting XI each week.

        Args:
            current_squad_ids: Current squad player IDs
            expected_points_map: Expected points per gameweek
            discount_factors: Discount factors per gameweek
            num_gameweeks: Number of gameweeks

        Returns:
            Total expected points with current squad
        """
        total = 0.0

        for t in range(num_gameweeks):
            # Get expected points for each player in current squad
            player_points = []
            for pid in current_squad_ids:
                points_list = expected_points_map.get(pid, [0.0] * num_gameweeks)
                player_points.append(points_list[t] if t < len(points_list) else 0.0)

            # Take top 11 (simple assumption for starting XI)
            player_points.sort(reverse=True)
            gameweek_total = sum(player_points[:11])

            total += discount_factors[t] * gameweek_total

        return total
