import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from board import Board
from q_learning_engine import DQNEngine

class TestDQNEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DQNEngine('white')

    def test_build_model(self):
        model = self.engine.build_model()
        self.assertIsNotNone(model)

    def test_board_to_array(self):
        board = Board()
        arr = self.engine._board_to_array(board)
        self.assertEqual(arr.shape, (8, 8, 6))

    def test_get_reward(self):
        board = Board()
        piece = board.tiles[6][4].piece
        move = (4,4)
        reward = self.engine._get_reward(board, piece, move)
        self.assertEqual(reward, 0)

    def test_choose_move(self):
        board = Board()
        piece, move = self.engine.choose_move(board)
        self.assertIsNotNone(piece)
        self.assertIsNotNone(move)

    def test_save_load_model(self):
        self.engine.save_model('test_model.h5')
        loaded_engine = DQNEngine('white')
        loaded_engine.load_model('test_model.h5')
        self.assertIsNotNone(loaded_engine.model)
        self.assertIsNotNone(loaded_engine.target_model)

if __name__ == '__main__':
    unittest.main()
