from copy import deepcopy
from game_state import GameState
from game_model import GameModel
from algorithms.algorithm_utils import get_possible_moves, apply_move

class QLearn:
    """
    Basic Q-learning algorithm implementation following the formula:
    Q(s,a) = Q(s,a) + α[R + γ·max_a Q(s',a') - Q(s,a)]
    
    Where:
    - s is the current state
    - a is the action taken
    - s' is the next state
    - R is the immediate reward
    - α is the learning rate
    - γ is the discount factor
    """
    
    def __init__(self, max_depth=2, learning_rate=0.5, discount_factor=0.9):
        self.max_depth = max_depth
        self.learning_rate = learning_rate  # Alpha (α)
        self.discount_factor = discount_factor  # Gamma (γ)
        self.nodes_evaluated = 0
        self.q_values = {}  # Dictionary to store Q-values for state-action pairs
    
    def get_state_key(self, state):
        """
        Generate a unique key for a state to use in the Q-value dictionary.
        """
        # For the state key, we'll use a simplified grid representation
        grid = state.grid
        grid_size = grid.get_size()
        grid_str = ""
        
        for row in range(grid_size):
            for col in range(grid_size):
                grid_str += "1" if grid.get_tile(row=row, col=col).get_occupied() else "0"
        
        # Add remaining blocks
        blocks_str = "|"
        for block in state.remaining_blocks:
            blocks_str += str(hash(str(block.indices)))
        
        # Add score and multiplier
        state_key = f"{grid_str}{blocks_str}|{state.score}|{state.current_streak_mult}"
        return state_key
    
    def get_action_key(self, action):
        """
        Generate a unique key for an action.
        """
        block_idx, _, row, col = action
        return f"{block_idx}_{row}_{col}"
    
    def get_q_value(self, state, action):
        """
        Get the Q-value for a state-action pair.
        If not in dictionary, initialize to 0.
        """
        state_key = self.get_state_key(state)
        action_key = self.get_action_key(action)
        
        if state_key not in self.q_values:
            self.q_values[state_key] = {}
        
        if action_key not in self.q_values[state_key]:
            self.q_values[state_key][action_key] = 0.0
            
        return self.q_values[state_key][action_key]
    
    def update_q_value(self, state, action, reward, next_state, next_max_q):
        """
        Update Q-value using the Q-learning formula:
        Q(s,a) = Q(s,a) + α[R + γ·max_a Q(s',a') - Q(s,a)]
        """
        state_key = self.get_state_key(state)
        action_key = self.get_action_key(action)
        
        # Get current Q-value
        current_q = self.get_q_value(state, action)
        
        # Calculate temporal difference
        td_target = reward + self.discount_factor * next_max_q
        td_error = td_target - current_q
        
        # Update Q-value
        new_q_value = current_q + self.learning_rate * td_error
        
        # Store the updated Q-value
        if state_key not in self.q_values:
            self.q_values[state_key] = {}
        
        self.q_values[state_key][action_key] = new_q_value
        
        return new_q_value
    
    def get_max_q_value(self, state):
        """
        Get the maximum Q-value for any action from the current state.
        """
        possible_moves = get_possible_moves(state)
        
        if not possible_moves:
            return 0.0
        
        max_q = float('-inf')
        
        for move in possible_moves:
            q_value = self.get_q_value(state, move)
            if q_value > max_q:
                max_q = q_value
        
        return max_q
    
    def get_reward(self, state, action, next_state):
        """
        Calculate the immediate reward for taking an action.
        Here we use the score difference as the reward.
        """
        reward = next_state.score - state.score
        
        # Additional reward for clearing lines
        full_rows = next_state.grid.check_full_rows()
        full_cols = next_state.grid.check_full_cols()
        
        # Add bonus reward for clearing lines
        reward += (len(full_rows) + len(full_cols)) * 10
        
        return reward
    
    def q_learning_search(self, state, depth):
        """
        Perform Q-learning search to find the best action sequence.
        """
        self.nodes_evaluated += 1
        
        # Base case: reached maximum depth or no more blocks
        if depth <= 0 or not state.remaining_blocks:
            return [], 0
        
        # Get all possible moves
        possible_moves = get_possible_moves(state)
        
        if not possible_moves:
            return [], 0
        
        best_q_value = float('-inf')
        best_path = []
        
        # Try each action and update Q-values
        for action in possible_moves:
            # Apply action to get next state
            next_state = apply_move(state, action)
            
            # Calculate immediate reward
            reward = self.get_reward(state, action, next_state)
            
            # Recursively search for best action sequence from next state
            next_path, _ = self.q_learning_search(next_state, depth - 1)
            
            # Get max Q-value for next state
            next_max_q = self.get_max_q_value(next_state)
            
            # Update Q-value using the formula
            q_value = self.update_q_value(state, action, reward, next_state, next_max_q)
            
            # Track best action based on updated Q-value
            if q_value > best_q_value:
                best_q_value = q_value
                best_path = [action] + next_path
        
        return best_path, best_q_value
    
    def get_best_moves(self, game_model: GameModel):
        """
        Entry point to get the best move sequence from the current game state.
        """
        print(f"Starting Q-learning search with max depth: {self.max_depth}")
        self.nodes_evaluated = 0
        
        initial_state = GameState(
            grid=deepcopy(game_model.get_grid()),
            score=game_model.get_score(),
            remaining_blocks=deepcopy(game_model.get_current_shapes()),
            blocks=game_model.get_blocks(),
            current_streak_mult=game_model.get_current_streak_mult(),
            scored_this_round=game_model.get_scored_this_round()
        )
        
        print(f"Initial state has {len(initial_state.remaining_blocks)} blocks, Initial score: {initial_state.score}")
        
        # Run Q-learning search
        best_path, best_q_value = self.q_learning_search(initial_state, self.max_depth)
        
        # Simulate the best path to get the final score
        final_score = initial_state.score
        current_state = initial_state
        
        for i, move in enumerate(best_path):
            next_state = apply_move(current_state, move)
            reward = next_state.score - current_state.score
            current_state = next_state
            
            print(f"Move {i+1}: Score change: +{reward}, New score: {current_state.score}")
            
        final_score = current_state.score
        
        # Print details about the chosen path
        if best_path:
            print(f"Selected path length: {len(best_path)}")
            for i, move in enumerate(best_path):
                block_idx, block, row, col = move
                print(f"Move {i+1}: Block {block_idx} at position ({row}, {col})")
        
        print(f"Search complete. Total states evaluated: {self.nodes_evaluated}")
        print(f"Final score: {final_score}, Best Q-value: {best_q_value}")
        
        return best_path