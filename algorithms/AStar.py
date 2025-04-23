import heapq
from game_state import GameState
from algorithms.algorithm_utils import get_possible_moves, apply_move


class AStar:
    """
    A* Search algorithm implementation for finding optimal block placements
    """

    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    """
    potential heurisitc that that measures compactness of the grid 
    since it is better to clear the rows and cols 
    """

    def heuristic(self, state):
        """
        Heuristic evaluation function for a game state.
        Higher score indicates a better state.
        Tries to approximate the game's scoring behavior.
        """
        empty_spaces = 0
        potential_rows_cleared = 0
        potential_cols_cleared = 0
        isolated_spaces = 0
        grid = state.grid.grid
        grid_size = state.grid.get_size()

        # Analyze rows and columns for potential clears
        for row in range(grid_size):
            row_filled = True
            for col in range(grid_size):
                if not grid[row][col].get_occupied():
                    empty_spaces += 1
                    row_filled = False
            if row_filled:
                potential_rows_cleared += 1

        for col in range(grid_size):
            col_filled = True
            for row in range(grid_size):
                if not grid[row][col].get_occupied():
                    col_filled = False
                    break
            if col_filled:
                potential_cols_cleared += 1

        # Check for isolated empty cells (no orthogonal neighbors)
        for row in range(grid_size):
            for col in range(grid_size):
                if not grid[row][col].get_occupied():
                    has_neighbor = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < grid_size and 0 <= nc < grid_size:
                            if grid[nr][nc].get_occupied():
                                has_neighbor = True
                                break
                    if not has_neighbor:
                        isolated_spaces += 1

        # Estimate scoring opportunity
        lines_cleared = potential_rows_cleared + potential_cols_cleared
        line_clear_bonus = lines_cleared * 10

        if not state.scored_this_round and state.current_streak_mult > 1:
            # Protect multiplier — reward more heavily
            line_clear_bonus *= state.current_streak_mult * 2.5
        else:
            line_clear_bonus *= state.current_streak_mult

        # empty space is good (placement opportunity)
        # isolated spaces are bad (hard to fill)
        placement_bonus = empty_spaces * 1.0
        isolation_penalty = isolated_spaces * 3.0

        large_shape_penalty = 0
        for shape in state.remaining_blocks:
            size = len(shape.indices)
            if size >= 5:
                large_shape_penalty += size * 1.5

        return placement_bonus + line_clear_bonus - isolation_penalty - large_shape_penalty

    def a_star_search(self, initial_state):  # Changed default to 3
        open_set = []
        closed_set = set()

        initial_state.h_cost = self.heuristic(initial_state)
        heapq.heappush(open_set, initial_state)

        while open_set:
            current_state = heapq.heappop(open_set)

            # If we've reached our depth limit, return the current best state
            if current_state.g_cost >= self.max_depth:
                return current_state

            if not current_state.remaining_blocks:
                return current_state

            moves = get_possible_moves(current_state)

            for move in moves:
                new_state = apply_move(current_state, move)
                new_state.parent = current_state
                new_state.last_move = move
                new_state.g_cost = current_state.g_cost + 1

                # Only add if within depth limit
                if new_state.g_cost <= self.max_depth:
                    new_state.h_cost = self.heuristic(new_state)

                    state_key = str(new_state.grid.grid)
                    if state_key not in closed_set:
                        heapq.heappush(open_set, new_state)
                        closed_set.add(state_key)

        # If we can't find a complete solution, return the best partial solution
        if open_set:
            best_partial = min(open_set, key=lambda x: x.get_f_cost())
            return best_partial
        return None

    def get_best_moves(self, game_model):
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
            game_model.get_current_streak_mult(),
            game_model.get_scored_this_round(),
        )

        final_state = self.a_star_search(initial_state)

        if final_state:
            path = []
            current = final_state
            while current.parent:
                path.append(current.last_move)
                current = current.parent
            return path
        return None
