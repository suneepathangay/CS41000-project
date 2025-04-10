from block import Block
from grid import Grid
from util import initialize_shapes
from random import randint
from tile import GridTile



"""
    The GameModel class represents the game model for a grid-based game.
    It manages the game state, including the grid, score, and current shapes.
"""

class GameModel:


    def __init__(self) -> None:
        self.grid=Grid()
        self.score=0
        self.blocks=initialize_shapes()
        self.current_shapes=[]

    def start_game(self):
        # Initialize the game state
        self.grid=Grid()
        self.score=0
        self.current_shapes=[]

        # Generate three random shapes
        for i in range(3):
            shape=self.get_random_shape()
            self.current_shapes.append(shape)
        
        

    def get_grid(self):
        return self.grid

    def get_score(self):
        return self.score

    def get_current_shapes(self):
        return self.current_shapes

    def new_round(self):
        # Get three new shapes (where it is possible to win the game?)
        for i in range(3):
            shape=self.get_random_shape()
            self.current_shapes.append(shape)
        # Check if the game is over
        self.check_game_over()

    
    """
    Method to place the block on the board 
    """

    def place_block(self, row, col, block:Block):
        # Update the score
        if not self.can_place_block(row, col, block):
            return False  # Invalid placement

            # Place the block on the grid
        for dr, dc in block.indices:
            self.grid.set_tile(row + dr, col + dc, True)

        # Check for full rows and columns
        full_rows = self.check_full_rows()
        full_cols = self.check_full_cols()



        # Clear full rows
        for r in full_rows:
            for c in range(8):
                self.grid.set_tile(r, c, False)

        # Clear full columns
        for c in full_cols:
            for r in range(8):
                self.grid.set_tile(r, c, False)

        # Update score
        self.calculate_score(len(block.indices), len(full_rows), len(full_cols))

        return True
    
    def can_place_block(self, row, col, block):

        block_indices = block.indices

        for i in block_indices:
            if row + i[0] < 0 or row + i[0] >= 8 or col + i[1] < 0 or col + i[1] >= 8:
                return False
            tile = self.grid.get_tile(row + i[0], col + i[1])
            if tile.get_occupied():
                return False
        return True
        
    def check_full_rows(self):
        
        full_rows=[]
        
        for row_i in range(len(self.grid.grid)):
            
            is_full=True
            row=self.grid.grid[row_i]
            
            for col_i in range(len(row)):
                tile:GridTile = row[col_i]

                if not tile.get_occupied():
                    is_full = False
                    break
                
            if is_full:
                full_rows.append(row_i)
        
        return full_rows
    
    def check_full_cols(self):
        
        full_cols=[]
        
        for col_i in range(8):
            
            col=[]
            
            is_full = True
            
            for row_i in range(len(self.grid.grid)):
                col.append(self.grid.grid[row_i][col_i])
            
            for i in range(len(col)):

                curr_tile: GridTile = col[i]
                
                if not curr_tile.get_occupied():
                    is_full = False
                    break

            if is_full:
                full_cols.append(col_i)
            
        return full_cols
            
        
    def check_game_over(self):
        # Check if there are any empty tiles left
        # Check if there are any blocks that can be placed
        pass


    def calculate_score(self, tiles_placed, rows_cleared, cols_cleared):
        # Calculate the score based on the number of tiles occupied
        # and the number of blocks placed
        base_score = tiles_placed
        bonus = (rows_cleared + cols_cleared) * 10  # 10 points per cleared row/col
        self.score += base_score + bonus

    def get_random_shape(self):
        # Generate a random shape
        # Return the shape
        
        return self.blocks[randint(0,len(self.blocks)-1)]
    
    

   

# GameModel().initialize_shapes()
        

# GameModel().initialize_shapes()
        