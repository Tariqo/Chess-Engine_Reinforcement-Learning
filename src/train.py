from board import Board
from q_agent import Q_learning, Agent

board = Board()

agent = Agent()

R = Q_learning(board, 'black')

R.learn(iters=2)
