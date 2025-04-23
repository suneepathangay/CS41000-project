from game_model import GameModel
from algorithms.AStar import AStar
from algorithms.Expectimax import Expectimax
from util import print_curr_state


def main():
    # Create a new game model
    game = GameModel(grid_size=6, seed=42)
    astar = AStar()
    expectimax = Expectimax()

    game.start_game()

    print("Initial game state:")
    print(f"Score: {game.get_score()}")
    print(f"Available blocks: {len(game.get_current_shapes())}")
    print_curr_state(game.get_grid().grid)

    # Iterate through a few rounds
    for i in range(4):
        print("Iteration", i + 1)
        # Get the best move
        best_moves = astar.get_best_moves(game)
        # best_moves = expectimax.get_best_moves(game)

        if best_moves:
            for shape in game.get_current_shapes():
                shape.visualize()
                print("\n")

            for move in best_moves:
                block_idx, block, row, col = move
                print(f"Block: {block.shape}, Position: ({row}, {col}).")

                # Apply the move
                game.place_block(row, col, block)
                print(game.grid.visualize())

            print("\nAfter applying the best moves:")
            print(f"Score: {game.get_score()}")
            print(f"Available blocks: {len(game.get_current_shapes())}")
        else:
            print("\nNo valid moves found!")


if __name__ == "__main__":
    main()
