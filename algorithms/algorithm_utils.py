from copy import deepcopy
from game_state import GameState


def evaluate(state):
    """
    Heuristic evaluation function for a game state.
    Higher score indicates a better state.
    Tries to approximate the game's scoring behavior.
    """
    empty_spaces = 0
    potential_rows_cleared = 0
    potential_cols_cleared = 0
    isolated_spaces = 0
    grid = state.grid.grid
    grid_size = state.grid.get_size()

    # Analyze rows and columns for potential clears
    for row in range(grid_size):
        row_filled = True
        for col in range(grid_size):
            if not grid[row][col].get_occupied():
                empty_spaces += 1
                row_filled = False
        if row_filled:
            potential_rows_cleared += 1

    for col in range(grid_size):
        col_filled = True
        for row in range(grid_size):
            if not grid[row][col].get_occupied():
                col_filled = False
                break
        if col_filled:
            potential_cols_cleared += 1

    # Check for isolated empty cells (no orthogonal neighbors)
    for row in range(grid_size):
        for col in range(grid_size):
            if not grid[row][col].get_occupied():
                has_neighbor = False
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < grid_size and 0 <= nc < grid_size:
                        if grid[nr][nc].get_occupied():
                            has_neighbor = True
                            break
                if not has_neighbor:
                    isolated_spaces += 1

    # Estimate scoring opportunity
    lines_cleared = potential_rows_cleared + potential_cols_cleared
    line_clear_bonus = lines_cleared * 10

    if not state.scored_this_round and state.current_streak_mult > 1:
        # Protect multiplier — reward more heavily
        line_clear_bonus *= state.current_streak_mult * 2.5
    else:
        line_clear_bonus *= state.current_streak_mult

    # empty space is good (placement opportunity)
    # isolated spaces are bad (hard to fill)
    placement_bonus = empty_spaces * 1.0
    isolation_penalty = isolated_spaces * 3.0

    large_shape_penalty = 0
    for shape in state.remaining_blocks:
        size = len(shape.indices)
        if size >= 5:
            large_shape_penalty += size * 1.5
    return placement_bonus + line_clear_bonus - isolation_penalty - large_shape_penalty

def get_possible_moves(state):
    """
    Get all possible moves for the current blocks
    """
    moves = []
    grid = state.grid.grid
    if hasattr(state.remaining_blocks, "__iter__"):
        # It's already iterable
        blocks = list(state.remaining_blocks)
    else:
        # It's a single block, wrap it in a list
        blocks = [state.remaining_blocks]

    for block_idx, block in enumerate(blocks):
        for row in range(state.grid.get_size()):
            for col in range(state.grid.get_size()):
                can_place = True
                for dr, dc in block.indices:
                    nr, nc = row + dr, col + dc
                    if (
                        nr >= state.grid.get_size()
                        or nc >= state.grid.get_size()
                        or grid[nr][nc].get_occupied()
                    ):
                        can_place = False
                        break

                if can_place:
                    moves.append((block_idx, block, row, col))

    return moves


def apply_move(state, move):
    """
    Apply a move to the state and return the new state
    """
    block_idx, block, row, col = move
    if hasattr(state.remaining_blocks, "__iter__"):
        # It's already iterable
        blocks = list(state.remaining_blocks).copy()
    else:
        # It's a single block, wrap it in a list
        blocks = [state.remaining_blocks].copy()

    new_state = GameState(
        deepcopy(state.grid),
        state.score,
        blocks,
        state.blocks,
        state.current_streak_mult,
        state.scored_this_round,
    )

    # Place the block
    for dr, dc in block.indices:
        new_state.grid.set_tile(row + dr, col + dc, True)

    # Remove used block
    new_state.remaining_blocks.pop(block_idx)

    # Update score
    tiles_placed = len(block.indices)
    rows_cleared = len(new_state.grid.check_full_rows())
    cols_cleared = len(new_state.grid.check_full_cols())
    new_state.score += tiles_placed + (rows_cleared + cols_cleared) * 10

    return new_state


def get_possible_blocks(grid, blocks):
    """
    Get all possible blocks that can be placed on the grid
    """
    possible_blocks = []
    for block in blocks:
        if _can_place_block(grid, block):
            possible_blocks.append((block))
    return possible_blocks

    return possible_blocks


def _can_place_block(grid, block) -> bool:
    for row in range(grid.get_size()):
        for col in range(grid.get_size()):
            can_place = True
            block_indices = block.indices
            for i in block_indices:
                # Check if block is out of bounds
                if (
                    row + i[0] < 0
                    or row + i[0] >= grid.get_size()
                    or col + i[1] < 0
                    or col + i[1] >= grid.get_size()
                ):
                    can_place = False
                    break
                # Check if tile is already occupied
                tile = grid.get_tile(row + i[0], col + i[1])
                if tile.get_occupied():
                    can_place = False
                    break
            if can_place:
                return True
    return False
