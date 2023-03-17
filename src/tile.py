
class Tile:
    def __init__(self, row, col, piece = None):
        self.row=row
        self.col = col
        self.piece = piece
        self.en_passant_legal = False
        self.en_passant_color = 1
    
    def reset_passant(self):
        self.en_passant_legal = False

    def has_piece(self):
        return self.piece != None
    
    def set_piece(self, piece):
        self.piece = piece

    def piece_moved(self):
        self.piece._moved()
        self.piece = None
    
    def can_en_passant(self, color):
        return self.en_passant_legal and color == self.en_passant_color

    def set_en_passant(self, color):
        self.en_passant_legal = True
        self.en_passant_color = color
