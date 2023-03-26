
from game_vars import *
from board import *
from animation import Animate

class Game:
    def __init__(self, screen):
        self.board = Board()
        self.font = pygame.font.SysFont('monospace', 18, bold=True)
        self.selected_piece = None
        self.current_player = 1
        self.move_count_w = 0
        self.move_count_b = 0
        self.screen = screen
        self.animate = Animate()


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
                self._draw_highlights(self.screen)
                return True
            
        return False
        
    def legal_selection(self, piece):
        return (self._white_to_move() and piece.color == white) or (self._black_to_move() and piece.color == black) 

    def update_game(self):
        self.selected_piece = None
        if self.current_player == 1:
            self.move_count_w +=1
        else:
            self.move_count_b +=1
        #reset white
        if (self.move_count_b % 2 == 0 and self.move_count_w % 2 == 0) or (self.move_count_b % 2 == 1 and self.move_count_w % 2 == 1):
            self.board.reset_en_passant_board(1)
        #reset black
        elif (self.move_count_b % 2 == 0 and self.move_count_w % 2 == 1) or (self.move_count_b % 2 == 1 and self.move_count_w % 2 == 0):
            self.board.reset_en_passant_board(-1)

        self.board.check_for_stalemate()
        self.current_player = 1 if self.current_player == 2 else 2

    def update_screen(self):
        self._draw_board(self.screen)
        self._draw_pieces(self.screen)

    
    def move_piece(self, pr,pf):
        tiles = self.board.tiles
        current_piece = self.selected_piece
   
        new_tile = tiles[pr][pf]
        r,f = current_piece.rank, current_piece.file

        
        #check if piece is moved
        if pr == r and pf == f:
            return False 
        
        if (pr,pf) in current_piece.legal_moves(self.board):
            
            #move piece
            tiles[r][f].piece_moved()
            current_piece.rank, current_piece.file = pr, pf
            new_tile.set_piece(current_piece)
            self.board.last_move = current_piece
        

            if isinstance(current_piece, Pawn):
            
                #check for promotion 
                current_piece.promote(self.board)
                
                #En Passant 
                if (pr - current_piece.dir, pf) == current_piece.en_passant_tile:
                    tiles[pr - current_piece.dir][pf].set_en_passant(-current_piece.dir) 
                #if we move to an en passant square we kill the other pawn
                elif tiles[pr][pf].can_en_passant(current_piece.dir):
                    tiles[pr - current_piece.dir][pf].piece_moved()
            
            if isinstance(current_piece, King):
                # castle left
                if (pr, pf) == current_piece.castle_left_tile:
                    tiles[pr][pf - 2].piece.file = pf + 1
                    tiles[pr][pf + 1].set_piece(tiles[pr][pf - 2].piece)
                    tiles[pr][pf - 2].piece_moved()
                    self.board.last_move = tiles[pr][pf + 1].piece

                # castle right
                if (pr, pf) == current_piece.castle_right_tile:
                    tiles[pr][pf + 1].piece.file = pf - 1
                    tiles[pr][pf - 1].set_piece(tiles[pr][pf + 1].piece)
                    tiles[pr][pf + 1].piece_moved()
                    self.board.last_move = tiles[pr][pf - 1].piece

            if self.board.black_check or self.board.black_check: 
                self.board.black_check, self.board.black_check = False, False

            self.board.check_for_check()
            return True
        return False
    def deselect(self):
        self.selected_piece = None

    def _draw_highlights(self, display):
        highligh_display = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        sqrs = self._legal_piece_moves()
        for i,j in sqrs:
            color = (0,0,0,90)
            hrect = (j*TSIZE + (TSIZE/2), i*TSIZE + TSIZE / 2)
                
            if self.board.tiles[i][j].has_piece() and self.board.tiles[i][j].piece.color != ("black" if self._black_to_move() else "white"):
                color = (0,0,0,70)
                pygame.draw.circle(highligh_display,color,hrect,50,5)
            else:
                pygame.draw.circle(highligh_display,color,hrect,10)

        display.blit(highligh_display,(0,0))

    def draw_hover(self, display , r,f):
        highligh_display = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        hrect = r*TSIZE,f*TSIZE,TSIZE, TSIZE
        pygame.draw.rect(highligh_display, (0,0,0,90), hrect, 3)
        display.blit(highligh_display,(0,0))

    def draw_select(self,display,r,f):
        highligh_display = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        hrect = r*TSIZE,f*TSIZE,TSIZE, TSIZE
        pygame.draw.rect(highligh_display, (0,204,255,50), hrect)
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
                    if self.animate.held and self.animate.piece == piece:
                        continue
                    piece.draw(display)
                    
            


   

    