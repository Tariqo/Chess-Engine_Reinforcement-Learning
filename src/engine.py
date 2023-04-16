
from board import Board
import random

class Engine:
    def __init__(self,color):
        self.color = color
        self.legal_moves = []

    def choose_move(self,board : Board):
        legal_pieces = board.get_legal_moves_random(self.color)


        piece,moves = random.choice(legal_pieces)


        return piece, random.choice(moves)
    

