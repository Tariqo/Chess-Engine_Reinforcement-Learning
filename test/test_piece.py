import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


import unittest
from piece import Piece, Pawn, King, Queen, Rook, Bishop, Knight
from game_vars import *
from board import Board


class TestPiece(unittest.TestCase):
    
    def test_init(self):
        piece = Piece(0, 0, "pawn", "white", 1, "wp")
        self.assertEqual(piece.rank, 0)
        self.assertEqual(piece.file, 0)
        self.assertEqual(piece.name, "pawn")
        self.assertEqual(piece.color, "white")
        self.assertEqual(piece.color_val, -1)
        self.assertEqual(piece.value, -1)
        self.assertEqual(piece.dir, -1)
        self.assertEqual(piece.legals, [])
        self.assertEqual(piece.moved, False)        

    def test__moved(self):
        piece = Piece(0, 0, "pawn", "white", 1, "wp")
        piece._moved()
        self.assertEqual(piece.moved, True)
        self.assertEqual(piece.legals, [])
        
    def test_legal_straight_moves(self):
        piece = Piece(0, 0, "rook", "white", 5, "wr")
        # test vertical moves
        legals = piece.legal_straight_moves([(1,0), (-1,0)])
        self.assertIn((1,0), legals[0])  # check first inner list
        self.assertIn((3,0), legals[0])
        self.assertNotIn((0,3), legals[0])
        # test horizontal moves
        legals = piece.legal_straight_moves([(0,1), (0,-1)])
        self.assertIn((0,1), legals[1])  # check second inner list
        self.assertIn((0,2), legals[1])
        self.assertIn((0,3), legals[1])
        self.assertNotIn((2,0), legals[1])
        self.assertNotIn((3,0), legals[1])


    def test_pawn(self):
        board = Board(True)
        
        # test that a pawn can move one or two squares forward from starting position
        piece = Pawn("black", 1, 0)
        board.tiles[1][0].set_piece(piece)
        legals = board.piece_legal_moves(piece, True) 
        self.assertEqual(len(legals), 2)
        self.assertIn((2,0), legals)
        self.assertIn((3,0), legals)

        # test that a pawn can capture diagonally
        board.tiles[2][1].set_piece(Piece(2, 1, "pawn", "white", 1, "bp"))
        legals = board.piece_legal_moves(piece, True) 
        self.assertEqual(len(legals), 3)
        self.assertIn((2, 1), legals)
        self.assertNotIn((0, 1), legals)
        self.assertNotIn((1, 1), legals)

        # test that a pawn cannot move forward if there is a piece in front of it

        board.tiles[2][0].set_piece(Piece(2, 0, "pawn", "black", 1, "bp"))
        legals = board.piece_legal_moves(piece, True)
        # this test ended up causing a change in the code to not allow a pawn to move if another pawn is in front of it
        self.assertEqual(len(legals), 1)
        self.assertNotIn((2,0), legals)
        self.assertNotIn((3,0), legals)

        # test that a pawn can only move diagonally to capture 
        self.assertEqual(len(legals), 1)
        self.assertIn((2, 1), legals)


    def test_king(self):
        board = Board(True)
        # test that a king can move one square in any direction
        piece = King("white", 0, 4)
        legals = board.piece_legal_moves(piece, True) 
        self.assertEqual(len(legals), 5)
        self.assertIn((0, 3), legals)
        self.assertIn((1, 3), legals)
        self.assertIn((1, 4), legals)
        self.assertIn((1, 5), legals)
        self.assertIn((0, 5), legals)


    def test_queen(self):
        board = Board(True)
        # test that a queen can move in any direction
        piece = Queen("white", 3, 3)
        legals = board.piece_legal_moves(piece, True) 
        self.assertEqual(len(legals), 27)
        self.assertIn((3, 2), legals)
        self.assertIn((3, 4), legals)
        self.assertIn((2, 3), legals)
        self.assertIn((4, 3), legals)
        self.assertIn((2, 2), legals)
        self.assertIn((4, 4), legals)
        self.assertIn((2, 4), legals)
        self.assertIn((4, 2), legals)

        # test that a queen can't move in a blocked direction
        board.tiles[3][5].set_piece(Piece(3, 6, "pawn", "black", 1, "bp"))
        legals = board.piece_legal_moves(piece, True)
        self.assertEqual(len(legals), 25)
        self.assertIn((2, 4), legals)
        self.assertNotIn((3, 7), legals)

        # test that a queen can't move in a blocked direction
        board.tiles[4][4].set_piece(Piece(4, 4, "pawn", "white", 1, "bp"))
        legals = board.piece_legal_moves(piece, True)
        self.assertEqual(len(legals), 21)
        self.assertNotIn((4, 4), legals)


    def test_knight(self):
        board = Board(True)

        # test that a knight can move in an L-shape to any unoccupied square
        piece = Knight("white", 3, 3)
        legals = board.piece_legal_moves(piece, True)
        self.assertEqual(len(legals), 8)
        self.assertIn((1, 2), legals)
        self.assertIn((1, 4), legals)
        self.assertIn((2, 1), legals)
        self.assertIn((2, 5), legals)
        self.assertIn((4, 1), legals)
        self.assertIn((4, 5), legals)
        self.assertIn((5, 2), legals)
        self.assertIn((5, 4), legals)
        self.assertNotIn((6, 4), legals)

        # test that a knight can capture an opponent's piece
        board.tiles[1][2].set_piece(Piece(1, 2, "pawn", "black", 1, "bp"))
        legals = board.piece_legal_moves(piece, True)
        self.assertEqual(len(legals), 8)
        self.assertIn((1, 2), legals)

        # test that a knight cannot move to a square occupied by its own piece
        board.tiles[1][4].set_piece(Piece(1, 4, "knight", "white", 3, "wn"))
        legals = board.piece_legal_moves(piece, True)
        self.assertEqual(len(legals), 7)
        self.assertNotIn((1, 4), legals)
    
    def test_bishop(self):
        board = Board(True)

        # Test for diagonal movement restrictions
        piece = Bishop("white", 4, 4)
        board.tiles[4][4].set_piece(piece)

        legals = board.piece_legal_moves(piece, True)
        self.assertEqual(len(legals), 13)
        self.assertIn((3, 3), legals)
        self.assertIn((3, 5), legals)
        self.assertIn((5, 3), legals)
        self.assertIn((5, 5), legals)
        self.assertNotIn((4, 5), legals) # non-diagonal move
        board.tiles[3][3].set_piece(Piece(3, 3, "bishop", "white", 2, "wb"))
        self.assertNotIn((1, 2), legals) # same color piece blocking the move
        board.tiles[3][3].set_piece(Piece(3, 3, "pawn", "black", 2, "bp"))
        self.assertIn((2, 2), legals) # opposite color piece that can be captured

        # Test for valid capture moves
        board = Board(True)
        piece = Bishop("white", 4, 4)
        board.tiles[4][4].set_piece(piece)
        board.tiles[2][2].set_piece(Piece(2, 2, "pawn", "black", 1, "bp"))
        legals = board.piece_legal_moves(piece, True)
        self.assertIn((2, 2), legals) # bishop can capture the pawn
        self.assertNotIn((1, 1), legals) # outside of capture range
        board.tiles[1][3].set_piece(Piece(1, 3, "bishop", "white", 2, "wb"))
        legals = board.piece_legal_moves(piece, True)
        self.assertNotIn((1, 3), legals) # same color piece blocking the move

        # Test for edge cases
        board = Board(True)

        piece1 = Bishop("white", 0, 0)
        piece2 = Bishop("white", 0, 7)
        piece3 = Bishop("white", 7, 0)
        piece4 = Bishop("white", 7, 7)
        piece5 = Bishop("white", 4, 4)

        board.tiles[0][0].set_piece(piece1)
        legals = board.piece_legal_moves(piece1, True)
        self.assertIn((7, 7), legals) # bishop can move to opposite corner
        board.tiles[0][0].set_piece(None)

        board.tiles[0][7].set_piece(piece2)
        legals = board.piece_legal_moves(piece2, True)
        self.assertIn((7, 0), legals) # bishop can move to opposite corner
        board.tiles[0][7].set_piece(None)

        board.tiles[7][0].set_piece(piece3)
        legals = board.piece_legal_moves(piece3, True)
        self.assertIn((0, 7), legals) # bishop can move to opposite corner
        board.tiles[7][0].set_piece(None)

        board.tiles[7][7].set_piece(piece4)
        legals = board.piece_legal_moves(piece4, True)
        self.assertIn((0, 0), legals) # bishop can move to opposite corner
        board.tiles[7][7].set_piece(None)



        board.tiles[4][4].set_piece(piece5)
        legals = board.piece_legal_moves(piece5, True)
        self.assertIn((2, 2), legals) # bishop can move to adjacent center square

    def test_rook_horizontal_movement(self):
        board = Board(True)
        rook = Rook("white", 3, 3)
        board.tiles[3][3].set_piece(rook)

        # test one step movement horizontally
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 14)
        self.assertIn((3, 0), legals)
        self.assertIn((3, 1), legals)
        self.assertIn((3, 2), legals)
        self.assertIn((3, 4), legals)
        self.assertIn((3, 5), legals)
        self.assertIn((3, 6), legals)
        self.assertIn((3, 7), legals)
        self.assertIn((0, 3), legals)
        self.assertIn((1, 3), legals)
        self.assertIn((2, 3), legals)
        self.assertIn((4, 3), legals)
        self.assertIn((5, 3), legals)
        self.assertIn((6, 3), legals)
        self.assertIn((7, 3), legals)

        self.assertNotIn((3, 8), legals)
        self.assertNotIn((3, 9), legals)
        self.assertNotIn((3, 10), legals)

        # test diagonal movement
        board.tiles[4][4].set_piece(Piece(4, 4, "pawn", "white", 1, "wp"))
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 14)
        self.assertNotIn((4, 4), legals)

        # test movement to a square occupied by another piece of the same color
        board.tiles[3][6].set_piece(Piece(3, 6, "rook", "white", 3, "wr"))
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 12)
        self.assertNotIn((3, 6), legals)

        # test capture
        board.tiles[3][0].set_piece(Piece(3, 0, "pawn", "black", 1, "bp"))
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 12)
        self.assertIn((3, 0), legals)
    
    def test_rook_vertical_movement(self):
        board = Board(True)
        rook = Rook("white", 3, 3)
        board.tiles[3][3].set_piece(rook)

        # test# test diagonal movement
        board.tiles[4][4].set_piece(Piece(4, 4, "pawn", "white", 1, "wp"))
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 14)
        self.assertNotIn((4, 4), legals)

        # test same color piece on the way
        board.tiles[6][3].set_piece(Piece(6, 3, "bishop", "white", 3, "wb"))
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 12)
        self.assertNotIn((7, 3), legals)

        # test opponent's piece to capture
        board.tiles[1][3].set_piece(Piece(1, 3, "knight", "black", 1, "bn"))
        legals = board.piece_legal_moves(rook, True)
        self.assertEqual(len(legals), 11)
        self.assertIn((1, 3), legals)
        self.assertNotIn((10, 3), legals)


if __name__ == "__main__":
    unittest.main()
