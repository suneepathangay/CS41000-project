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
        empty_spaces = 0
        potential_clears = 0
        grid = state.grid.grid
        
        # Count empty spaces and potential row clears
        for row in range(state.grid.get_size()):
            row_filled = True
            for col in range(state.grid.get_size()):
                if not grid[row][col].get_occupied():
                    empty_spaces += 1
                    row_filled = False
            if row_filled:
                potential_clears += 1
        
        # Count potential column clears
        for col in range(state.grid.get_size()):
            col_filled = True
            for row in range(state.grid.get_size()):
                if not grid[row][col].get_occupied():
                    col_filled = False
                    break
            if col_filled:
                potential_clears += 1
        
        # Count isolated empty spaces
        isolated_spaces = 0
        for row in range(state.grid.get_size()):
            for col in range(state.grid.get_size()):
                if not grid[row][col].get_occupied():
                    has_neighbor = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if (
                            0 <= nr < state.grid.get_size()
                            and 0 <= nc < state.grid.get_size()
                            and grid[nr][nc].get_occupied()
                        ):
                            has_neighbor = True
                            break
                    if not has_neighbor:
                        isolated_spaces += 1
        
        base_score = -empty_spaces * 1.0 - potential_clears * 10.0 - isolated_spaces * 2.0
        
        # Add streak multiplier considerations
        streak_bonus = 0

        if state.current_streak_mult > 1 and not state.scored_this_round:
            # Heavily reward potential clears to avoid losing the multiplier
            streak_bonus = potential_clears * 25.0 * state.current_streak_mult
        else:
            # Still reward potential clears based on current multiplier
            streak_bonus = potential_clears * 5.0 * state.current_streak_mult
        
        return base_score + streak_bonus

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
