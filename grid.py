from tile import GridTile


"""
Class to represent the playing grid of the game
"""


class Grid:
    def __init__(self, grid_size=8) -> None:
        self.grid_size = grid_size
        self.grid = self._initialize_grid(grid_size)

    def _initialize_grid(self, grid_size):
        grid = []

        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                grid_tile = GridTile()
                row.append(grid_tile)
            grid.append(row)

        return grid

    def get_tile(self, row, col)->GridTile:
        return self.grid[row][col]

    def set_tile(self, row, col, tile_state):
        self.grid[row][col].set_state(tile_state)

    def get_size(self):
        return self.grid_size

    def check_full_rows(self):
        full_rows = []
        for row in range(self.grid_size):
            if all(self.grid[row][col].get_occupied() for col in range(self.grid_size)):
                full_rows.append(row)
        return full_rows

    def check_full_cols(self):
        full_cols = []
        for col in range(self.grid_size):
            if all(self.grid[row][col].get_occupied() for row in range(self.grid_size)):
                full_cols.append(col)
        return full_cols

    def clear_rows(self, rows):
        for row in rows:
            for col in range(self.grid_size):
                self.set_tile(row, col, False)
        
    def clear_cols(self, cols):
        for col in cols:
            for row in range(self.grid_size):
                self.set_tile(row, col, False)

    def clone(self):
        new_grid = Grid(self.grid_size)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                new_grid.set_tile(row, col, self.get_tile(row, col).get_occupied())
        return new_grid

    def __str__(self):
        display = ""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                tile: GridTile = self.grid[row][col]
                display += "X" if tile.get_occupied() else "-"
                display += " "
            display += "\n"
        return display