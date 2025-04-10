from game_model import GameModel
from util import print_curr_state, print_block






model = GameModel()

grid_arr = model.get_grid().grid
model.start_game()

display = print_curr_state(grid=grid_arr)
print(display)

current_blocks = model.get_current_shapes()

print("Your Current Blocks are\n")

display_blocks=print_block(current_blocks[0])

for block in current_blocks:
    display_blocks=print_block(block)
    print(display_blocks)


model.place_block(row=0, col=0, block=current_blocks[0])
grid_arr = model.get_grid().grid
display = print_curr_state(grid=grid_arr)
print(display)




