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
        self.engine_try_move_piece = None
        self.last_move_castle_left = False
        self.last_move_castle_right = False
        self.last_move_castle_left_engine = False
        self.last_move_castle_right_engine = False
        self.turn = ""
        self.move_count = 0
        # cnt = 0
        # for row in self.tiles:
        #     for sqr in row:
        #         cnt +=1
    def set_turn(self, num):
        self.move_count += 1
        if num == 1:
            self.turn == 'white'
        else:
            self.turn == 'black'
             
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
        # self.last_move.legals.clear()
        if self.last_move.color == 'black':
            self.white_check = self.check_white_k_in_check()
        else:
            self.black_check = self.check_black_k_in_check()
        if self.check_for_checkmate():
            return True
        else:
            return False
    def is_in_check(self, color):
        if color == 'white':
            return self.check_white_k_in_check()
        else:
            return self.check_black_k_in_check()
    
    def is_checkmate(self,color):
        return self.check_for_checkmate()
    def check_white_k_in_check(self):
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    if tile.piece.color == "black":
                        # tile.piece.legals.clear()
                        if (self.white_k.rank, self.white_k.file) in tile.piece.legal_moves_pre_check(self):
                            return True
        return False

    def check_black_k_in_check(self):
        for row in self.tiles:
            for tile in row:
                if tile.has_piece():
                    # tile.piece.legals.clear()
                    # sprint(tile.piece.color, tile.piece.name,tile.piece.legal_moves_pre_check(self))
                    if tile.piece.color == "white":
                        if (self.black_k.rank, self.black_k.file) in tile.piece.legal_moves_pre_check(self):
                            return True
        # print("-------------------------------")
        return False

    def try_move(self, r, f, lr, lf):
        # print("Trying Move: ", r,f,lr,lf)
        # for i in self.tiles:
        #     for j in i:
        #         if not j.has_piece():
        #             print("---", end=" ")
        #         else:
        #             name = j.piece.name[0].upper() if j.piece.name != 'knight' else 'N'
        #             print(j.piece.color[0].upper() + "-" + name, end=" ")
        #     print("\n ")
        # print("------------------------------------------------")        
        # # save older tile's piece
        self.try_move_piece = None
        self.try_move_piece = self.tiles[lr][lf].piece

        piece = self.tiles[r][f].piece
        piece.is_trying = True
        if isinstance(piece, King):
            # castle left
            piece.trying_move = True
            if (lr, lf) == piece.castle_left_tile and piece.can_castle_left():
                print(piece.color, "Tried to move to", "(", str(lr) + ","+ str(lf) + "),", "castle_left_tile is:  ", str(piece.castle_left_tile))
                self.tiles[lr][lf - 2].piece.file = lf + 1
                self.tiles[lr][lf + 1].set_piece(self.tiles[lr][lf - 2].piece)
                self.last_move_castle_left = True

            # castle right
            if (lr, lf) == piece.castle_right_tile and piece.can_castle_right():
                print(piece.color, "Tried to move to", "(", str(lr) + ","+ str(lf) + "),", "castle_right_tile is:  ", str(piece.castle_right_tile))
                self.tiles[lr][lf + 1].piece.file = lf - 1
                self.tiles[lr][lf - 1].set_piece(self.tiles[lr][lf + 1].piece)
                self.last_move_castle_right = True


        self.tiles[r][f].set_piece(self.tiles[r][f].piece)

        piece.rank, piece.file = lr,lf
        self.tiles[lr][lf].set_piece(None)
        self.tiles[lr][lf].set_piece(piece)
        self.tiles[lr][lf].piece.old_legals = self.tiles[lr][lf].piece.legals.copy()
        self.tiles[lr][lf].piece.legals.clear()
        self.tiles[lr][lf].piece.legal_moves_pre_check(self)

            
        
    def undo_move(self, r,f,lr,lf):
        piece = self.tiles[lr][lf].piece
        if isinstance(piece, King):
            piece.trying_move = False
            # castle left
            if self.last_move_castle_left:
                self.tiles[lr][lf + 1].piece.file = lf - 2
                self.tiles[lr][lf - 2].set_piece(self.tiles[lr][lf + 1].piece)
                self.tiles[lr][lf + 1].set_piece(None)
                self.last_move_castle_left = False

            # castle right
            if self.last_move_castle_right:
                self.tiles[lr][lf - 1].piece.file = lf + 1 
                self.tiles[lr][lf + 1].set_piece(self.tiles[lr][lf - 1].piece)
                self.tiles[lr][lf - 1].set_piece(None)
                self.last_move_castle_right = False

        piece.rank, piece.file = r,f
        self.tiles[r][f].set_piece(self.tiles[lr][lf].piece)
        # self.tiles[lr][lr].set_piece(None)


        # load older tile's piece
        self.tiles[lr][lf].set_piece(self.try_move_piece)
        self.try_move_piece = None
        piece.is_trying = False
        if self.tiles[lr][lf].has_piece(): 
            self.tiles[lr][lf].piece.legals.clear()
            self.tiles[lr][lf].piece.legal_moves_pre_check(self)

        self.tiles[r][f].piece.legals.clear()
        self.tiles[r][f].piece.legals = self.tiles[r][f].piece.old_legals.copy()
        # print("Move undone: ", r,f,lr,lf)
        # for i in self.tiles:
        #     for j in i:
        #         if not j.has_piece():
        #             print("---", end=" ")
        #         else:
        #             name = j.piece.name[0].upper() if j.piece.name != 'knight' else 'N'
        #             print(j.piece.color[0].upper() + "-" + name, end=" ")
        #     print("\n ")
        # print("------------------------------------------------")        

    
    
    def engine_try_move(self, r, f, lr, lf):
        # save older tile's piece
        self.engine_try_move_piece = self.tiles[lr][lf].piece

        piece = self.tiles[r][f].piece
        if isinstance(piece, King):
            # castle left

            if (lr, lf) == piece.castle_left_tile and piece.can_castle_left():
                self.tiles[lr][lf - 2].piece.file = lf + 1
                self.tiles[lr][lf + 1].set_piece(self.tiles[lr][lf - 2].piece)
                self.last_move_castle_left_engine = True

            # castle right
            if (lr, lf) == piece.castle_right_tile and piece.can_castle_right():
                self.tiles[lr][lf + 1].piece.file = lf - 1
                self.tiles[lr][lf - 1].set_piece(self.tiles[lr][lf + 1].piece)
                self.last_move_castle_right_engine = True


        self.tiles[r][f].set_piece(None)

        piece.rank, piece.file = lr,lf
        self.tiles[lr][lf].set_piece(piece)
        self.last_move = piece
        # for i in self.tiles:
        #     for j in i:
        #         if not j.has_piece():
        #             print("blank", end=" ")
        #         else:
        #             print(j.piece.name, end=" ")
        #     print("\n------")

        
    def engine_undo_move(self, r,f,lr,lf):
        piece = self.tiles[lr][lf].piece
        if isinstance(piece, King):
            # castle left
            if self.last_move_castle_left_engine:
                self.tiles[lr][lf + 1].piece.file = lf - 2
                self.tiles[lr][lf - 2].set_piece(self.tiles[lr][lf + 1].piece)
                self.tiles[lr][lf + 1].set_piece(None)
                self.last_move_castle_left_engine = False

            # castle right
            if self.last_move_castle_right_engine:
                self.tiles[lr][lf - 1].piece.file = lf + 1 
                self.tiles[lr][lf + 1].set_piece(self.tiles[lr][lf - 1].piece)
                self.tiles[lr][lf - 1].set_piece(None)
                self.last_move_castle_right = False

        piece.rank, piece.file = r,f
        self.tiles[r][f].set_piece(piece)
        # self.tiles[lr][lr].set_piece(None)


        # load older tile's piece
        self.tiles[lr][lf].set_piece(self.engine_try_move_piece)
        # self.tiles[lr][lf].piece_moved_try()
        # if piece.color == 'black':
        #     for i in self.tiles:
        #         for j in i:
        #             if not j.has_piece():
        #                 print(" ", end=" ")
        #             else:
        #                 print(j.piece.name[0].upper(), end=" ")
        #         print("\n ")
        #     print("------------------------------------------------")        
        self.engine_try_move_piece = None
        self.last_move = None


        
        
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
                # print(self.tiles[r][f].piece.name, r,f,lr,lf)
                return False
            else:
                self.undo_move(r,f,lr, lf)
                return True
        else:
            if self.check_black_k_in_check():
                self.undo_move(r,f,lr, lf)
                print(self.tiles[r][f].piece.name, r,f,lr,lf)
                # exit()
                return False
            else:
                self.undo_move(r,f,lr, lf)
                return True
            
    def get_in_check(self, color):
        return  not self.white_check if color == "white" else not self.black_check
    
    def check_for_checkmate(self):
        if self.last_move == None:
            return False
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == check_mate_color:
                    if len(tile.piece.legal_moves(self)) >0:
                        return False
        # print("checkmate#")
        if check_mate_color == 'black' and self.black_check:
            print(self.last_move.color, "wins")

            with open("winner.log", "a") as file:
                file.write(self.last_move.color + " wins\n")

            return True
        elif check_mate_color == 'white' and self.white_check:
            print(self.last_move.color, "wins")

            with open("winner.log", "a") as file:
                file.write(self.last_move.color + " wins\n")


            return True
        else:
            return self.check_for_stalemate()    
    
    def check_for_stalemate(self):
        remaining_pieces_white = []
        remaining_pieces_black = []
        stale_mate = True
        check_mate_color = "white" if self.last_move.color == "black" else "black"
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece():
                    if tile.piece.color == 'white':
                        remaining_pieces_white.append(tile.piece)
                    if tile.piece.color == 'black':
                        remaining_pieces_black.append(tile.piece)
                    if tile.piece.color == check_mate_color:
                        if len(tile.piece.legal_moves(self)) >0:
                            stale_mate = False
        
        if len(remaining_pieces_black) == len(remaining_pieces_white) and len(remaining_pieces_black) == 1:
            print("stalemate, DRAW!")
            with open("winner.log", "a") as file:
                file.write("Stalemate\n")
            return True
        if stale_mate:
            print("stalemate, DRAW!")
            with open("winner.log", "a") as file:
                file.write("Stalemate\n")
            return True
        return stale_mate
    
    def get_legal_moves(self,color):
        pieces = []
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == color:
                    if len(tile.piece.legal_moves(self)) > 0:
                        pieces.append((tile.piece,tile.piece.legal_moves(self)))
        return pieces
    
    def get_legal_moves_engine(self,color):
        legals = []
        for rank in self.tiles:
            for tile in rank:
                if tile.has_piece() and tile.piece.color == color:
                    if len(tile.piece.legal_moves(self)) > 0:
                        for mv in tile.piece.legal_moves(self):
                            move_name = chr(97 + tile.piece.file) + str(ROWS - tile.piece.rank) + chr(97 + mv[1]) + str(ROWS - mv[0])
                            move = (tile.piece.rank, tile.piece.file, mv[0], mv[1])
                            legals.append((move,move_name))
        return legals