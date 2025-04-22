from tile import GridTile
from block import Block


"""
Contains useful util methods
"""


def visualize_block(block: Block):
    # Getting the frame dimensions
    width = max([coor[1] for coor in block.indices]) + 1
    height = max([coor[0] for coor in block.indices]) + 1
    
    # Initialize a proper 2D array filled with spaces
    display_arr = [[" " for _ in range(width)] for _ in range(height)]
    
    # Place 'B' characters at block coordinates
    for coor in block.indices:
        row, col = coor[0], coor[1]
        display_arr[row][col] = "B"
    
    # Convert to display string
    display_str = ""
    for row in display_arr:
        display_str += " ".join(row) + "\n"
    
    return display_str


"""
Prints the current state of the game board
"""


def print_curr_state(grid):
    display = ""

    for row in range(len(grid)):
        for col in range(len(grid[row])):
            tile: GridTile = grid[row][col]
            if tile.get_occupied():
                display += "X"
            else:
                display += "-"
            display += " "

        display += "\n"

    return display


def initialize_shapes():
    rotations = [0, 90, 180, 270]

    blocks = []

    # 3x3 square
    blocks.append(
        Block(
            "3x3 Square",
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
        )
    )
    # 5x1 line
    blocks.append(Block("5x1 Line", [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]))
    # 1x5 line
    blocks.append(Block("1x5 Line", [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]))
    # 3x3 corner(s)
    base_indices = [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]
    for degrees in rotations:
        block = Block(f"3x3 Corner {degrees}", base_indices.copy())
        block.rotate(degrees)
        blocks.append(block)
    # 3x2 rectangle
    blocks.append(
        Block("3x2 Rectangle", [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)])
    )
    # 2x3 rectangle
    blocks.append(
        Block("2x3 Rectangle", [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)])
    )
    # 2x2 square
    blocks.append(Block("2x2 Square", [(0, 0), (0, 1), (1, 0), (1, 1)]))
    # 2x1 rectangle
    blocks.append(Block("2x1 Rectangle", [(0, 0), (0, 1)]))
    blocks.append(Block("2x1 Rectangle Inverted", [(0, 0), (1, 0)]))

    # 2x2 corner(s)
    base_indices = [(0, 0), (0, 1), (1, 0)]
    for degrees in rotations:
        block = Block(f"2x2 Corner {degrees}", base_indices.copy())
        block.rotate(degrees)
        blocks.append(block)

    # 2x3 corner
    base_indices = [(0, 0), (0, 1), (0, 2), (1, 0)]
    for degrees in rotations:
        block = Block(f"2x3 Corner {degrees}", base_indices.copy())
        block.rotate(degrees)
        blocks.append(block)

    # 3x2 corner
    base_indices = [(0, 0), (0, 1), (1, 0), (2, 0)]
    for degrees in rotations:
        block = Block(f"3x2 Corner {degrees}", base_indices.copy())
        block.rotate(degrees)
        blocks.append(block)

    # 2x2 diagonal(s)
    blocks.append(Block("2x2 Diagonal", [(0, 0), (1, 1)]))
    blocks.append(Block("2x2 Diagonal Inverted", [(1, 0), (0, 1)]))
    # 3x3 diagonal(s)
    blocks.append(Block("3x3 Diagonal", [(0, 0), (1, 1), (2, 2)]))
    blocks.append(Block("3x3 Diagonal Inverted", [(2, 0), (1, 1), (0, 2)]))
    # 1x1 square
    blocks.append(Block("1x1 Square", [(0, 0)]))

    return blocks
