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
    def __init__(self, grid_size=8) -> None:
        self.grid_size = grid_size
        self.grid = Grid(grid_size)
        self.score = 0
        self.blocks = initialize_shapes()
        self.current_shapes = []
        self.scored_this_round = False
        self.ongoing_streak_mult = 1

    def start_game(self):
        # Initialize the game state
        self.grid = Grid(self.grid_size)
        self.score = 0
        self.current_shapes = []

        # Generate three random shapes
        for i in range(3):
            shape = self.get_random_shape()
            self.current_shapes.append(shape)

    def get_grid(self):
        return self.grid

    def get_score(self):
        return self.score

    def get_current_shapes(self):
        return self.current_shapes

    def new_round(self):
        if self.current_shapes != []:
            raise Exception("You need to place the blocks before starting a new round")

        # Get three new shapes
        for i in range(3):
            shape = self.get_random_shape()
            self.current_shapes.append(shape)
            if not self.scored_this_round:
                self.ongoing_streak_mult = 1
        
        # Check if the game is over and handle it appropriately
        if self.check_game_over():
            print("Game Over! Final Score:", self.score)
            return True  
    
        return False  # Game continues

    """
    Method to place the block on the board 
    """

    def place_block(self, row, col, block: Block):
        shape_index = -1
        for i, shape in enumerate(self.current_shapes):
            if shape.shape == block.shape:
                shape_index = i
                break
        if shape_index == -1:
            print("Block not in current shapes")
            print("Current shapes: ", self.current_shapes)
            print("Block: ", block.shape)
            return False

        # Check if the block can be placed
        if not self.can_place_block(row, col, block):
            return False  # Invalid placement

        # Place the block on the grid
        for dr, dc in block.indices:
            self.grid.set_tile(row + dr, col + dc, True)

        # Remove the used block from current_shapes
        self.current_shapes.pop(shape_index)
        if len(self.current_shapes) == 0:
            self.new_round()

        # Check for full rows and columns
        full_rows = self.check_full_rows()
        full_cols = self.check_full_cols()

        # Clear full rows
        for r in full_rows:
            for c in range(self.grid_size):
                self.grid.set_tile(r, c, False)

        # Clear full columns
        for c in full_cols:
            for r in range(self.grid_size):
                self.grid.set_tile(r, c, False)

        # Update score
        self.calculate_score(len(block.indices), len(full_rows), len(full_cols))

        return True

    def can_place_block(self, row, col, block: Block):
        block_indices = block.indices

        for i in block_indices:
            if (
                row + i[0] < 0
                or row + i[0] >= self.grid_size
                or col + i[1] < 0
                or col + i[1] >= self.grid_size
            ):
                return False
            tile = self.grid.get_tile(row + i[0], col + i[1])
            if tile.get_occupied():
                return False
        return True

    def check_full_rows(self):
        full_rows = []

        for row_i in range(len(self.grid.grid)):
            is_full = True
            row = self.grid.grid[row_i]

            for col_i in range(len(row)):
                tile: GridTile = row[col_i]

                if not tile.get_occupied():
                    is_full = False
                    break

            if is_full:
                full_rows.append(row_i)

        return full_rows

    def check_full_cols(self):
        full_cols = []

        for col_i in range(self.grid_size):
            col = []

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
        if not self.current_shapes:
            return False  # No shapes to check
        
        for shape in self.current_shapes:
            # Check every possible position on the grid
            for row in range(8):
                for col in range(8):
                    if self.can_place_block(row, col, shape):
                        return False  # Found a valid placement
    
        return True

    def calculate_score(self, tiles_placed, rows_cleared, cols_cleared):
        # Calculate the score based on the number of tiles occupied
        # and the number of blocks placed
        base_score = tiles_placed
        bonus = (rows_cleared + cols_cleared) * 10  # 10 points per cleared row/col

        bonus *= self.ongoing_streak_mult
        self.ongoing_streak_mult += 1
        self.scored_this_round = True

        self.score += base_score + bonus

    def get_random_shape(self) -> Block:
        # Generate a random shape
        # Return the shape

        return self.blocks[randint(0, len(self.blocks) - 1)]
