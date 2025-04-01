


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

    def get_grid(self):
        return self.grid

    def get_score(self):
        return self.score

    def get_current_shapes(self):
        return self.current_shapes

    def new_round(self):
        # Get three new shapes
        # Check if the game is over
        pass

    def place_block(self, block):
        # Check if the block can be placed
        # Place the block on the grid
        # Update the score
        pass

    def check_game_over(self):
        # Check if there are any empty tiles left
        # Check if there are any blocks that can be placed
        pass

    def check_block_placement(self, block):
        # Check if the block can be placed on the grid
        # Check if the block is within the grid boundaries
        # Check if the block overlaps with any occupied tiles
        pass

    def calculate_score(self):
        # Calculate the score based on the number of tiles occupied
        # and the number of blocks placed
        pass

    
            
        