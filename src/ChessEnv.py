import gym
import math
import chess
import random
import numpy as np
import chess.engine
from board import Board
from piece import Pawn,King, Knight, Bishop
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3 import PPO

class ChessEnv(gym.Env):
    def __init__(self):
        self.board = Board()
        self.action_space = gym.spaces.Discrete(4096)
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(64, 8, 8), dtype=np.float32)
        self.board_to_dict()
    
    def board_to_dict(self):
        action_space_dict = {}
        for row in self.board.tiles:
            for tile in row:
                if tile.has_piece() and tile.piece.color == self.board.turn:
                    action_space_dict[(tile.row,tile.col)] = self.board.piece_legal_moves(tile.piece)
        self.action_space = gym.spaces.Dict(action_space_dict)

    def reset(self):
        self.board = Board()
        return self.board_to_observation()

    def step(self, action):
        move = self.action_to_move(action)
        piece, tile = self.board.tiles[move[0]][move[1]].piece, self.board.tiles[move[2]][move[3]]
        self.board.move_piece()
        done, _ = self.board.check_for_game_end()
        reward = self.get_reward(piece, (move[2],move[3]))
        return self.board_to_observation(), reward, done, {}

    def board_to_observation(self):
        new_board = chess.Board(self.board.save_to_FEN())
        board_array = np.zeros((64, 8, 8), dtype=np.float32)
        for square in chess.SQUARES:
            piece = new_board.piece_at(square)
            if piece is not None:
                board_array[piece.piece_type - 1, square // 8, square % 8] = piece.color + 1
        if new_board.turn == chess.BLACK:
            board_array = board_array[:, ::-1, :]
        return board_array

    def action_to_move(self, action):
        print(action)
        move = chess.Move((action // 64) % 8 + (action // 512) * 8, action % 8 + ((action // 8) % 8) * 8)
        return random.choice(list(self.board.legal_moves))

    def get_reward(self,piece, move):
        reward = 0
        captured_piece = self.board.tiles[move[0]][move[1]].piece
        
        if captured_piece is not None:
            symbol = captured_piece.name[0].upper()
            if piece.name == 'knight':
                symbol = 'N'
            reward += self.piece_values[symbol]

        self_sym  = piece.name[0].upper() if piece.name != 'knight' else 'N' 
        opp_color = 'black' if piece.color == 'white' else 'white'

        #if in an attacked square, bad move
        if move in self.board.update_attacked_squares(opp_color):
            reward -= self.piece_values[self_sym]

        #Encourage Development
        if self.board.move_count < 10:
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
            
        
        if self.board.move_count > 40:
            #we want to give more reward for moves that result in the king being more threatening 
            if isinstance(piece, King):

                if (
                    piece.color == 'black' and 
                    math.sqrt(((self.board.white_k.file - self.board.black_k.file)**2) + ((self.board.white_k.rank - self.board.black_k.rank)**2)) < 
                    math.sqrt(((self.board.white_k.rank - move[1])**2) + ((self.board.white_k.rank - move[0])**2))
                    ):
                    reward += 0.3
                    
                elif (
                    piece.color == 'white' and 
                    math.sqrt(((self.board.black_k.file - self.board.white_k.file)**2) + ((self.board.black_k.rank - self.board.white_k.rank)**2)) < 
                    math.sqrt(((self.board.black_k.file - move[1])**2) + ((self.board.black_k.rank - move[0])**2))
                    ):
                    reward += 0.3


        if isinstance(piece,Pawn) and (move[0] == 0 or move[0] == 7):
            reward += 3

                
        temp_board = self.board.try_move(piece, self.board.tiles[move[0]][move[1]])

        is_check = temp_board.is_in_check(self.color)
        is_checkmate = temp_board.is_checkmate()
        is_stalemate = temp_board.check_for_stalemate()

        if is_checkmate:
            reward += 5
        elif is_stalemate:
            reward -= 1
        elif is_check:
            reward += 0.3
        return reward

def train():
    env = make_vec_env(lambda: ChessEnv(), n_envs=1)
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=100)
    model.save("chess_model")

if __name__ == '__main__':
    train()
