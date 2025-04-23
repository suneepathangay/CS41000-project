from game_state import GameState
from algorithms.algorithm_utils import evaluate, get_possible_moves, apply_move, get_possible_blocks
import random


class Expectimax:
    """
    Expectimax algorithm implementation for finding optimal block placements
    with consideration for probabilistic elements that occur every three moves
    """

    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    def expectimax(self, state, depth, moves_since_chance=0):
        # Terminal condition
        if depth == 0 or not state.remaining_blocks:
            return evaluate(state), None

        # Handle chance node
        if moves_since_chance == 2:
            return self._handle_chance_node(state, depth)

        # Max player
        moves = get_possible_moves(state)
        if not moves:
            return evaluate(state), None

        best_value = float("-inf")
        best_move = None

        for move in moves:
            new_state = apply_move(state, move)

            shallow_value = evaluate(new_state)
            
            if best_value > float("-inf") and shallow_value < best_value * 0.5 and depth < 2:
                continue

            value, _ = self.expectimax(new_state, depth - 1, (moves_since_chance + 1) % 3)

            if value > best_value:
                best_value = value
                best_move = move
        return best_value, best_move

    
    def _handle_chance_node(self, state, depth):
        """
        Handle chance nodes where new shapes are generated
        Averages the expected values of all possible shape generations
        """
        # Get all possible shape combinations that could be generated
        possible_shape_combinations = get_possible_blocks(state.grid, state.blocks)
        
        if not possible_shape_combinations:
            return evaluate(state), None
            
        # Calculate expected value across all possible shape combinations
        total_value = 0
        # Assume uniform distribution for simplicity
        probability = 1.0 / len(possible_shape_combinations)
        
        for shapes in possible_shape_combinations:
            # Create a new state with the generated shapes
            new_state = self._create_state_with_new_shapes(state, shapes)
            # Reset moves_since_chance to 0 after a chance node
            value, _ = self.expectimax(new_state, depth - 1, 0)
            total_value += probability * value
            
        # No move to return at a chance node, just the expected value
        return total_value, None
    
    def _create_state_with_new_shapes(self, state, shapes):
        """
        Create a new state with the given shapes
        """
        # Implementation would depend on the game's state representation
        # For simplicity, this is a placeholder
        # In a real implementation, this would create a new state with
        # the given shapes added to the remaining blocks
        return state.clone_with_new_shapes(shapes)

    def get_best_move(self, game_model):
        """
        Get the best move using expectimax
        """
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
            game_model.get_blocks(),
            game_model.get_current_streak_mult(),
            game_model.get_scored_this_round(),
        )

        # Start with moves_since_chance=0
        _, best_move = self.expectimax(initial_state, self.max_depth, 0)

        if best_move:
            return best_move
        return None

    def get_best_moves(self, game_model):
        """
        For compatibility with A* interface, returns a path of moves.
        This version continues past chance nodes by letting expectimax evaluate them.
        """
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
            game_model.get_blocks(),
            game_model.get_current_streak_mult(),
            game_model.get_scored_this_round(),
        )

        path = []
        current_state = initial_state
        depth_remaining = self.max_depth
        moves_since_chance = 0

        while depth_remaining > 0 and current_state.remaining_blocks:
            _, best_move = self.expectimax(current_state, depth_remaining, moves_since_chance)

            if not best_move:
                break  # No more valid moves
            
            path.append(best_move)
            current_state = apply_move(current_state, best_move)

            depth_remaining -= 1
            moves_since_chance = (moves_since_chance + 1) % 3

            # If this move *triggered* a chance event, we simulate it
            if moves_since_chance == 0:
                # Apply chance node by picking the expected outcome (average of all)
                possible_shapes = get_possible_blocks(current_state.grid, current_state.blocks)
                if not possible_shapes:
                    break  # No valid shapes, game over

                chosen_shapes = []
                for i in range(3):
                    chosen_shapes.append(random.choice(possible_shapes))
                current_state = current_state.clone_with_new_shapes(chosen_shapes)

        return path if path else None
