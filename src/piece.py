class Piece:
    def __init__(self, name, value, color, sprite=None):
        self.row = rank
        self.column = file
        self.name = name
        self.color = color
        self.color_val = 1 if color == "black" else -1
        self.value = value * color_val
        self.dir = color_val
        self.legal_moves = []
        self.selected = False
        self.sprite = sprite

class Pawn(Piece):
    def __init__(self, color):
        self.can_en_passant = False
        super().__init__('pawn', color, 1.0)

class King(Piece):
    def __init__(self, color):
        self.castle_left = False
        self.castle_right = False
        super().__init__('king', color, 9999.9)

class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.0)

class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.0)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__('bishop', color, 3.0)

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)