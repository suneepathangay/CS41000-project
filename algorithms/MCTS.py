from copy import deepcopy
import math
from random import Random
from game_state import GameState
from algorithms.algorithm_utils import (
    evaluate,
    get_possible_moves,
    apply_move,
    get_possible_blocks,
)


class MCTSNode:
    """
    Node class for Monte Carlo Tree Search
    """

    def __init__(self, state, parent=None, prev_move=None, depth=0, seed=42):
        self.state = state
        self.parent = parent
        self.prev_move = prev_move
        self.children = []
        self.visits = 0
        self.value = 0
        self.untried_moves = get_possible_moves(state)
        self.depth = depth
        self.rng = Random(seed)

    def uct_select_child(self, exploration_weight=1.0):
        # Add a small constant to avoid division by zero
        epsilon = 1e-6
        log_parent_visits = math.log(self.visits + epsilon)

        # Add randomness to break ties
        best_score = float("-inf")
        best_children = []

        for child in self.children:
            exploitation = child.value / (child.visits + epsilon)
            exploration = exploration_weight * math.sqrt(
                log_parent_visits / (child.visits + epsilon)
            )
            uct_score = exploitation + exploration

            if abs(uct_score - best_score) < 1e-8:  # Approximately equal
                best_children.append(child)
            elif uct_score > best_score:
                best_score = uct_score
                best_children = [child]

        # Choose randomly among best children to promote diversity
        return self.rng.choice(best_children) if best_children else None

    def expand(self):
        """
        Expand the tree by adding a child node
        """
        if not self.untried_moves:
            return None

        move = self.untried_moves.pop(self.rng.randint(0, len(self.untried_moves) - 1))
        new_state = apply_move(deepcopy(self.state), move)
        child_node = MCTSNode(
            new_state, parent=self, prev_move=move, depth=self.depth + 1
        )
        self.children.append(child_node)

        return child_node

    def update(self, result):
        """
        Update the node statistics
        """
        self.visits += 1
        self.value += result

    def is_terminal(self):
        """
        Check if the state is terminal or if we've reached max depth (3 moves)
        """
        # Terminal if no more blocks or no possible moves or reached depth 3
        return (
            not self.state.remaining_blocks
            or not get_possible_moves(self.state)
            or self.depth >= 3
        )

    def is_fully_expanded(self):
        """
        Check if all possible moves from this state have been tried
        """
        return len(self.untried_moves) == 0

    def get_move_sequence(self):
        """
        Get the sequence of moves from root to this node
        """
        sequence = []
        node = self
        while node.parent is not None:  # Stop at the root node
            sequence.append(node.prev_move)
            node = node.parent

        sequence.reverse()  # Reverse to get correct order
        return sequence


class MCTS:
    """
    Monte Carlo Tree Search implementation for finding optimal 3-move sequences
    """

    def __init__(self, iterations=1000, exploration_weight=1.0):
        self.iterations = iterations
        self.exploration_weight = exploration_weight
        self.rng = Random(42)  # Fixed seed for reproducibility

    def search(self, root_state):
        """
        Perform Monte Carlo Tree Search to find the best 3-move sequence
        """
        root = MCTSNode(root_state)

        # Run for the specified number of iterations
        for _ in range(self.iterations):
            # Selection
            node = root
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.uct_select_child(self.exploration_weight)

            # Expansion
            if not node.is_terminal():
                node = node.expand()

            # Simulation
            state = deepcopy(node.state)
            current_depth = node.depth

            # Continue simulation until terminal or depth 3
            while not self._is_terminal(state) and current_depth < 3:
                moves = self.get_reasonable_moves(state)
                if not moves:
                    break

                move = moves[node.rng.randint(0, len(moves) - 1)]
                state = apply_move(state, move)
                current_depth += 1

                # Check if we need to regenerate shapes (every 3 moves)
                if current_depth == 3:
                    state.current_shapes = self._generate_new_shapes(state)

            # Backpropagation
            result = evaluate(state)
            result += 5 * current_depth
            while node is not None:
                node.update(result)
                node = node.parent

        # Find the best move sequence
        return self._get_best_sequence(root)

    def _generate_new_shapes(self, state):
        """
        Generate a new set of shapes based on remaining blocks
        """
        possible_shapes = get_possible_blocks(state.grid, state.blocks)
        new_shapes = []
        for i in range(3):
            new_shapes.append(
                possible_shapes[self.rng.randint(0, len(possible_shapes) - 1)]
            )
        return new_shapes

    def _is_terminal(self, state):
        """
        Check if the state is terminal
        """
        return not state.remaining_blocks or not get_possible_moves(state)

    def _get_best_sequence(self, root):
        """
        Find the best path in the tree up to depth 3 based on both visit count and value
        """
        # Start with the best immediate child using UCT value
        best_child = root.uct_select_child(
            exploration_weight=0.0
        )  # Use 0 for exploitation only

        if not best_child:
            return []

        # Follow the best path up to depth 3
        path = [best_child.prev_move]
        current = best_child

        while len(path) < 3 and current.children:
            best_next = current.uct_select_child(
                exploration_weight=0.0
            )  # Use 0 for exploitation only

            if not best_next:
                break

            path.append(best_next.prev_move)
            current = best_next

        return path

    def get_best_move(self, game_model):
        """
        Get the best move using MCTS with some randomization to prevent loops
        """
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
            game_model.get_blocks(),
            game_model.get_current_streak_mult(),
            game_model.get_scored_this_round(),
        )

        move_sequence = self.search(initial_state)

        if not move_sequence or self.rng.random() < 0.1:
            possible_moves = get_possible_moves(initial_state)
            if possible_moves:
                return possible_moves[self.rng.randint(0, len(possible_moves) - 1)]

        return move_sequence[0] if move_sequence else None

    def get_best_moves(self, game_model):
        """
        Get the best 3-move sequence using MCTS
        """
        initial_state = GameState(
            game_model.get_grid(),
            game_model.get_score(),
            game_model.get_current_shapes(),
            game_model.get_blocks(),
            game_model.get_current_streak_mult(),
            game_model.get_scored_this_round(),
        )

        move_sequence = self.search(initial_state)
        return move_sequence if move_sequence else None

    def is_valid_move(state, move):
        try:
            apply_move(deepcopy(state), move)
            return True  # or validate some property
        except:
            return False

    def score_delta(self, state, move):
        new_state = apply_move(deepcopy(state), move)
        return evaluate(new_state) - evaluate(state)

    def get_reasonable_moves(self, state):
        moves = get_possible_moves(state)
        scored_moves = []

        for move in moves:
            delta = self.score_delta(state, move)
            if delta >= 0:  # Keeps or improves score
                scored_moves.append((move, delta))

        # Sort by score delta descending
        scored_moves.sort(key=lambda x: x[1], reverse=True)

        # Optionally take top N
        top_moves = [m for m, _ in scored_moves[:5]]  # or any threshold
        return top_moves or moves  # fallback to original if none scored positively
