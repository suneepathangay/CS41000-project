from tile import GridTile


"""
Class to represent the playing grid of the game
"""


class Grid:
    def __init__(self) -> None:
        self.grid = self.initialize_grid()

    def initialize_grid(self):
        grid = []

        for i in range(8):
            row = []
            for j in range(8):
                grid_tile = GridTile()
                row.append(grid_tile)
            grid.append(row)

        return grid

    def get_tile(self, row, col):
        return self.grid[row][col]

    def set_tile(self, row, col, tile_state):
        self.grid[row][col].set_state(tile_state)
