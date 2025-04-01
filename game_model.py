


class GridTile:
    
    def __init__(self) -> None:
        self.occupied=False
    
    def get_occupied(self):
        return self.occupied
    
    def set_state(self,tile_state):
        self.occupied=tile_state


class Grid:
    
    def __init__(self) -> None:
        
        self.grid=self.initialize_grid()
    
    
    
    
    def initialize_grid(self):
        
        grid=[]
        
        for i in range(8):
            row=[]
            for j in range(8):
                grid_tile=GridTile()
                row.append(grid_tile)
            grid.append(row)
        
        return grid
            
            
            
        