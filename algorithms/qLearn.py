from copy import deepcopy
import random
from game_state import GameState
from game_model import GameModel

def get_possible_moves(state):
    """
    Get all possible moves for the current blocks
    """
    moves = []
    grid = state.grid
    grid_size = grid.get_size()
    
    for block_idx, block in enumerate(state.remaining_blocks):
        for row in range(grid_size):
            for col in range(grid_size):
                can_place = True
                for dr, dc in block.indices:
                    nr, nc = row + dr, col + dc
                    if (
                        nr < 0 or nr >= grid_size or
                        nc < 0 or nc >= grid_size or
                        grid.get_tile(row=nr, col=nc).get_occupied()
                    ):
                        can_place = False
                        break
                
                if can_place:
                    moves.append((block_idx, block, row, col))
    
    # Shuffle moves for diversity
    random.shuffle(moves)
    return moves

def apply_move(state, move):
    """
    Apply a move to the state and return the new state
    """
    block_idx, block, row, col = move
    grid_size = state.grid.get_size()
    
    # Create new state with deep copies
    new_state = GameState(
        grid=deepcopy(state.grid),
        score=state.score,
        remaining_blocks=deepcopy(state.remaining_blocks),
        blocks=state.blocks,
        current_streak_mult=state.current_streak_mult,
        scored_this_round=state.scored_this_round
    )
    
    # Place the block using the correct API
    for dr, dc in block.indices:
        nr, nc = row + dr, col + dc
        new_state.grid.set_tile(row=nr, col=nc, tile_state=True)
    
    # Remove used block
    new_state.remaining_blocks.pop(block_idx)
    
    # Use the built-in methods to check for full rows and columns
    full_rows = new_state.grid.check_full_rows()
    full_cols = new_state.grid.check_full_cols()
    
    # Calculate score
    tiles_placed = len(block.indices)
    clear_score = (len(full_rows) + len(full_cols)) * 10
    
    if clear_score > 0:
        new_state.scored_this_round = True
        multiplied_clear_score = clear_score * new_state.current_streak_mult
        new_state.current_streak_mult += 1
        new_state.score += tiles_placed + multiplied_clear_score
    else:
        if not new_state.scored_this_round:
            new_state.current_streak_mult = 1
        new_state.score += tiles_placed
    
    # Clear full rows and columns
    for r in full_rows:
        for c in range(grid_size):
            new_state.grid.set_tile(row=r, col=c, tile_state=False)
    
    for c in full_cols:
        for r in range(grid_size):
            new_state.grid.set_tile(row=r, col=c, tile_state=False)
    
    # Add new blocks if needed (this is the key for multi-turn planning)
    if len(new_state.remaining_blocks) == 0 and hasattr(state, 'blocks') and state.blocks:
        # This is a new round, we need to add new blocks
        # Since we can't directly call game_model methods, we'll simulate adding new blocks
        # by sampling from the available blocks
        if hasattr(state, 'blocks') and len(state.blocks) > 0:
            # Add 3 new random blocks (or as many as available)
            for _ in range(min(3, len(state.blocks))):
                idx = random.randint(0, len(state.blocks) - 1)
                new_block = deepcopy(state.blocks[idx])
                new_state.remaining_blocks.append(new_block)
            
            # Reset scored_this_round flag for the new round
            if not new_state.scored_this_round:
                new_state.current_streak_mult = 1
            new_state.scored_this_round = False
    
    return new_state

