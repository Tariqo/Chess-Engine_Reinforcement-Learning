import pygame
import os
from piece import *
from game_vars import *
from tile import *

class Board:

    def __init__(self):
        self.tiles = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')      
        # cnt = 0
        # for row in self.tiles:
        #     for sqr in row:
        #         cnt +=1

    
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.tiles[row][col] = Tile(row, col)

    def reset_en_passant_board(self):
        for i in self.tiles:
            for j in i:
                j.reset_passant()
        
    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
         # pawns
        for col in range(COLS):
            self.tiles[row_pawn][col] = Tile(row_pawn, col, Pawn(color,row_pawn,col))

        # knights
        self.tiles[row_other][1] = Tile(row_other, 1, Knight(color,row_other,1))
        self.tiles[row_other][6] = Tile(row_other, 6, Knight(color,row_other,6))

        # bishops
        self.tiles[row_other][2] = Tile(row_other, 2, Bishop(color,row_other,2))
        self.tiles[row_other][5] = Tile(row_other, 5, Bishop(color,row_other,5))

        # rooks
        self.tiles[row_other][0] = Tile(row_other, 0, Rook(color,row_other,0))
        self.tiles[row_other][7] = Tile(row_other, 7, Rook(color,row_other,7))

        # queen
        self.tiles[row_other][3] = Tile(row_other, 3, Queen(color,row_other,3))

        # king
        self.tiles[row_other][4] = Tile(row_other, 4, King(color,row_other,4))
    
