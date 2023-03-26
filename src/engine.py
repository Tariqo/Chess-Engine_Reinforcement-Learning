
from board import Board
import random

class Engine:
    def __init__(self,color):
        self.color = color
        self.legal_moves = []

    def choose_move(self,board : Board):
        legal_pieces = board.get_legal_moves(self.color)


        piece,moves = legal_pieces[random.randint(0,len(legal_pieces)-1)]


        return piece,moves[random.randint(0, len(moves)-1)]
    

