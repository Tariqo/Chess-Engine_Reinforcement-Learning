import pygame
import os
from piece import *
from game_vars import *
from tile import *


class Board:

    def __init__(self):
        self.tiles = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self.white_k = self.tiles[7][4].piece
        self.white_check = False
        self._add_pieces('black')
        self.black_k = self.tiles[0][4].piece
        self.black_check = False
        self.try_move_piece = None
        # cnt = 0
        # for row in self.tiles:
        #     for sqr in row:
        #         cnt +=1

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.tiles[row][col] = Tile(row, col)

    def reset_en_passant_board(self, color):
        for i in self.tiles:
            for j in i:
                if color == j.en_passant_color:
                    j.reset_passant()
                

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
         # pawns
        for col in range(COLS):
            self.tiles[row_pawn][col] = Tile(
                row_pawn, col, Pawn(color, row_pawn, col))

        # knights
        self.tiles[row_other][1] = Tile(
            row_other, 1, Knight(color, row_other, 1))
        self.tiles[row_other][6] = Tile(
            row_other, 6, Knight(color, row_other, 6))

        # bishops
        self.tiles[row_other][2] = Tile(
            row_other, 2, Bishop(color, row_other, 2))
        self.tiles[row_other][5] = Tile(
            row_other, 5, Bishop(color, row_other, 5))

        # rooks
        self.tiles[row_other][0] = Tile(
            row_other, 0, Rook(color, row_other, 0))
        self.tiles[row_other][7] = Tile(
            row_other, 7, Rook(color, row_other, 7))

        # queen
        self.tiles[row_other][3] = Tile(
            row_other, 3, Queen(color, row_other, 3))

        # king
        self.tiles[row_other][4] = Tile(
            row_other, 4, King(color, row_other, 4))

    def triggerPromotion(self, rank, file, color):
        self.tiles[rank][file].piece = Queen(color, rank, file)

    def check_for_check(self):
        if self.last_move.color == 'black':
            if (self.white_k.rank, self.white_k.file) in self.last_move.legal_moves_pre_check(self):
                print("white in check")
                self.white_check = True
        else:
            if (self.black_k.rank, self.black_k.file) in self.last_move.legal_moves_pre_check(self):
                print("black in check")
                self.black_check = True
        self.check_for_checkmate()

    def check_white_k_in_check(self):
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "black":
                        if (self.white_k.rank, self.white_k.file) in tile.piece.legal_moves_pre_check(self):
                            return True

    def check_black_k_in_check(self):
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "white":
                        if (self.black_k.rank, self.black_k.file) in tile.piece.legal_moves_pre_check(self):
                            return True

    def try_move(self, r, f, lr, lf):
        # save older tile's piece
        self.try_move_piece = self.tiles[lr][lf].piece

        piece = self.tiles[r][f].piece
        self.tiles[r][f].piece_moved
        self.tiles[r][f].set_piece(None)

        piece.rank, piece.file = lr,lf
        self.tiles[lr][lf].set_piece(piece)

        
    def undo_move(self, r,f,lr,lf):
        piece = self.tiles[lr][lf].piece
        self.tiles[lr][lf].piece_moved
        self.tiles[lr][lf].set_piece(None)
        piece.rank, piece.file = r,f
        self.tiles[r][f].set_piece(piece)


        # load older tile's piece
        self.tiles[lr][lf].set_piece(self.try_move_piece)

        # for i in self.tiles:
        #     for j in i:
        #         if not j.has_piece():
        #             print("blank", end=" ")
        #         else:
        #             print(j.piece.name, end=" ")
        #     print("\n------")
        
        
    def check_for_move_uncheck(self, r,f, lr,lf):
        self.try_move(r,f, lr,lf)

        if self.white_check:
            # if still in check return bad move
            if self.check_white_k_in_check():
                self.undo_move(r,f, lr,lf)
                return False
        elif self.black_check:
            if self.check_black_k_in_check():
                self.undo_move(r,f, lr,lf)
                return False
        self.undo_move(r,f, lr,lf)
        return True

    def check_pin_move(self,r,f, lr,lf):
        self.try_move(r,f,lr, lf)
        if self.tiles[lr][lf].piece.color == 'white':
            if self.check_white_k_in_check():
                self.undo_move(r,f,lr, lf)
                return False
            else:
                self.undo_move(r,f,lr, lf)
                return True
        else:
            if self.check_black_k_in_check():
                self.undo_move(r,f,lr, lf)
                return False
            else:
                self.undo_move(r,f,lr, lf)
                return True
            
    def get_in_check(self, color):
        return  not self.white_check if color == "white" else not self.black_check
    
    def check_for_checkmate(self):
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == check_mate_color:
                    if len(tile.piece.legal_moves(self)) >0:
                        print("not checkmate")
                        return False
        print("checkmate#")
        return True
    
    def check_for_stalemate(self):
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == check_mate_color:
                    if len(tile.piece.legal_moves(self)) >0:
                        print("not stalemate")
                        return False
        print("stalemate, DRAW!")
        return True
    
    def get_legal_moves(self,color):
        pieces = []
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == color:
                    if len(tile.piece.legal_moves(self)) > 0:
                        pieces.append((tile.piece,tile.piece.legal_moves(self)))
        return pieces