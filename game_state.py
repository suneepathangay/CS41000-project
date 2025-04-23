from grid import Grid

"""
GameState class
"""
class GameState:
    def __init__(self, grid:Grid, score, remaining_blocks):
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
    
    
    
    def set_remaining_blocks(self, blocks_remaining):
        self.remaining_blocks = blocks_remaining
        
    def get_remaining_blocks(self):
        return self.remaining_blocks
        
    
    