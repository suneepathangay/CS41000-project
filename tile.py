

class GridTile:
    
    def __init__(self) -> None:
        self.occupied=False
        self.color = None
    
    def get_occupied(self):
        return self.occupied
    
    def set_state(self,tile_state):
        self.occupied=tile_state
        
            