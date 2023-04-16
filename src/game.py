
#"P6050 P1020 P6343 P1727 P6545 P1434 P6151 R0010 P6252 P2030 R7060 P1232 P6646 P1626 N7657 P3040 P4636 P4051 P5242 P1525 N5776 P2737 P3627 P2636 P5040 N0120 K7465 R1000 R6061 P1333 N7657 R0010 Q7363 P3747 Q6352 N0627 B7254 P3243 Q5253 B0523 P4030 B2350 Q5373 R0706 B7566 R0607 R7776 B0213 P4233 N2012 N7150 N1224 B6644 R0706 K6575 P3445 B5445 N2445 R7677 P2535 P3020 R0607 R7776 R0717 P6454 B1322 P3323 B2213 B4466 Q0300 B6622 N2706 K7574 P1131 K7465 P3141 K6574 Q0022 R6164 B1302 P5444 P3544 R7677 N0625 N5745 R1014 N4533 P4353 P2010 B0224 N5031 R1707 N3143 R1413 N4335 K0403 N3556 R0727 Q7363 R2717 N5637 P5364 N3314 P4757 K7464 R1714 P2314 K0312 P1000 K1221 K6473 R1353 K7374 P4454 Q6364 R5333 Q6455 Q2231 Q0060"

from game_vars import *
from board import *
from animation import Animate
from q_learning_engine import DQNEngine
from engine import Engine
import time
import os.path

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
        self.engine = DQNEngine("white")
        self.engine2 = Engine("black")
        self.move_log = ""
        self.general_move_cnt = 0
        self.simulation_string = "P6151 P1020 P6040 P1636 P6343 P1525 N7152 R0010 P6656 R1000 B7236 P1737 P6242 K0415 B3663 P1121 P6454 P1222 P5141 P2232 K7464 Q0304 N5231 P2535 B6352 B0211 P4030 P3747 N7655 P2031 R7050 Q0402 P4332 N0625 B5234 B1122 Q7374 P3142 R5070 P4757 B7557 B2240 Q7475 B4051 N5576 N0120 P3222 R0001 P5646 R0747 B3425 R0100 B2507 Q0211 P5444 R0010 Q7572 K1506 Q7254 B5140 P3021 N2041 Q5436 K0607 R7050 R4746 N7655 B4031 Q3646 P3545 N5543 B0516 R7770 K0717 Q4626 K1726 R5055 Q1120 R5553 B1625 P2110 B2536 R5350 B3625 K6473 P4252 P2213 K2617 R5030 N4153 N4322 P4555 P1000 B2507 R7060 N5365 K7374 N6557 Q0002 B0716 N2201 P5262 N0120 B3122 Q0211 K1706 N2041 K0605 Q1112 K0515 R3036 P1424 R3635 P2435 Q1203 P3545 R6020 B1605 P6747 K1526 Q0336 N5736 R2022 B0523 P4434 P6272 R2272 B2334 N4122 K2616 R7262 P5565 K7465 P4555 R6252 B3425 K6575 K1626 R5242 K2617 N2210 B2552 R4243 N3615 P1303 P5565 R4341 K1726 R4151 K2627 Q0321 B5225 R5161 N1523 Q2132 K2717 R6151 K1706 Q3236 K0617 R5111 B2516 Q3663 N2335 R1141 N3547 Q6364 B1605 R4161 K1706 Q6473 B0527 Q7364 N4766 N1002 N6654 K7565 N5435 K6566 K0617 R6160 B2772 Q6475 K1726 Q7520 K2636 Q2023 N3554 K6657 K3637 Q2345 B7263 Q4575 K3727 N0223 B6341 R6040 B4174 R4060 N5462 R6010 N6250 R1012 B7447 R1222 K2737 R2220 K3726 N2304 K2637 Q7545 N5031 Q4567 N3150 Q6761 K3736 Q6171 K3637 Q7151 N5031 Q5133 B4736 N0416"
        self.moves = self.simulation_string.split(" ")
        self.log_file = os.path.isfile("move_log.log")
        self.current_piece_legal_moves = []
                                       
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

        
        if self.board.check_for_game_end():
            self.save_model()
        self.current_player = 1 if self.current_player == 2 else 2
        self.board.set_turn(self.current_player)

    def make_engine_play(self):
        # time.sleep(0.9)
        if self.current_player == 1:
            if not self.engine_move():
                print("Motherfucking white made an illegal move")
            else:
                self.update_screen()
                self.update_game()
        if self.current_player == 2:
            if not self.engine2_move():
                print("Motherfucking black made an illegal move")
            else:
                self.update_screen()
                self.update_game()

    def make_engine_play_black(self):
        if self.current_player == 2:
            if not self.engine2_move():
                print("Motherfucking black made an illegal move")
            else:
                self.update_screen()
                self.update_game()
    
    def simulate_game(self):
        if self.general_move_cnt < len(self.moves):
            mv = self.moves[self.general_move_cnt]
            # print(mv)
            self.selected_piece = self.board.tiles[int(mv[1])][int(mv[2])].piece 
            self.move_piece(int(mv[3]),int(mv[4]))
            self.update_screen()
            self.update_game()
            self.general_move_cnt += 1
        else:
            self.make_engine_play()
    def make_first_move(self):
        self.engine_move()
        self.update_game()

    def engine_move(self):
        piece, move = self.engine.choose_move(self.board)

        log_string = self.engine.color + " to play: " + "\n" + piece.color + " " + piece.name + " from (" + str(piece.rank)  + "," + str(piece.file) + ") to (" + str(move[0]) + "," + str(move[1]) + "): \n"
        self.log_to_file(log_string)
        self.selected_piece = piece
        return self.move_piece(move[0],move[1])

    def engine2_move(self):
        piece, move = self.engine2.choose_move(self.board)
        log_string = self.engine2.color + " to play: " + "\n" + piece.color + " " + piece.name + " from (" + str(piece.rank)  + "," + str(piece.file) + ") to (" + str(move[0]) + "," + str(move[1]) + "): \n"
        self.log_to_file(log_string)
        self.selected_piece = piece
        return self.move_piece(move[0],move[1])

    def update_screen(self):
        self._draw_board(self.screen)
        self._draw_pieces(self.screen)

    
    def move_piece(self, pr,pf):
        move_log_string = ""
        r,f = self.selected_piece.rank, self.selected_piece.file
        piece_moved = self.board.move_piece(self.selected_piece, self.board.tiles[pr][pf])

        if piece_moved:
            for i in self.board.tiles:
                for j in i:
                    if not j.has_piece():
                        move_log_string += "--- "
                    else:
                        name = j.piece.name[0].upper() if j.piece.name != 'knight' else 'N'
                        move_log_string += j.piece.color[0].upper() + "-" + name + " "
                move_log_string+= "\n"
            move_log_string+= "------------------------------------------------\n"    
            self.log_to_file(move_log_string)
            self.add_move_to_move_log(self.selected_piece.name, r,f,pr,pf)

        return piece_moved

    def log_to_file(self, move_log_string):
        if(self.log_file):
            with open("move_log.log", "a") as file: 
                file.write(move_log_string)

        else:
            with open("move_log.log", "w") as file: 
                file.write(move_log_string)



    def find_king(self, color):
        for tiles in self.board.tiles:
            for tile in tiles:
                if tile.has_piece() and tile.piece.name == 'king' and tile.piece.color == color:
                    return tile.piece
        
    def deselect(self):
        self.selected_piece = None

    def add_move_to_move_log(self, name,r,f, pr,pf ):
        concat_string = ""
        p_name = name
        if p_name == "knight":
            p_name = "N"
        else:
            p_name = str.upper(name[0]) 

        new_string = p_name + str(r) + str(f) + str(pr) + str(pf) + " "
        # new_string = p_name + str(r) + str(f) + concat_string + chr(97 + pf) + str(ROWS - pr) + " "
        self.move_log += new_string

        with open("Game.txt", "a") as file:
            file.write(new_string)


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
        if self.current_piece_legal_moves and self.animate.held:
            return self.current_piece_legal_moves
        else:
            self.current_piece_legal_moves = self.board.piece_legal_moves(self.selected_piece).copy()
            return self.current_piece_legal_moves
            
    
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
                    sprite = pygame.image.load(os.path.join(IMAGE_DIR, piece.sprite + '.png'))
                    piece_img = sprite
                    img_center = piece.file * TSIZE + TSIZE // 2, piece.rank * TSIZE + TSIZE // 2
                    img_rect = piece_img.get_rect(center=img_center)
                    display.blit(piece_img,img_rect)
    
    def save_model(self):
        self.engine.save_model('QDN')
        with open("Game.txt", "a") as file:
            file.write("\n")
        exit()

    
    def load_model(self):
        try:
            self.engine.load_model('QDN')
        except IOError:
            print("Q-table file not found. Starting with an empty Q-table.")

    def save_q_table_after_game(self):
        self.engine.save_q_table('q_table.pickle')
        with open("Game.txt", "a") as file:
            file.write("\n")
        exit()

    
    def load_q_table_before_game(self):
        try:
            self.engine.load_q_table('q_table.pickle')
        except FileNotFoundError:
            print("Q-table file not found. Starting with an empty Q-table.")



   

    