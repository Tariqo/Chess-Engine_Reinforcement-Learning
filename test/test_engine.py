import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from board import Board
from q_agent import Q_learning

class TestQ_learning(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.engine = Q_learning(self.board, 'black')

    def test_init_network(self):
        model = self.engine.init_network()
        self.assertIsNotNone(model)

    def test_choose_move(self):
        board = Board()
        piece, move = self.engine.choose_move(board)
        self.assertIsNotNone(piece)
        self.assertIsNotNone(move)

    def test_save_load_model(self):
        self.engine.save_model()
        loaded_engine = Q_learning(self.board,'black')
        loaded_engine.load_model()
        self.assertIsNotNone(loaded_engine.model)
        self.assertIsNotNone(loaded_engine.target_model)

if __name__ == '__main__':
    unittest.main()
