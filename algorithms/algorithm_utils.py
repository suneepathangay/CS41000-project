from copy import deepcopy
from game_state import GameState


def evaluate(state):
    """
    Evaluation function for a game state
    Higher score means better state
    """
    empty_spaces = 0
    potential_clears = 0
    grid = state.grid.grid

    # Count empty spaces and potential row/column clears
    for row in range(state.grid.get_size()):
        row_filled = True
        for col in range(state.grid.get_size()):
            if not grid[row][col].get_occupied():
                empty_spaces += 1
                row_filled = False
        if row_filled:
            potential_clears += 1

    for col in range(state.grid.get_size()):
        col_filled = True
        for row in range(state.grid.get_size()):
            if not grid[row][col].get_occupied():
                col_filled = False
                break
        if col_filled:
            potential_clears += 1

    # Count isolated spaces (empty cells without adjacent occupied cells)
    isolated_spaces = 0
    for row in range(state.grid.get_size()):
        for col in range(state.grid.get_size()):
            if not grid[row][col].get_occupied():
                has_neighbor = False
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = row + dr, col + dc
                    if (
                        0 <= nr < state.grid.get_size()
                        and 0 <= nc < state.grid.get_size()
                        and grid[nr][nc].get_occupied()
                    ):
                        has_neighbor = True
                        break
                if not has_neighbor:
                    isolated_spaces += 1

    base_score = -empty_spaces * 1.0 - potential_clears * 10.0 - isolated_spaces * 2.0

    streak_bonus = 0
    if state.current_streak_mult > 1 and not state.scored_this_round:
        # Heavily reward potential clears to avoid losing the multiplier
        streak_bonus = potential_clears * 25.0 * state.current_streak_mult
    else:
        # Still reward potential clears based on current multiplier
        streak_bonus = potential_clears * 5.0 * state.current_streak_mult

    return base_score + streak_bonus


def get_possible_moves(state):
    """
    Get all possible moves for the current blocks
    """
    moves = []
    grid = state.grid.grid
    if hasattr(state.remaining_blocks, '__iter__'):
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
    if hasattr(state.remaining_blocks, '__iter__'):
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