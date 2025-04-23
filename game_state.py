from grid import Grid

"""
GameState class
"""
class GameState:
    def __init__(self, grid, score, remaining_blocks, blocks, current_streak_mult=1, scored_this_round=False):
        self.grid = grid
        self.score = score
        self.remaining_blocks = remaining_blocks
        self.blocks = blocks
        self.g_cost = 0
        self.h_cost = 0
        self.parent = None
        self.last_move = None
        self.current_streak_mult = current_streak_mult
        self.scored_this_round = scored_this_round

    def __lt__(self, other):
        return (self.g_cost + self.h_cost) < (other.g_cost + other.h_cost)

    def get_f_cost(self):
        return self.g_cost + self.h_cost
    
    
    
    def set_remaining_blocks(self, blocks_remaining):
        self.remaining_blocks = blocks_remaining
        
    def get_remaining_blocks(self):
        return self.remaining_blocks
        
    
    