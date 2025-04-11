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


class Block:
    def __init__(self, shape, indices) -> None:
        self.shape=shape
        self.indices=indices

    def rotate(self, degrees=0):
        """Rotates block around the pivot by 90, 180, or 270 degrees and shifts to avoid negative indices."""
        new_indices = []

        for x, y in self.indices:
            # Apply rotation based on degrees
            if degrees == 90:
                x, y = (-y, x)
            elif degrees == 180:
                x, y = (-x, -y)
            elif degrees == 270:
                x, y = (y, -x)

            new_indices.append((x, y))

        # Find minimum row and column
        min_x = min(x for x, y in new_indices)
        min_y = min(y for x, y in new_indices)

        # Compute shift to keep indices non-negative
        shift_x = -min_x if min_x < 0 else 0
        shift_y = -min_y if min_y < 0 else 0

        self.indices = [(x + shift_x, y + shift_y) for x, y in new_indices]

    def visualize(self, grid_size=(5, 5)):
        # Create an empty grid filled with dots
        grid = [['.' for _ in range(grid_size[1])] for _ in range(grid_size[0])]

        # Mark block positions with 'X'
        for r, c in self.indices:
            if 0 <= r < grid_size[0] and 0 <= c < grid_size[1]:  # Ensure within bounds
                grid[r][c] = 'X'

        # Print the grid
        for row in grid:
            print(' '.join(row))
        print()

class GameModel:
    """
        The GameModel class represents the game model for a grid-based game.
        It manages the game state, including the grid, score, and current shapes.
    """

    def __init__(self) -> None:
        self.grid=Grid()
        self.score=0
        self.blocks=[]
        self.current_shapes=[]

    def start_game(self):
        # Initialize the game state
        self.grid=Grid()
        self.score=0
        self.current_shapes=[]



        # Generate three random shapes
        for _ in range(3):
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
        for _ in range(3):
            shape=self.get_random_shape()
            self.current_shapes.append(shape)
        # Check if the game is over
        self.check_game_over()
        pass

    def place_block(self, row, col, block):
        # Check if the block can be placed
        block_indices = block.indices

        # Place the block on the grid
        # Update the score
        pass

    def can_place_block(self, row, col, block):
        # Check if the block can be placed on the grid
        block_indices = block.indices
        # TODO: implement block logic
        for i in block_indices:
            if row + i[0] < 0 or row + i[0] >= 8 or col + i[1] < 0 or col + i[1] >= 8:
                return False
            tile = self.grid.get_tile(row + i[0], col + i[1])
            if tile.get_occupied():
                return False
        return True
        # Check if the block is within the grid boundaries
        # Check if the block overlaps with any occupied tiles
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

    def get_random_shape(self):
        # Generate a random shape
        # Return the shape
        pass

    def initialize_shapes(self):
        rotations = [0, 90, 180, 270]
        # 3x3 square
        self.blocks.append(Block("3x3 Square", [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]))
        # 5x1 line
        self.blocks.append(Block("5x1 Line", [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]))
        # 1x5 line
        self.blocks.append(Block("1x5 Line", [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]))
        # 3x3 corner(s)
        base_indices = [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]
        for degrees in rotations:
            block = Block(f"3x3 Corner {degrees}", base_indices.copy())
            block.rotate(degrees)
            self.blocks.append(block)
        # 3x2 rectangle
        self.blocks.append(Block("3x2 Rectangle", [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]))
        # 2x3 rectangle
        self.blocks.append(Block("2x3 Rectangle", [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]))
        # 2x2 square
        self.blocks.append(Block("2x2 Square", [(0, 0), (0, 1), (1, 0), (1, 1)]))
        # 2x1 rectangle
        self.blocks.append(Block("2x1 Rectangle", [(0, 0), (0, 1)]))
        self.blocks.append(Block("2x1 Rectangle", [(0, 0), (1, 0)]))
        # 2x2 corner(s)
        base_indices = [(0, 0), (0, 1), (1, 0)]
        for degrees in rotations:
            block = Block(f"2x2 Corner {degrees}", base_indices.copy())
            block.rotate(degrees)
            self.blocks.append(block)
        # 2x3 corner
        base_indices = [(0, 0), (0, 1), (0, 2), (1, 0)]
        for degrees in rotations:
            block = Block(f"2x3 Corner {degrees}", base_indices.copy())
            block.rotate(degrees)
            self.blocks.append(block)
        # 3x2 corner
        base_indices = [(0, 0), (0, 1), (1, 0), (2, 0)]
        for degrees in rotations:
            block = Block(f"3x2 Corner {degrees}", base_indices.copy())
            block.rotate(degrees)
            self.blocks.append(block)
        # 2x2 diagonal(s)
        self.blocks.append(Block("2x2 Diagonal", [(0, 0), (1, 1)]))
        self.blocks.append(Block("2x2 Diagonal", [(1, 0), (0, 1)]))
        # 3x3 diagonal(s)
        self.blocks.append(Block("3x3 Diagonal", [(0, 0), (1, 1), (2, 2)]))
        self.blocks.append(Block("3x3 Diagonal", [(2, 0), (1, 1), (0, 2)]))
        # 1x1 square
        self.blocks.append(Block("1x1 Square", [(0, 0)]))

        for block in self.blocks:
            block.visualize()

GameModel().initialize_shapes()

    
            
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
        