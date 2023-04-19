import random
import numpy as np
import pickle
import time
import chess
import chess.engine
import tensorflow as tf
from board import Board
class DQNEngine:
    def __init__(self, color, learning_rate=0.001, discount_factor=0.99, exploration_rate=0.3, exploration_decay=0.9995, use_target_network=True):
        self.color = color
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.use_target_network = use_target_network
        self.piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}

        self.model = self.build_model()
        if self.use_target_network:
            self.target_model = self.build_model()
            self.update_target_network()

    def build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(8, 8, 6)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(1, activation=None)
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), loss='mse')
        return model

    def choose_move(self, board: Board):
        legal_board_moves = board.get_legal_moves_engine(self.color)
        state = self._board_to_array(board)

        if random.uniform(0, 1) < self.exploration_rate:
            moves = random.choice(legal_board_moves)
            ((pR,pF, move1,move2), move_name) = moves
            move = (move1,move2)
        else:
            print("studied move")
            q_values = self.model.predict(np.array([state]))
            q_values = q_values.reshape(-1)
            max_q_value = np.max(q_values)
            max_q_moves = [((pR,pF, move1,move2), move_name) for ((pR,pF, move1,move2), move_name), q_value in zip(legal_board_moves, q_values) if q_value == max_q_value]
            ((pR,pF, move1,move2), move_name) = random.choice(max_q_moves)
            move = (move1,move2)

        piece = board.tiles[pR][pF].piece 

        reward = self._get_reward(board,piece, move)
        temp_board = board.try_move(piece, board.tiles[move[0]][move[1]])
        next_state = self._board_to_array(temp_board)

        
        if self.use_target_network:
            target_q = reward + self.discount_factor * np.max(self.target_model.predict(np.array([next_state])).reshape(-1))
        else:
            target_q = reward + self.discount_factor * np.max(self.model.predict(np.array([next_state])).reshape(-1))

        self.model.fit(np.array([state]), np.array([target_q]), epochs=1, verbose=0)

        if self.use_target_network:
            if board.move_count % 10 == 0:
                self.update_target_network()

        self.exploration_rate *= self.exploration_decay

        return piece,move

    def update_target_network(self):
        self.target_model.set_weights(self.model.get_weights())

    def _board_to_array(self, board):
        # Convert the board to a 8x8x6 array
        # Each channel represents a type of piece and the current player
        arr = np.zeros((8, 8, 6))
        for r in range(8):
            for f in range(8):
                piece = board.tiles[r][f].piece
                if piece is not None:
                    symbol = piece.name[0].upper()
                    if piece.name == 'knight':
                        symbol = 'N'
                    index = 'PNBRQK'.index(symbol)
                    arr[r, f, index] = 1
                arr[r, f, 5] = self.color == board.turn
        return arr

    def _get_reward(self, board : Board, piece, move):
        reward = 0
        captured_piece = board.tiles[move[0]][move[1]].piece

        symbol = piece.name[0].upper()
        if piece.name == 'knight':
            symbol = 'N'
        if captured_piece is not None:
            reward += self.piece_values[symbol]

        if board.last_move != None:
            temp_board = board.try_move(piece, board.tiles[move[0]][move[1]])

            is_check = temp_board.is_in_check(self.color)
            is_checkmate = temp_board.is_checkmate()
            is_stalemate = temp_board.check_for_stalemate()

            if is_checkmate:
                reward += 100
            elif is_stalemate:
                reward += 10
            elif is_check:
                reward += 0.5

        return reward

    def save_model(self, filename):
        self.model.save(filename)


    def load_model(self, filename):
        self.model = tf.keras.models.load_model(filename)
        if self.use_target_network:
            self.target_model = self.build_model()
            self.update_target_network()


	