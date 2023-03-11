
class Tile:
    def __init__(self, row, col, piece = None):
        self.row=row
        self.col = col
        self.piece = piece
        self.en_passant_legal = False
    
    def reset_passant(self):
        self.en_passant_legal = False

    def has_piece(self):
        return self.piece != None
    
    def set_piece(self, piece):
        self.piece = piece

    def piece_moved(self):
        self.piece = None
    
    def can_en_passant(self):
        return self.en_passant_legal

    def set_en_passant(self):
        self.en_passant_legal = True
