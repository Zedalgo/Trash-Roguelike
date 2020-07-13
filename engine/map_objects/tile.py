class Tile:
    #A tile on the map, may or may not be blocked, may or may not block LoS
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        #If a Tile is blocked, defaults to block LoS
        #Prob gonna need to edit later for grates or something
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        self.explored = False