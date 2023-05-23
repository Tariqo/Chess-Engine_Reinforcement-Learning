import os
import pygame
from game_vars import *
class Piece:
    def __init__(self,rank, file, name, color, value, sprt_name):
        self.rank = rank
        self.file = file
        self.name = name
        self.color = color
        self.color_val = 1 if color == "black" else -1
        self.value = value * self.color_val
        self.dir = self.color_val
        self.legals = []
        self.moved = False
        self.sprite = sprt_name
        self.is_trying = False

    
    def draw(self, display):
        piece_img = self.sprite
        img_center = self.file * TSIZE + TSIZE // 2, self.rank * TSIZE + TSIZE // 2
        img_rect = piece_img.get_rect(center=img_center)
        display.blit(piece_img,img_rect)
    
    def _moved(self):
        self.moved = True
    
    def _moved_try(self):
        pass

    def legal_moves(self,):
        self.legals.clear()
        return self.legals

    def legal_straight_moves(self,dirs):
        r,f = self.rank, self.file
        for dir in dirs:
            rank_i = dir[0]
            file_i = dir[1]
            dir_moves = []
            while True:    
                if rank_i + r >= 0 and rank_i + r < ROWS and file_i + f >= 0 and file_i + f < COLS:
                    dir_moves.append((rank_i + r, file_i + f))
                    rank_i += dir[0]
                    file_i += dir[1]
                else:
                    if dir_moves:
                        self.legals.append(dir_moves)
                    break

        return self.legals
    def is_being_tried(self):
        self.is_trying = True
            
    def done_being_tried(self):
        self.is_trying = False



class Pawn(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'pawn', color, 1.0, 'bP' if color == 'black' else 'wP')
        self.en_passant_tile = (self.rank + 1 * self.dir,self.file)
        self.trying_move = False
        self.en_passant = (0,0)
    
    def legal_moves(self):
        self.legals.clear()
        sq = 2
        if not self.moved and not self.is_trying :
            sq = 3
        for i in range(1, sq):
            if self.rank + (i*self.dir) < 0 or self.rank + (i*self.dir) >= COLS :
                continue
            self.legals.append((self.rank + (i*self.dir),self.file))


        #--TODO-- eat right or left
        diags = [(self.rank + (1*self.dir), self.file + 1),(self.rank + (1*self.dir), self.file - 1)]
        for t in diags:
            if t[0] < 0 or t[0] >= ROWS or t[1] < 0 or t[1] >= COLS:
                continue
            self.legals.append(t)
        return self.legals
                
class King(Piece):
    def __init__(self, color, rank = 0, file= 0):
        self.castle_left = True
        self.castle_right = True
        self._in_check = False
        self.rank = rank
        self.file = file
        self.castle_left_tile=(self.rank, self.file - 2)
        self.castle_right_tile = (self.rank, self.file + 2)
        self.trying_move = False
        self.blocking_left = True
        self.blocking_right = True
        super().__init__( rank , file,'king', color, 9999.9, 'bK' if color == 'black' else 'wK')
    
    def in_check(self):
        self._in_check = True
    def is_in_check(self):
        return self._in_check
    def not_in_check(self):
        self._in_check = False
    
    def legal_moves(self ):
        self.legals.clear()
        possible_moves = [(self.rank + i, self.file + j) for i,j in [(0,1),(1,0),(1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(-1,1)]]
        for m in possible_moves:
            if m[0] >= 0 and m[0] < ROWS and m[1] >= 0 and m[1] < COLS:
                self.legals.append(m)
        #castling
        if self.moved:
            self.castle_left = False
            self.castle_right= False
        return self.legals
    
    def can_castle_left(self):
        return self.castle_left
    
    def can_castle_right(self):
        return self.castle_right
    
    def add_castle_left(self):
        self.legals.append((self.rank, self.file - 2))

    def add_castle_right(self):
        self.legals.append((self.rank, self.file + 2))

    def cant_castle_right(self):
        self.castle_right = False
    def cant_castle_left(self):
        self.castle_left = False


class Queen(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'queen', color, 9.0, 'bQ' if color == 'black' else 'wQ')
    def legal_moves(self ):
        self.legals.clear()
        self.legals =  super().legal_straight_moves(dirs = [(0,1),(1,0),(1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(-1,1)]) 
        return self.legals
class Rook(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'rook', color, 5.0, 'bR' if color == 'black' else 'wR')
    def legal_moves(self ):
        self.legals.clear()
        self.legals =  super().legal_straight_moves(dirs = [(0,1),(1,0),(0,-1),(-1,0)])
        return self.legals
class Bishop(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'bishop', color, 3.0, 'bB' if color == 'black' else 'wB')
    def legal_moves(self ):
        self.legals.clear()
        self.legals = super().legal_straight_moves(dirs = [(1,1),(-1,-1),(1,-1),(-1,1)])
        return self.legals


class Knight(Piece):
    def __init__(self, color, rank = 0, file= 0):
        super().__init__( rank , file,'knight', color, 3.0, 'bN' if color == 'black' else 'wN')
        
    def legal_moves(self ):
        self.legals.clear()
        possible_moves = [(self.rank + i, self.file + j) for i,j in [(-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1)]]
        for m in possible_moves:
            if m[0] >= 0 and m[0] < ROWS and m[1] >= 0 and m[1] < COLS:
                self.legals.append(m)
        return self.legals