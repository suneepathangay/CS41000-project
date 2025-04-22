from game_model import GameModel
from block import Block
import heapq
from copy import deepcopy



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

def heuristic(state):
    empty_spaces = 0
    potential_clears = 0
    grid = state.grid.grid
    
    for row in range(8):
        row_filled = True
        for col in range(8):
            if not grid[row][col].get_occupied():
                empty_spaces += 1
                row_filled = False
        if row_filled:
            potential_clears += 1

    for col in range(8):
        col_filled = True
        for row in range(8):
            if not grid[row][col].get_occupied():
                col_filled = False
                break
        if col_filled:
            potential_clears += 1

    isolated_spaces = 0
    for row in range(8):
        for col in range(8):
            if not grid[row][col].get_occupied():
                has_neighbor = False
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < 8 and 0 <= nc < 8 and grid[nr][nc].get_occupied():
                        has_neighbor = True
                        break
                if not has_neighbor:
                    isolated_spaces += 1

    return -empty_spaces - (potential_clears * 10) - (isolated_spaces * 2)

def get_possible_moves(state):
    moves = []
    grid = state.grid.grid
    
    for block in state.remaining_blocks:
        for rotation in [0, 90, 180, 270]:
            rotated_block = deepcopy(block)
            rotated_block.rotate(rotation)
            
            for row in range(8):
                for col in range(8):
                    can_place = True
                    for dr, dc in rotated_block.indices:
                        nr, nc = row + dr, col + dc
                        if nr >= 8 or nc >= 8 or grid[nr][nc].get_occupied():
                            can_place = False
                            break
                    
                    if can_place:
                        moves.append((rotated_block, row, col, rotation))
    
    return moves

def apply_move(state, move):
    block, row, col, rotation = move
    new_state = GameState(deepcopy(state.grid), state.score, state.remaining_blocks.copy())
    
    for dr, dc in block.indices:
        new_state.grid.set_tile(row + dr, col + dc, True)
    
    new_state.remaining_blocks.remove(block)
    
    tiles_placed = len(block.indices)
    rows_cleared = len(new_state.grid.check_full_rows())
    cols_cleared = len(new_state.grid.check_full_cols())
    new_state.score += tiles_placed + (rows_cleared + cols_cleared) * 10
    
    return new_state

def a_star_search(initial_state):
    open_set = []
    closed_set = set()
    
    initial_state.h_cost = heuristic(initial_state)
    heapq.heappush(open_set, initial_state)
    
    while open_set:
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