class QLearn:
    """
    Q* Search algorithm implementation using depth-limited lookahead
    with heuristic evaluation to estimate long-term rewards.
    """
    
    def __init__(self, max_depth=2):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.all_paths = []
        # Set a different random seed each time
        self.random_seed = random.randint(1, 10000)
        random.seed(self.random_seed)
    
    def evaluate(self, state: GameState):
        """
        Heuristic evaluation function: higher is better
        """
        self.nodes_evaluated += 1
        
        empty_spaces = 0
        potential_clears = 0
        grid = state.grid
        grid_size = grid.get_size()
        
        # Count empty spaces and potential row/column clears
        for row in range(grid_size):
            row_filled = True
            row_occupied = 0
            for col in range(grid_size):
                if not grid.get_tile(row=row, col=col).get_occupied():
                    empty_spaces += 1
                    row_filled = False
                else:
                    row_occupied += 1
            
            if row_filled:
                potential_clears += 1
            # Partial credit for nearly full rows
            elif row_occupied >= grid_size * 0.75:
                potential_clears += 0.5
        
        for col in range(grid_size):
            col_filled = True
            col_occupied = 0
            for row in range(grid_size):
                if not grid.get_tile(row=row, col=col).get_occupied():
                    col_filled = False
                else:
                    col_occupied += 1
            
            if col_filled:
                potential_clears += 1
            # Partial credit for nearly full columns
            elif col_occupied >= grid_size * 0.75:
                potential_clears += 0.5
        
        # Count isolated spaces
        isolated_spaces = 0
        for row in range(grid_size):
            for col in range(grid_size):
                if not grid.get_tile(row=row, col=col).get_occupied():
                    has_neighbor = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if (
                            0 <= nr < grid_size
                            and 0 <= nc < grid_size
                            and grid.get_tile(row=nr, col=nc).get_occupied()
                        ):
                            has_neighbor = True
                            break
                    if not has_neighbor:
                        isolated_spaces += 1
        
        # Add a larger random factor (15% variation) to encourage diversity
        random_factor = random.uniform(0.85, 1.15)
        
        # Calculate final score with more randomness
        score = (
            (state.score * 2.0)
            + (-empty_spaces * 1.0)
            + (potential_clears * 10.0) 
            + (-isolated_spaces * 2.0)
            + (state.current_streak_mult * 5.0 if state.current_streak_mult > 1 else 0)
        ) * random_factor
        
        # Add a bonus for states with more moves left (for longer paths)
        if hasattr(state, 'remaining_blocks') and len(state.remaining_blocks) > 0:
            score += len(state.remaining_blocks) * 2.0
            
        return score
    
    def simulate_next_round(self, state):
        """
        Simulate adding new blocks for the next round
        """
        if not hasattr(state, 'blocks') or not state.blocks:
            return state  # Can't add new blocks
            
        new_state = GameState(
            grid=deepcopy(state.grid),
            score=state.score,
            remaining_blocks=[],  # Start with empty list
            blocks=state.blocks,
            current_streak_mult=state.current_streak_mult,
            scored_this_round=False  # Reset for new round
        )
        
        # Add 3 new random blocks or as many as available
        for _ in range(min(3, len(state.blocks))):
            idx = random.randint(0, len(state.blocks) - 1)
            new_block = deepcopy(state.blocks[idx])
            new_state.remaining_blocks.append(new_block)
            
        return new_state
    
    def q_star_search(self, state, depth, path_so_far=None):
        """
        Recursive depth-limited Q* lookahead with path tracking
        """
        if path_so_far is None:
            path_so_far = []
            
        # Debug print
        print(f"Searching at depth: {depth}, Remaining blocks: {len(state.remaining_blocks)}")
        
        # Base case: reached maximum depth or game over
        if depth <= 0:
            eval_score = self.evaluate(state)
            print(f"Reached terminal state, evaluation: {eval_score}")
            return eval_score, path_so_far
        
        # Get all possible moves
        possible_moves = get_possible_moves(state)
        print(f"Found {len(possible_moves)} possible moves at depth {depth}")
        
        # No valid moves case
        if not possible_moves:
            # Check if we can start a new round
            if len(state.remaining_blocks) == 0 and hasattr(state, 'blocks') and state.blocks:
                # Try to get new blocks and continue
                new_state = self.simulate_next_round(state)
                if len(new_state.remaining_blocks) > 0:
                    return self.q_star_search(new_state, depth - 1, path_so_far)
                
            # No more moves possible
            eval_score = self.evaluate(state)
            print(f"No possible moves, evaluation: {eval_score}")
            return eval_score, path_so_far
        
        best_score = float('-inf')
        best_path = None
        
        # Limit moves to evaluate for higher depths to improve performance
        max_moves = min(len(possible_moves), 10 if depth > 3 else 15)
        
        # Try each move
        for move_idx, move in enumerate(possible_moves[:max_moves]):
            print(f"Evaluating move {move_idx+1}/{max_moves} at depth {depth}")
            
            # Apply the move to get new state
            new_state = apply_move(state, move)
            
            # Recursively search from this new state with reduced depth
            new_path = path_so_far + [move]  # Add current move to path
            score, sub_path = self.q_star_search(new_state, depth - 1, new_path)
            
            # Add small random variation to break ties
            score_with_noise = score * random.uniform(0.98, 1.02)
            
            # If this move is better than the best so far, update
            if score_with_noise > best_score:
                best_score = score_with_noise
                best_path = sub_path
                print(f"New best score at depth {depth}: {best_score}")
        
        # Store this path for potential later use
        if best_path and len(best_path) > 0:
            if len(best_path) > len(path_so_far):
                self.all_paths.append((best_score, best_path))
        
        return best_score, best_path if best_path else path_so_far
    
    def get_best_moves(self, game_model: GameModel):
        """
        Entry point to get the best move sequence from the current game state
        """
        print(f"Starting Q* search with max depth: {self.max_depth}")
        self.nodes_evaluated = 0
        self.all_paths = []
        
        # Set a new random seed each time
        random.seed(self.random_seed + self.max_depth)
        
        initial_state = GameState(
            grid=deepcopy(game_model.get_grid()),
            score=game_model.get_score(),
            remaining_blocks=deepcopy(game_model.get_current_shapes()),
            blocks=game_model.get_blocks(),
            current_streak_mult=game_model.get_current_streak_mult(),
            scored_this_round=game_model.get_scored_this_round()
        )
        
        print(f"Initial state has {len(initial_state.remaining_blocks)} blocks")
        
        # Run search with different random seeds
        score, best_path = self.q_star_search(initial_state, self.max_depth)
        
        # Add some variation - sometimes pick a different path for diversity
        if len(self.all_paths) > 1:
            # Sort paths by score (descending) and then by length (descending)
            self.all_paths.sort(key=lambda x: (x[0], len(x[1])), reverse=True)
            
            # 20% chance to pick a different path for variety
            if random.random() < 0.2 and len(self.all_paths) > 1:
                # Pick a random path from the top half of paths
                idx = random.randint(1, min(len(self.all_paths) - 1, 3))
                score, best_path = self.all_paths[idx]
                print(f"Selected alternative path for variety. Score: {score}")
        
        # Print detailed information about the chosen path
        if best_path:
            print(f"Selected path length: {len(best_path)}")
            for i, move in enumerate(best_path):
                block_idx, block, row, col = move
                print(f"Move {i+1}: Block {block_idx} at position ({row}, {col})")
            
        print(f"Search complete. Total states evaluated: {self.nodes_evaluated}")
        
        return score, best_path or []