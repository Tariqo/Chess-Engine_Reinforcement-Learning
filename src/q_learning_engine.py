import random
import math
import numpy as np
import tensorflow as tf
from piece import *
from board import Board
from stockfish import Stockfish

class DQNEngine:
    def __init__(self, color, learning_rate=0.001, discount_factor=0.99, exploration_rate=0.1, exploration_decay=0.9995, use_target_network=True):
        self.color = color
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.use_target_network = use_target_network
        self.piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        depth = 10
        if color == 'black':
            self.exploration_rate = 1
            self.sfish = Stockfish(path="Stockfish/stockfish-windows-2022-x86-64-avx2")
            self.sfish.set_elo_rating(2)

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
            if self.color == 'black':
                self.sfish.set_fen_position(board.save_to_FEN())
                top3_moves = [i['Move'] for i in self.sfish.get_top_moves(3)]
                move_str = random.choice(top3_moves)
                #uci = chr(97 + piece.file) + str(ROWS - piece.rank) + chr(97 + mv[1]) + str(ROWS - mv[0])
                pR,pF = (8 - int(move_str[1])) , ord(move_str[0]) - ord('a') 
                move = (8 - int(move_str[3])) , ord(move_str[2]) - ord('a')
            else:
                # print(move_str, pR,pF ,move)
                moves = random.choice(legal_board_moves)
                ((pR,pF, move1,move2), move_name) = moves
                move = (move1,move2)
        else:
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
        
        if captured_piece is not None:
            symbol = captured_piece.name[0].upper()
            if piece.name == 'knight':
                symbol = 'N'
            reward += self.piece_values[symbol]

        self_sym  = piece.name[0].upper() if piece.name != 'knight' else 'N' 
        opp_color = 'black' if piece.color == 'white' else 'white'

        #if in an attacked square, bad move
        if move in board.update_attacked_squares(opp_color):
            reward -= self.piece_values[self_sym]

        #Encourage Development
        if board.move_count < 10:
            if isinstance(piece, Knight):
                if piece.color == 'black' and move in [(2,2), (2,5)]:
                    reward += 0.3
                elif piece.color == 'white' and move in [(5,2), (5,5)]:
                    reward += 0.3

            if isinstance(piece, Bishop):
                if piece.color == 'black' and move in [(3,2), (4,1),(3,5),(4,6)]:
                    reward += 0.3
                elif piece.color == 'white' and move in [(4,5), (3,6), (4,2), (3,1)]:
                    reward += 0.3

            if isinstance(piece,Pawn):
                if move in [(3,2),(3,3),(3,4), (4,2),(4,3),(4,4)]:
                    reward += 0.3
            if isinstance(piece, King):
                if piece.castle_left and not piece.blocking_left and move == piece.castle_left_tile:
                    reward += 2
                    
                elif piece.castle_right and not piece.blocking_right and move == piece.castle_right_tile:
                    reward += 2
                else:
                    reward -= 2
            
        
        if board.move_count > 40:
            #we want to give more reward for moves that result in the king being more threatening 
            if isinstance(piece, King):

                if (
                    piece.color == 'black' and 
                    math.sqrt(((board.white_k.file - board.black_k.file)**2) + ((board.white_k.rank - board.black_k.rank)**2)) < 
                    math.sqrt(((board.white_k.rank - move[1])**2) + ((board.white_k.rank - move[0])**2))
                    ):
                    reward += 0.3
                    
                elif (
                    piece.color == 'white' and 
                    math.sqrt(((board.black_k.file - board.white_k.file)**2) + ((board.black_k.rank - board.white_k.rank)**2)) < 
                    math.sqrt(((board.black_k.file - move[1])**2) + ((board.black_k.rank - move[0])**2))
                    ):
                    reward += 0.3


        if isinstance(piece,Pawn) and (move[0] == 0 or move[0] == 7):
            reward += 3

                
        temp_board = board.try_move(piece, board.tiles[move[0]][move[1]])

        is_check = temp_board.is_in_check(self.color)
        is_checkmate = temp_board.is_checkmate()
        is_stalemate = temp_board.check_for_stalemate()

        if is_checkmate:
            reward += 5
        elif is_stalemate:
            reward -= 1
        elif is_check:
            reward += 0.3
        # self.get_eval(temp_board)
        return reward
    
    def get_eval(self, board):
        import chess
        import chess.engine
        newBoard = chess.Board(board.save_to_FEN())
        engine = chess.engine.SimpleEngine.popen_uci("Stockfish/stockfish-windows-2022-x86-64-avx2")
        result = engine.analyse(newBoard, chess.engine.Limit(time=0.01))
        print(result['score'])
        return result['score']

    def save_model(self, filename):
        self.model.save(filename)


    def load_model(self, filename):
        self.model = tf.keras.models.load_model(filename)
        if self.use_target_network:
            self.target_model = self.build_model()
            self.update_target_network()


	