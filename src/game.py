
from game_vars import *
from board import *

class Game:
    def __init__(self):
        self.board = Board()
        self.font = pygame.font.SysFont('monospace', 18, bold=True)
        self.selected_piece = None
        self.current_player = 1
        self.move_count = 0

    def piece_selected(self):
        return self.selected_piece != None
    
    def _white_to_move(self):
        return self.current_player == 1
    
    def _black_to_move(self):
        return self.current_player == 2
    #select piece based on rank and file
    def select_piece(self, pr,pf):
        tile = self.board.tiles[pr][pf]
        if tile.has_piece():
            if self.legal_selection(tile.piece):
                self.selected_piece = tile.piece
                return True
        return False
        
    def legal_selection(self, piece):
        return (self._white_to_move() and piece.color == white) or (self._black_to_move() and piece.color == black) 

    def update_game(self):
        self.selected_piece = None
        self.current_player = 1 if self.current_player == 2 else 2
        self.move_count+=1 

        if self.move_count % 3 ==0:
            self.board.reset_en_passant_board()

    def move_piece(self, pr,pf):
        tiles = self.board.tiles
        current_piece = self.selected_piece
   
        new_tile = tiles[pr][pf]
        r,f = current_piece.rank, current_piece.file

        
        #check if piece is moved
        if pr == r and pf == f:
            return False 
        
        if (pr,pf) in current_piece.legal_moves(self.board):
        #change older tile's piece to None
            
            
            #En Passant 
            if isinstance(current_piece, Pawn):
                if (pr - current_piece.dir, pf) == current_piece.en_passant_tile:
                    self.board.tiles[pr - current_piece.dir][pf].set_en_passant()                                
            
            
            if isinstance(current_piece, King):
                #--TODO-- castle left
                if (pr, pf) == current_piece.castle_left_tile:
                    tiles[pr][pf - 2].piece.file = pf + 1
                    tiles[pr][pf + 1].set_piece(tiles[pr][pf - 2].piece)
                    tiles[pr][pf - 2].piece.moved()
                    tiles[pr][pf - 2].piece_moved()

                #--TODO-- castle right
                if (pr, pf) == current_piece.castle_right_tile:
                    tiles[pr][pf + 1].piece.file = pf - 1
                    tiles[pr][pf - 1].set_piece(tiles[pr][pf + 1].piece)
                    tiles[pr][pf + 1].piece.moved()
                    tiles[pr][pf + 1].piece_moved()

                pass

            #move piece
            tiles[r][f].piece_moved()
            current_piece.rank, current_piece.file = pr, pf
            current_piece.moved()
            new_tile.set_piece(current_piece)
            return True
        return False
    def deselect(self):
        self.selected_piece = None

    def _draw_highlights(self,sqrs, display):
        highligh_display = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        for i,j in sqrs:
            color = (0,0,0,90)
            hrect = (j*TSIZE + (TSIZE/2), i*TSIZE + TSIZE / 2)
                
            if self.board.tiles[i][j].has_piece():
                color = (0,0,0,70)
                pygame.draw.circle(highligh_display,color,hrect,50,5)
            else:
                pygame.draw.circle(highligh_display,color,hrect,10)

        display.blit(highligh_display,(0,0))

    def _legal_piece_moves(self):
        return self.selected_piece.legal_moves(self.board)
    
    def _draw_board(self, display):
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = blk if (row + col) % 2 == 0 else wht
                # rect
                rect = (col * TSIZE, row * TSIZE, TSIZE, TSIZE)
                # blit
                pygame.draw.rect(display, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color =  blk  if row % 2 != 0 else wht
                    # label
                    lbl = self.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * TSIZE)
                    # blit
                    display.blit(lbl, lbl_pos)
                # col coordinates
                if row == 7:
                    # color
                    color = blk if (row + col) % 2 != 0 else wht
                    # label
                    lbl = self.font.render(chr(97 + col), 1, color)
                    lbl_pos = (col * TSIZE + TSIZE - 20, HEIGHT - 20)
                    # blit
                    display.blit(lbl, lbl_pos)
        
    def _castle_left(self):
        pass
    
    def _castle_right(self):
        pass

    def _draw_pieces(self, display):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.tiles[row][col].has_piece():
                    piece = self.board.tiles[row][col].piece
                    piece.draw(display)
                    
            


   

    