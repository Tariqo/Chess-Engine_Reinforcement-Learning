import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import numpy as np
from board import Board
from q_agent import Q_learning, Agent

class TestQEngine(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.engine = Q_learning(self.board, 'black')

    
    def test_init(self):
        self.assertEqual(self.engine.memory, [])
        self.assertEqual(self.engine.memsize, 1000)
        self.assertEqual(self.engine.reward_trace, [])
        self.assertEqual(self.engine.sampling_probs, [])
        self.assertEqual(self.engine.color, 'black')
    
    def test_init_network(self):
        self.engine.agent.init_network()
        model = self.engine.agent.model
        self.assertIsNotNone(model)
    
    def test_fix_model(self):
        agent = Agent()
        agent.fix_model()
        self.assertEqual(len(agent.fixed_model.layers), 7)

    def test_get_action_values(self):
        agent = Agent()
        state = np.zeros((1, 8, 8, 8))
        action_values = agent.get_action_values(state)
        self.assertEqual(action_values.shape, (1, 4096))

    def test_save_load_model(self):
        self.engine.agent.save_model()
        loaded_engine = Q_learning(self.board,'black')
        loaded_engine.agent.load_model('')
        self.assertIsNotNone(loaded_engine.agent.model)
    
if __name__ == '__main__':
    unittest.main()
