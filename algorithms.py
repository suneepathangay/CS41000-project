from game_model import GameModel
from block import Block
import heapq
from copy import deepcopy
from util import print_curr_state
from grid import Grid


"""
Contains the algorithms for the game such as A* search
"""

"""
GameState class
"""
class GameState:
    def __init__(self, grid, score, remaining_blocks):
        self.grid = grid
        self.score = score
        self.remaining_blocks = remaining_blocks
        self.g_cost = 0
        self.h_cost = 0
        self.parent = None
        self.last_move = None

    def __lt__(self, other):
        return (self.g_cost + self.h_cost) < (other.g_cost + other.h_cost)

    def get_f_cost(self):
        return self.g_cost + self.h_cost

"""
potnential heurisitc that that measures compactness of the grid 
since it is bettert to clear the rows and cols 
"""
def heuristic(state):
    empty_spaces = 0
    potential_clears = 0
    grid = state.grid.grid
    
    for row in range(state.grid.get_size()):
        row_filled = True
        for col in range(state.grid.get_size()):
            if not grid[row][col].get_occupied():
                empty_spaces += 1
                row_filled = False
        if row_filled:
            potential_clears += 1

    for col in range(state.grid.get_size()):
        col_filled = True
        for row in range(state.grid.get_size()):
            if not grid[row][col].get_occupied():
                col_filled = False
                break
        if col_filled:
            potential_clears += 1

    isolated_spaces = 0
    for row in range(state.grid.get_size()):
        for col in range(state.grid.get_size()):
            if not grid[row][col].get_occupied():
                has_neighbor = False
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < state.grid.get_size() and 0 <= nc < state.grid.get_size() and grid[nr][nc].get_occupied():
                        has_neighbor = True
                        break
                if not has_neighbor:
                    isolated_spaces += 1

    return -empty_spaces - (potential_clears * 10) - (isolated_spaces * 2)

"""
get_possible_moves function
"""
def get_possible_moves(state):
    moves = []
    grid = state.grid.grid
    
    for block_idx, block in enumerate(state.remaining_blocks):
        for rotation in [0, 90, 180, 270]:
            rotated_block = deepcopy(block)
            rotated_block.rotate(rotation)
            
            for row in range(state.grid.get_size()):
                for col in range(state.grid.get_size()):
                    can_place = True
                    for dr, dc in rotated_block.indices:
                        nr, nc = row + dr, col + dc
                        if nr >= state.grid.get_size() or nc >= state.grid.get_size() or grid[nr][nc].get_occupied():
                            can_place = False
                            break
                    
                    if can_place:
                        moves.append((block_idx, rotated_block, row, col, rotation))
    
    return moves

def apply_move(state, move):
    block_idx, block, row, col, rotation = move
    new_state = GameState(deepcopy(state.grid), state.score, state.remaining_blocks.copy())
    
    for dr, dc in block.indices:
        new_state.grid.set_tile(row + dr, col + dc, True)
    
    # Remove by index instead of by reference
    new_state.remaining_blocks.pop(block_idx)
    
    tiles_placed = len(block.indices)
    rows_cleared = len(new_state.grid.check_full_rows())
    cols_cleared = len(new_state.grid.check_full_cols())
    new_state.score += tiles_placed + (rows_cleared + cols_cleared) * 10
    
    return new_state

def a_star_search(initial_state, max_depth=10000):
    open_set = []
    closed_set = set()
    
    initial_state.h_cost = heuristic(initial_state)
    heapq.heappush(open_set, initial_state)
    
    while open_set and len(open_set) < max_depth:
        current_state = heapq.heappop(open_set)
        
        if not current_state.remaining_blocks:
            return current_state
        
        moves = get_possible_moves(current_state)
        
        for move in moves:
            new_state = apply_move(current_state, move)
            new_state.parent = current_state
            new_state.last_move = move
            new_state.g_cost = current_state.g_cost + 1
            new_state.h_cost = heuristic(new_state)
            print(new_state.grid.visualize())

            
            state_key = str(new_state.grid.grid)
            if state_key not in closed_set:
                heapq.heappush(open_set, new_state)
                closed_set.add(state_key)
    
    return None

def get_best_move(game_model):
    initial_state = GameState(
        game_model.get_grid(),
        game_model.get_score(),
        game_model.get_current_shapes()
    )
    
    final_state = a_star_search(initial_state)
    
    if final_state:
        path = []
        current = final_state
        while current.parent:
            path.append(current.last_move)
            current = current.parent
        return path[-1]
    return None

def main():
    # Create a new game model
    game = GameModel(grid_size=4)
    
    # Initialize the game with some blocks
    # This would depend on how your GameModel and Block classes are implemented
    # For example:
    game.start_game()  # Assuming this method exists
    
    print("Initial game state:")
    print(f"Score: {game.get_score()}")
    print(f"Available blocks: {len(game.get_current_shapes())}")
    print_curr_state(game.get_grid().grid) 
    
    # Get the best move
    best_move = get_best_move(game)
    
    if best_move:
        block, row, col, rotation = best_move
        print(f"\nBest move found:")
        print(f"Block: {block}")
        print(f"Position: ({row}, {col})")
        print(f"Rotation: {rotation} degrees")
        
        # Apply the move
        # game.place_block(block, row, col)  # Assuming this method exists
        
        print("\nAfter applying the best move:")
        print(f"Score: {game.get_score()}")
        print(f"Available blocks: {len(game.get_current_shapes())}")
        print_curr_state(game.get_grid().grid) 
    else:
        print("\nNo valid moves found!")

if __name__ == "__main__":
    main()
