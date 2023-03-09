import pygame
import os
from piece import *
from game_vars import *
from square import *

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')      
        # cnt = 0
        # for row in self.squares:
        #     for sqr in row:
        #         cnt +=1
        #         print(sqr.piece, cnt)

    
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
         # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color,row_pawn,col))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color,row_other,1))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color,row_other,6))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color,row_other,2))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color,row_other,5))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color,row_other,0))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color,row_other,7))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color,row_other,3))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color,row_other,4))
    
