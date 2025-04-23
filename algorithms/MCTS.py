from copy import deepcopy
import math
import random
from game_state import GameState
from algorithms.algorithm_utils import evaluate, get_possible_moves, apply_move

class MCTSNode:
    """
    Node class for Monte Carlo Tree Search
    """
    def __init__(self, state, parent=None, move=None, depth=0):
        self.state = state
        self.parent = parent
        self.move = move  # Move that led to this state
        self.children = []
        self.visits = 0
        self.value = 0
        self.untried_moves = get_possible_moves(state)
        self.depth = depth  # Track depth in the search tree
        
    def uct_select_child(self, exploration_weight=1.0):
        """
        Select the child with the highest UCT value
        """
        log_parent_visits = math.log(self.visits) if self.visits > 0 else 0
        
        best_score = float('-inf')
        best_child = None
        
        for child in self.children:
            exploitation = child.value / child.visits if child.visits > 0 else 0
            exploration = exploration_weight * math.sqrt(log_parent_visits / child.visits) if child.visits > 0 else float('inf')
            uct_score = exploitation + exploration
            
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
                
        return best_child
    
    def expand(self):
        """
        Expand the tree by adding a child node
        """
        if not self.untried_moves:
            return None
            
        move = self.untried_moves.pop(random.randrange(len(self.untried_moves)))
        new_state = apply_move(deepcopy(self.state), move)
        child_node = MCTSNode(new_state, parent=self, move=move, depth=self.depth + 1)
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
        return (not self.state.remaining_blocks or 
                not get_possible_moves(self.state) or 
                self.depth >= 3)
        
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
            sequence.append(node.move)
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
                moves = get_possible_moves(state)
                if not moves:
                    break
                move = random.choice(moves)
                state = apply_move(state, move)
                current_depth += 1
                
            # Backpropagation
            result = evaluate(state)
            while node is not None:
                node.update(result)
                node = node.parent
                
        # Find the best move sequence
        return self._get_best_sequence(root)
    
    def _is_terminal(self, state):
        """
        Check if the state is terminal
        """
        return not state.remaining_blocks or not get_possible_moves(state)
        
    def _get_best_sequence(self, root):
        """
        Find the best path in the tree up to depth 3
        """
        # Start with the best immediate child
        best_child = None
        best_visits = -1
        
        for child in root.children:
            if child.visits > best_visits:
                best_visits = child.visits
                best_child = child
                
        if not best_child:
            return []
            
        # Follow the most visited path up to depth 3
        path = [best_child.move]
        current = best_child
        
        while len(path) < 3 and current.children:
            best_next = None
            best_next_visits = -1
            
            for child in current.children:
                if child.visits > best_next_visits:
                    best_next_visits = child.visits
                    best_next = child
                    
            if not best_next:
                break
                
            path.append(best_next.move)
            current = best_next
            
        return path
        
    def get_best_move(self, game_model):
        """
        Get the best move using MCTS (just the first move of the sequence)
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