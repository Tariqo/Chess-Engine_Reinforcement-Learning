import os
import pygame
from game_vars import *
class Piece:
    def __init__(self,rank, file, name, color, value, sprt_name):
        self.rank = rank
        self.file = file
        self.name = name
        self.color = color
        self.color_val = 1 if color == "black" else -1
        self.value = value * self.color_val
        self.dir = self.color_val
        self.legal_moves = []
        self.selected = False
        self.sprite_load = pygame.image.load(os.path.join(IMAGE_DIR, sprt_name + '.png'))
        self.sprite = pygame.transform.scale(self.sprite_load, (80 , 80))
    # def _load_sprite(self, sprt_name):
    #     self.sprite = 
    #     print(self.sprite)
    
    def draw(self, display):
        piece_img = self.sprite
        img_center = self.file * SQSIZE + SQSIZE // 2, self.rank * SQSIZE + SQSIZE // 2
        img_rect = piece_img.get_rect(center=img_center)
        display.blit(piece_img,img_rect)


class Pawn(Piece):
    def __init__(self, color, rank = 0, file= 0):
        self.can_en_passant = False
        super().__init__( rank , file,'pawn', color, 1.0, 'bP' if color == 'black' else 'wP')

class King(Piece):
    def __init__(self, color, rank = 0, file= 0):
        self.castle_left = False
        self.castle_right = False
        super().__init__( rank , file,'king', color, 9999.9, 'bK' if color == 'black' else 'wK')

class Queen(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'queen', color, 9.0, 'bQ' if color == 'black' else 'wQ')

class Rook(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'rook', color, 5.0, 'bR' if color == 'black' else 'wR')

class Bishop(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'bishop', color, 3.0, 'bB' if color == 'black' else 'wB')

class Knight(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'knight', color, 3.0, 'bN' if color == 'black' else 'wN')