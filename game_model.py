from block import Block
from grid import Grid
from util import initialize_shapes
from random import Random
from tile import GridTile


class GameModel:
    """
    The GameModel class represents the game model for a grid-based game.
    It manages the game state, including the grid, score, and current shapes.

    Attributes:
        grid_size (int): Size of the game grid (default: 8)
        grid (Grid): The game grid object
        score (int): Current player score
        blocks (list): All available block shapes
        current_shapes (list): Currently available shapes for placement
        seed (any): Random seed for reproducible games
        rng (Random): Random number generator
        scored_this_round (bool): Whether points were scored in the current round
        ongoing_streak_mult (int): Score multiplier for consecutive clears
    """

    def __init__(self, grid_size=8, seed=None) -> None:
        """
        Initialize a new GameModel instance.

        Args:
            grid_size (int, optional): Size of the game grid (default is 8).
            seed (any, optional): Seed for the random number generator to ensure reproducibility.
        """
        self.grid_size = grid_size
        self.grid = Grid(grid_size)
        self.score = 0
        self.blocks = initialize_shapes()
        self.current_shapes = []
        self.seed = seed
        self.rng = Random(seed)
        self.scored_this_round = False
        self.ongoing_streak_mult = 1

    def start_game(self):
        """
        Initialize or restart the game. Resets the grid, score, streak, and 
        generates three new random shapes for placement.
        """
        # Initialize the game state
        self.grid = Grid(self.grid_size)
        self.score = 0
        self.current_shapes = []
        self.ongoing_streak_mult = 1
        self.scored_this_round = False

        # Generate three random shapes
        for i in range(3):
            shape = self._get_random_shape()
            self.current_shapes.append(shape)

    def check_game_over(self):
        """
        Check if the game is over. The game ends when none of the current shapes 
        can be placed anywhere on the grid.

        Returns:
            bool: True if no valid placements are possible; False otherwise.
        """
        if not self.current_shapes:
            return False  # No shapes to check

        for shape in self.current_shapes:
            # Check every possible position on the grid
            for row in range(8):
                for col in range(8):
                    if self.can_place_block(row, col, shape):
                        return False  # Found a valid placement

        return True

    def _new_round(self):
        """
        Starts a new round by generating three new placeable shapes.
        Resets the score multiplier if no points were scored in the last round.
        
        Returns:
            bool: True if the game ends after this round; False otherwise.

        Raises:
            Exception: If new round is started before placing all current blocks.
        """
        if self.current_shapes != []:
            raise Exception("You need to place the blocks before starting a new round")

        # Get three new shapes
        while len(self.current_shapes) < 3:
            shape = self._get_random_shape()
            if self.can_be_placed(shape):
                self.current_shapes.append(shape)
        if not self.scored_this_round:
            self.ongoing_streak_mult = 1

        # Check if the game is over and handle it appropriately
        if self.check_game_over():
            print("Game Over! Final Score:", self.score)
            return True

        return False  # Game continues

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
            self._new_round()

        # Check for full rows and columns
        full_rows = self._check_full_rows()
        full_cols = self._check_full_cols()

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
        """
        Check if a block can be legally placed on the grid at the given position.

        Args:
            row (int): Starting row index.
            col (int): Starting column index.
            block (Block): The block to check.

        Returns:
            bool: True if the block fits without overlapping or going out of bounds.
        """
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

    def can_be_placed(self, block:Block):
        """
        Check if a block can be placed anywhere on the grid.

        Args:
            block (Block): The block to check.

        Returns:
            bool: True if the block can be placed; False otherwise.
        """
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.can_place_block(row, col, block):
                    return True
        return False

    def _check_full_rows(self):
        """
        Check for fully occupied rows in the grid.

        Returns:
            list: List of row indices that are completely filled.
        """
        full_rows = []

        for row_i in range(self.grid_size):
            is_full = True
            row = self.grid.grid[row_i]

            for col_i in range(self.grid_size):
                tile: GridTile = row[col_i]
                if not tile.get_occupied():
                    is_full = False
                    break

            if is_full:
                full_rows.append(row_i)

        return full_rows

    def _check_full_cols(self):
        """
        Check for fully occupied columns in the grid.

        Returns:
            list: List of column indices that are completely filled.
        """
        full_cols = []

        for col_i in range(self.grid_size):
            is_full = True

            for row_i in range(self.grid_size):
                curr_tile: GridTile = self.grid.grid[row_i][col_i]

                if not curr_tile.get_occupied():
                    is_full = False
                    break

            if is_full:
                full_cols.append(col_i)

        return full_cols

    def _calculate_score(self, tiles_placed, rows_cleared, cols_cleared):
        """
        Calculate and update the score based on tiles placed and full lines cleared.
        Applies a streak multiplier for consecutive clears.

        Args:
            tiles_placed (int): Number of tiles placed by the block.
            rows_cleared (int): Number of full rows cleared.
            cols_cleared (int): Number of full columns cleared.
        """
        base_score = tiles_placed
        bonus = (rows_cleared + cols_cleared) * 10  # 10 points per cleared row/col

        bonus *= self.ongoing_streak_mult
        self.ongoing_streak_mult += 1
        self.scored_this_round = True

        self.score += base_score + bonus

    def _get_random_shape(self) -> Block:
        """
        Select a random block shape from the available pool.

        Returns:
            Block: A randomly selected block shape.
        """

        return self.blocks[self.rng.randint(0, len(self.blocks) - 1)]

    def get_grid(self):
        return self.grid

    def get_score(self):
        return self.score

    def get_current_shapes(self):
        return self.current_shapes

    def get_seed(self):
        return self.seed

    def set_seed(self, seed):
        self.seed = seed
        self.rng = Random(seed)

    def get_current_streak_mult(self):
        return self.ongoing_streak_mult

    def get_scored_this_round(self):
        return self.scored_this_round

    def get_blocks(self):
        return self.blocks
