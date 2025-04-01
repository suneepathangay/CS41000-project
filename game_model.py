


class GridTile:
    
    def __init__(self) -> None:
        self.occupied=False
    
    def get_occupied(self):
        return self.occupied
    
    def set_state(self,tile_state):
        self.occupied=tile_state


class Grid:
    
    def __init__(self) -> None:
        self.grid=self.initialize_grid()
    
    
    def initialize_grid(self):
        grid=[]
        
        for i in range(8):
            row=[]
            for j in range(8):
                grid_tile=GridTile()
                row.append(grid_tile)
            grid.append(row)
        
        return grid

    def get_tile(self, row, col):
        return self.grid[row][col]
        
    def set_tile(self, row, col, tile_state):
        self.grid[row][col].set_state(tile_state)
    
class GameModel:
    def __init__(self) -> None:
        self.grid=Grid()
        self.score=0
        self.current_shapes=[]
    # place block (placing many tiles)
        # Check if each tile is free
    # Calculate score
    # Go to next round (get three new shapes)
    # Check if the game is over
    # 

    
            
        