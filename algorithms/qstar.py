from copy import deepcopy
from game_state import GameState
from algorithms.algorithm_utils import get_possible_moves, apply_move
from heapq import heappush, heappop
from game_model import GameModel


class QStar:
    """
    Q* Search algorithm implementation using depth-limited lookahead
    with heuristic evaluation to estimate long-term rewards.
    """

    def __init__(self, max_depth=2):
        self.max_depth = max_depth

    def evaluate(self, state:GameState):
        """
        Heuristic evaluation function: higher is better
        """
        empty_spaces = 0
        potential_clears = 0
        grid = state.grid

        for row in range(len(grid.grid)):
            row_filled = True
            for col in range(len(grid.grid[0])):
                if not grid.get_tile(row=row, col=col).get_occupied():
                    empty_spaces += 1
                    row_filled = False
            if row_filled:
                potential_clears += 1

        for col in range(len(grid.grid)):
            col_filled = True
            for row in range(len(grid.grid[0])):
                if not grid.get_tile(row=row, col=col).get_occupied():
                    col_filled = False
                    break
            if col_filled:
                potential_clears += 1

        isolated_spaces = 0
        for row in range(state.grid.get_size()):
            for col in range(state.grid.get_size()):
                if not grid.get_tile(row=row, col=col).get_occupied():
                    has_neighbor = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if (
                            0 <= nr < state.grid.get_size()
                            and 0 <= nc < state.grid.get_size()
                            and grid.get_tile(row=row,col=col).get_occupied()
                        ):
                            has_neighbor = True
                            break
                    if not has_neighbor:
                        isolated_spaces += 1

        return (
            state.score
            + (-empty_spaces * 1.0)
            + (potential_clears * 10.0)
            + (-isolated_spaces * 2.0)
        )

    def q_star_search(self, state:GameState, depth):
        """
        Recursive depth-limited Q* lookahead
        """
        
        
        if depth == 0 or not state.remaining_blocks:

            return self.evaluate(state), []

        best_score = float('-inf')
        best_path = []

        possible_moves = get_possible_moves(state)
        
        if not possible_moves:
            return self.evaluate(state), []

        for move in possible_moves:
            new_state = apply_move(state, move)
            score, path = self.q_star_search(new_state, depth - 1)

            if score > best_score:
                best_score = score
                best_path = [move] + path

        return best_score, best_path

    def get_best_moves(self, game_model:GameModel):
        """
        Entry point to get the best move sequence from the current game state
        """
        game_model.start_game()
        
        initial_state = GameState(
            deepcopy(game_model.get_grid()),
            game_model.get_score(),
            deepcopy(game_model.get_current_shapes())
        )


        _, best_path = self.q_star_search(initial_state, self.max_depth)
        return best_path
