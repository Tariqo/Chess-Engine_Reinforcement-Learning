import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest

from board import Board
from piece import Piece, Pawn, King, Queen, Rook, Bishop, Knight
from game_vars import *
from tile import Tile

class TestBoard(unittest.TestCase):
    def str_to_move(self, move : str):
        #d5d8
        return (ROWS - int(move[1]),ord(move[0]) - ord("a"),ROWS - int(move[3]),ord(move[2]) - ord("a"))

         

    def test_move_piece(self):
        board = Board()
        board.move_piece(board.tiles[6][0].piece,board.tiles[5][0])  
        self.assertIsNone(board.tiles[6][0].piece)
        self.assertIsInstance(board.tiles[5][0].piece, Pawn)

        board.move_piece(board.tiles[1][0].piece,board.tiles[2][0])  
        self.assertIsNone(board.tiles[1][0].piece)
        self.assertIsInstance(board.tiles[2][0].piece, Pawn)
        
        board.move_piece(board.tiles[6][1].piece,board.tiles[5][1]) 
        self.assertIsNone(board.tiles[6][1].piece)
        self.assertIsInstance(board.tiles[5][1].piece, Pawn)

        board.move_piece(board.tiles[1][1].piece,board.tiles[2][1]) 
        self.assertIsNone(board.tiles[1][1].piece)
        self.assertIsInstance(board.tiles[2][1].piece, Pawn)
        
        board.move_piece(board.tiles[6][2].piece,board.tiles[5][2]) 
        self.assertIsNone(board.tiles[6][2].piece)
        self.assertIsInstance(board.tiles[5][2].piece, Pawn)

        board.move_piece(board.tiles[1][2].piece,board.tiles[2][2])
        self.assertIsNone(board.tiles[1][2].piece)
        self.assertIsInstance(board.tiles[2][2].piece, Pawn)

        
        
        
    def test_move_piece_en_passant(self):
        board = Board()
        board.move_piece(board.tiles[6][4].piece,board.tiles[4][4], True) #move white pawn two squares 
        board.move_piece(board.tiles[4][4].piece,board.tiles[3][4], True) #move white pawn one more square
        board.move_piece(board.tiles[1][3].piece,board.tiles[3][3]) #move black pawn 


        self.assertTrue(board.move_piece(board.tiles[3][4].piece, board.tiles[2][3]))
        self.assertIsNone(board.tiles[3][3].piece)

    def test_move_piece_pawn_promotion(self):
        board = Board(testing=True)
        pawn = Pawn("white", 1,0)
        board.tiles[1][0].set_piece(pawn)
        # self.assertTrue(False)
        self.assertTrue(board.move_piece(pawn, board.tiles[0][0]))
        self.assertIsInstance(board.tiles[0][0].piece, Queen)

    def test_move_piece_castling_left(self):
        board = Board()
        self.assertFalse(board.move_piece(board.white_k, board.tiles[7][2])) #cant castle left with piece in between
        board.tiles[7][3].set_piece(None)
        board.tiles[7][2].set_piece(None)
        board.tiles[7][1].set_piece(None)
        board.update_castling()
        self.assertTrue(board.move_piece(board.white_k, board.tiles[7][2])) #can castle left when there are no pieces in between
        self.assertIsInstance(board.tiles[7][2].piece, King)
        self.assertIsInstance(board.tiles[7][3].piece, Rook)

        del(board)

        #test castling when rook moves
        board = Board()
        self.assertFalse(board.move_piece(board.white_k, board.tiles[7][2])) #cant castle left with piece in between
        board.tiles[7][3].set_piece(None)
        board.tiles[7][2].set_piece(None)
        board.tiles[7][1].set_piece(None)
        self.assertTrue(board.move_piece(board.tiles[7][0].piece, board.tiles[7][2])) 
        self.assertTrue(board.move_piece(board.tiles[1][0].piece, board.tiles[3][0])) 
        self.assertTrue(board.move_piece(board.tiles[7][2].piece, board.tiles[7][0])) 
        self.assertFalse(board.move_piece(board.white_k, board.tiles[7][2])) 



    
    def test_move_piece_castling_right(self):
        board = Board()
        self.assertFalse(board.move_piece(board.white_k, board.tiles[7][6])) #cant castle right with piece in between
        board.tiles[7][5].set_piece(None)
        board.tiles[7][6].set_piece(None)
        board.update_castling()
        self.assertTrue(board.move_piece(board.white_k, board.tiles[7][6])) #can castle left when there are no pieces in between
        self.assertIsInstance(board.tiles[7][6].piece, King)
        self.assertIsInstance(board.tiles[7][5].piece, Rook)
        del(board)
        
        
        #test castling when rook moves
        board = Board()
        self.assertFalse(board.move_piece(board.white_k, board.tiles[7][2])) #cant castle left with piece in between
        board.tiles[7][5].set_piece(None)
        board.tiles[7][6].set_piece(None)
        self.assertTrue(board.move_piece(board.tiles[7][7].piece, board.tiles[7][5])) 
        self.assertTrue(board.move_piece(board.tiles[1][0].piece, board.tiles[3][0])) 
        self.assertTrue(board.move_piece(board.tiles[7][5].piece, board.tiles[7][7])) 
        self.assertFalse(board.move_piece(board.white_k, board.tiles[7][2])) #cant castle left with piece in between


    def test_piece_legal_moves(self):
        board = Board(testing=True)
        pawn = Pawn("white", 6,0)
        board.tiles[6][0].set_piece(pawn)
        legal_moves = board.piece_legal_moves(pawn)
        expected_moves = [(5, 0), (4, 0)]
        self.assertCountEqual(legal_moves, expected_moves)

    def test_load_from_FEN(self):
        # Test 1: Starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board = Board(fen=fen)
        self.assertIsInstance(board.tiles[0][0].piece, Rook)
        self.assertIsInstance(board.tiles[0][1].piece, Knight)
        self.assertIsInstance(board.tiles[0][2].piece, Bishop)
        self.assertIsInstance(board.tiles[0][3].piece, Queen)
        self.assertIsInstance(board.tiles[0][4].piece, King)
        self.assertIsInstance(board.tiles[0][5].piece, Bishop)
        self.assertIsInstance(board.tiles[0][6].piece, Knight)
        self.assertIsInstance(board.tiles[0][7].piece, Rook)
        for i in range(8):
            self.assertIsInstance(board.tiles[1][i].piece, Pawn)

        self.assertEqual(board.turn, "white")
        self.assertTrue(board.white_k.castle_left)
        self.assertTrue(board.white_k.castle_right)
        self.assertTrue(board.black_k.castle_left)
        self.assertTrue(board.black_k.castle_right)
        self.assertEqual(board.move_count, 1)

        # Test 2: FEN with en passant square
        fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq e6 0 3"
        board = Board(fen=fen)
        self.assertEqual(board.tiles[3][4].piece.name, "pawn")
        self.assertTrue(board.tiles[2][4].can_en_passant(-1))
        self.assertEqual(board.turn, "white")
        self.assertEqual(board.move_count, 3)
        
        fen = "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R/ b QKqk d3 2 4"
        board = Board(fen=fen)
        self.assertEqual(board.tiles[4][3].piece.name, "pawn")
        self.assertTrue(board.tiles[5][3].can_en_passant(1))
        self.assertEqual(board.turn, "black")
        self.assertEqual(board.move_count, 4)

        # Test 3: FEN with no castling rights
        fen = "r3k2r/pp1bppbp/2n1qnp1/2pp4/2P5/2N1PN2/PP1B1PPP/R2QKB1R b - - 1 8"
        board = Board(fen=fen)
        self.assertEqual(board.white_k.castle_left, False)
        self.assertEqual(board.white_k.castle_right, False)
        self.assertEqual(board.black_k.castle_left, False)
        self.assertEqual(board.black_k.castle_right, False)
    
    def test_check_check_mate(self):
        with open("./test/mate_in_one.txt", "r") as file:
            fen_strs = file.read()
            fen_strs_parts = fen_strs.split(',')
            for i in range(0,len(fen_strs_parts),2):
                from_rank,from_file,to_rank,to_file = self.str_to_move(fen_strs_parts[i+1]) 
                board = Board(fen=fen_strs_parts[i])
                board.move_piece(board.tiles[from_rank][from_file].piece, board.tiles[to_rank][to_file])
                board.check_for_check()
                self.assertTrue(board.check_for_checkmate(True))
        
if __name__ == '__main__':
    unittest.main()
