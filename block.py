class Block:
    def __init__(self, shape, indices) -> None:
        self.shape = shape
        self.indices = indices
        self.rotation = 0

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
        self.rotation = (self.rotation + degrees) % 360

    def visualize(self):
        # Create an empty grid filled with dots
        grid_size = (
            max(x for x, y in self.indices) + 1,
            max(y for x, y in self.indices) + 1,
        )
        grid = [["." for _ in range(grid_size[1])] for _ in range(grid_size[0])]

        # Mark block positions with 'X'
        for r, c in self.indices:
            if 0 <= r < grid_size[0] and 0 <= c < grid_size[1]:  # Ensure within bounds
                grid[r][c] = "X"

        # Print the grid
        for row in grid:
            print(" ".join(row))
