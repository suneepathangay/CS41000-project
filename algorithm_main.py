from game_model import GameModel
from algorithms.AStar import AStar
from algorithms.Expectimax import Expectimax
from algorithms.MCTS import MCTS
from util import print_curr_state

def simulate_game(algorithm, seed=None, debug=False, iterations=5):
    """
    Simulate a game using the specified algorithm
    """
    print("\nSimulating game with algorithm:", algorithm.__class__.__name__)
    game = GameModel(grid_size=6, seed=seed)
    game.start_game()

    if debug:
        print("Initial game state:")
        print(f"Score: {game.get_score()}")
        print(f"Available blocks: {len(game.get_current_shapes())}")
        print_curr_state(game.get_grid().grid)

    # Iterate through a few rounds
    for i in range(iterations):
        if debug:
            print("Iteration", i + 1)
        # Get the best move
        best_moves = algorithm.get_best_moves(game)

        if best_moves:
            if debug:
                for shape in game.get_current_shapes():
                    shape.visualize()
                    print("\n")

            for move in best_moves:
                block_idx, block, row, col = move
                if debug:
                    print(f"Block: {block.shape}, Position: ({row}, {col}).")

                # Apply the move
                game.place_block(row, col, block)
                if debug:
                    print(game.grid.visualize())
            if debug:
                print(f"\nAfter applying the best moves: {game.get_score()}")
        else:
            print("No valid moves found!")
            break
    print(f"Final score for algorithm {algorithm.__class__.__name__} with seed {seed} over {iterations} iterations: {game.get_score()}")


def main():
    astar = AStar()
    expectimax = Expectimax()
    mcts = MCTS()

    seeds = [None, 42, 123, 456, 789]
    iterations = [3, 5, 10]
    # Simulate the game with different seeds
    for seed in seeds:
        for iteration in iterations:
            print(f"\nSimulating game with seed {seed} over {iteration} iterations:")
            simulate_game(astar, seed, debug=False, iterations=iteration)
            simulate_game(expectimax, seed, debug=False, iterations=iteration)
            simulate_game(mcts, seed, debug=False, iterations=iteration)
            print("\n" + "="*50)



if __name__ == "__main__":
    main()
