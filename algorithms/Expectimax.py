from game_state import GameState
from algorithms.algorithm_utils import evaluate, get_possible_moves, apply_move


class Expectimax:
    """
    Expectimax algorithm implementation for finding optimal block placements
    with consideration for probabilistic elements
    """

    def __init__(self, max_depth=3):
        self.max_depth = max_depth


    def expectimax(self, state, depth):
        """
        Expectimax algorithm implementation
        For max player, chooses move with highest expected value
        """
        # Terminal conditions
        if depth == 0 or not state.remaining_blocks:
            return evaluate(state), None

        # Max player (the actual player making a decision)
        moves = get_possible_moves(state)
        if not moves:
            return evaluate(state), None

        best_value = float("-inf")
        best_move = None

        for move in moves:
            new_state = apply_move(state, move)
            value, _ = self.expectimax(new_state, depth - 1)

            if value > best_value:
                best_value = value
                best_move = move

        return best_value, best_move

    def get_best_move(self, game_model):
        """
        Get the best move using expectimax
        """
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
            current_streak_mult=game_model.get_current_streak_mult(),
            scored_this_round=game_model.get_scored_this_round(),
        )

        _, best_move = self.expectimax(initial_state, self.max_depth)

        if best_move:
            return best_move
        return None

    def get_best_moves(self, game_model):
        """
        For compatibility with A* interface, returns a path of moves
        Since we're looking 3 steps ahead, we'll compute the full 3-step path
        """
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
        )

        path = []
        current_state = initial_state
        depth_remaining = self.max_depth

        # Build a path of up to 3 moves
        while depth_remaining > 0 and current_state.remaining_blocks:
            _, best_move = self.expectimax(
                current_state, depth_remaining
            )
            if not best_move:
                break

            path.append(best_move)
            current_state = apply_move(current_state, best_move)
            depth_remaining -= 1

        return path if path else None
