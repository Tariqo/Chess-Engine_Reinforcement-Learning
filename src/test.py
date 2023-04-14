import random
import numpy as np
import pickle
import time
class QLearningEngine:
    def __init__(self, color, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.9995):
        self.color = color
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}


    def choose_move(self, board):
        legal_moves = board.get_legal_moves(self.color)
        state = self._board_to_state(board)

        if random.uniform(0, 1) < self.exploration_rate:
            piece, moves = random.choice(legal_moves)
            move = random.choice(moves)
        else:
            max_q_value = float('-inf')
            piece, move = None, None
            for p, moves in legal_moves:
                for m in moves:
                    q_value = self.q_table.get((state, (p.rank, p.file, m[0], m[1])), 0)
                    if q_value > max_q_value:
                        max_q_value = q_value
                        piece, move = p, m

        pR, pF = piece.rank, piece.file
        prev_state = state
        board.engine_try_move(pR, pF, move[0], move[1])
        new_state = self._board_to_state(board)
        board.engine_undo_move(pR, pF, move[0], move[1])
        reward = self._get_reward(board, piece, move)
        max_future_q = max([self.q_table.get((new_state, (p.rank, p.file, m[0], m[1])), 0) for p, moves in legal_moves for m in moves])
        current_q = self.q_table.get((prev_state, (piece.rank, piece.file, move[0], move[1])), 0)

        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_future_q - current_q)
        self.q_table[(prev_state, (piece.rank, piece.file, move[0], move[1]))] = new_q
        self.exploration_rate *= self.exploration_decay
        return piece, move


    def _board_to_state(self, board):
        state = ""
        for row in board.tiles:
            for tile in row:
                if tile.has_piece():
                    state += str(tile.piece.name[0].upper())
                else:
                    state += " "
        return state
    

    
    def _get_reward(self, board, piece, move):
        pR, pF = piece.rank, piece.file
        is_capture = board.tiles[move[0]][move[1]].has_piece()
        captured_piece_value = 0
        
        if is_capture:
            captured_piece = board.tiles[move[0]][move[1]].piece
            captured_piece_value = self.piece_values[(captured_piece.name[0]).upper()]

        board.engine_try_move(pR, pF, move[0], move[1])

        is_check = board.is_in_check(self.color)
        is_checkmate = board.is_checkmate(self.color)
        board.engine_undo_move(pR, pF, move[0], move[1])

        reward = 0

        if is_capture:
            reward += captured_piece_value
            print("captured")
        
        if is_check:
            reward += 0.5

        if is_checkmate:
            reward += 100
            	

        return reward

    import pickle
    
    def save_q_table(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_q_table(self, filename):
        with open(filename, 'rb') as f:
            self.q_table = pickle.load(f)

import random
import numpy as np
import pickle
import time

class QLearningEngine:
    def __init__(self, color, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.9995):
        self.color = color
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        self.state_history = []

    def choose_move(self, board):
        legal_moves = board.get_legal_moves(self.color)
        state = self._board_to_state(board)

        if random.uniform(0, 1) < self.exploration_rate:
            piece, moves = random.choice(legal_moves)
            move = random.choice(moves)
        else:
            max_q_value = float('-inf')
            piece, move = None, None
            for p, moves in legal_moves:
                for m in moves:
                    q_value = self.q_table.get((state, (p.rank, p.file, m[0], m[1])), 0)
                    if q_value > max_q_value:
                        max_q_value = q_value
                        piece, move = p, m

        pR, pF = piece.rank, piece.file
        prev_state = state
        board.engine_try_move(pR, pF, move[0], move[1])
        new_state = self._board_to_state(board)
        board.engine_undo_move(pR, pF, move[0], move[1])
        reward = self._get_reward(board, piece, move)
        max_future_q = max([self.q_table.get((new_state, (p.rank, p.file, m[0], m[1])), 0) for p, moves in legal_moves for m in moves])
        current_q = self.q_table.get((prev_state, (piece.rank, piece.file, move[0], move[1])), 0)

        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_future_q - current_q)
        self.q_table[(prev_state, (piece.rank, piece.file, move[0], move[1]))] = new_q
        
        # Add the current state and action to the state history
        self.state_history.append((prev_state, (piece.rank, piece.file, move[0], move[1])))
        
        self.exploration_rate *= self.exploration_decay
        return piece, move

    def learn(self):
        # Update the Q-values for all (state, action) pairs in the state history
        for state, action in self.state_history:
            reward = self._get_reward(board, piece, move)
            max_future_q = max([self.q_table.get((new_state, (p.rank, p.file, m[0], m[1])), 0) for p, moves in legal_moves for m in moves])
            current_q = self.q_table.get((state, action), 0)
            new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_future_q - current_q)
            self.q_table[(state, action)] = new_q
        self.state_history = []

    def _board_to_state(self, board):
        state = ""
        for
class QLearningEngine:
    def __init__(self, color, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0, exploration_decay=0.9995):
        self.color = color
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        self.last_state = None
        self.last_action = None

    def choose_move(self, board):
        legal_moves = board.get_legal_moves(self.color)
        state = self._board_to_state(board)

        if random.uniform(0, 1) < self.exploration_rate:
            piece, moves = random.choice(legal_moves)
            move = random.choice(moves)
        else:
            max_q_value = float('-inf')
            piece, move = None, None
            for p, moves in legal_moves:
                for m in moves:
                    q_value = self.q_table.get((state, (p.rank, p.file, m[0], m[1])), 0)
                    if q_value > max_q_value:
                        max_q_value = q_value
                        piece, move = p, m

        pR, pF = piece.rank, piece.file
        prev_state = state
        board.engine_try_move(pR, pF, move[0], move[1])
        new_state = self._board_to_state(board)
        board.engine_undo_move(pR, pF, move[0], move[1])
        reward = self._get_reward(board, piece, move)
        max_future_q = max([self.q_table.get((new_state, (p.rank, p.file, m[0], m[1])), 0) for p, moves in legal_moves for m in moves])
        current_q = self.q_table.get((prev_state, (piece.rank, piece.file, move[0], move[1])), 0)

        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_future_q - current_q)
        self.q_table[(prev_state, (piece.rank, piece.file, move[0], move[1]))] = new_q
        self.exploration_rate *= self.exploration_decay

        # store last state and action for experience replay
        self.last_state = prev_state
        self.last_action = (piece.rank, piece.file, move[0], move[1])

        return piece, move

    def experience_replay(self, board, batch_size=32):
        # if there is no last action, then there is no experience to replay
        if not self.last_action:
            return

        # sample a batch of previous states and actions from the Q-table
        prev_states = []
        actions = []
        rewards = []
        next_states = []
        legal_moves = board.get_legal_moves(self.color)

        for i in range(batch_size):
            # select a random legal move
            piece, moves = random.choice(legal_moves)
            move = random.choice(moves)
            pR, pF = piece.rank, piece.file

            # apply the move and record the resulting state and reward
            board.engine_try_move(pR, pF, move[0], move[1])
            prev_state = self._board_to_state(board)
            reward = self._