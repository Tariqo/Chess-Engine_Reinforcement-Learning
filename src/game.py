import os.path
import sqlite3
import pygame.freetype
from game_vars import *
from board import *
from animation import Animate
from q_learning_engine import DQNEngine
from engine import Engine

class Game:
    def __init__(self, screen, fen = ""):
        if fen:
            self.board = Board(fen=fen)
            self.current_player = 1 if self.board.turn == 'white' else 2
        else:
            self.board = Board()
            self.current_player = 1
        self.font = pygame.font.SysFont('monospace', 18, bold=True)
        self.selected_piece = None
        self.move_count_w = 0
        self.move_count_b = 0
        self.screen = screen
        self.animate = Animate()
        # self.engine = Engine("white")
        self.engine = DQNEngine("white")
        self.engine2 = DQNEngine("black")
        # self.engine2 = Engine("black")
        self.move_log = ""
        self.visual_move_log = ""
        self.winner = ""
        self.general_move_cnt = 0
        self.board_history = []
        self.moves = []
        self.log_file = os.path.isfile("logs/move_log.out")
        self.current_piece_legal_moves = []
        self.db_connector = None
        self.game_over = False
        self.create_db()

                                       
    def piece_selected(self):
        return self.selected_piece is not None
    
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

        game_end, result = self.board.check_for_game_end()
        if game_end:
            self.winner = result
            self.game_over = True
            self.close_db()
            self.update_screen()
            self.save_model()
        self.current_player = 1 if self.current_player == 2 else 2
        self.board.set_turn(self.current_player)
    def make_engine_play(self):
        if not self.game_over:
            if self.current_player == 1:
                if not self.engine_move():
                    print("White made an illegal move")
                else:
                    self.update_screen()
                    self.update_game()
            if self.current_player == 2:
                if not self.engine2_move():
                    print("Black made an illegal move")
                else:
                    self.update_screen()
                    self.update_game()

    def make_engine_play_black(self):
        if not self.game_over:
            if self.current_player == 2:
                if not self.engine2_move():
                    print("Black made an illegal move")
                else:
                    self.update_screen()
                    self.update_game()
        
    def simulate_game(self, command):
        if self.general_move_cnt < len(self.moves) and command == 'n':
            self.board_history.append(self.board.save_to_FEN())
            mv = self.moves[self.general_move_cnt]
            move_log_string = ''
            for i in self.board.tiles:
                for j in i:
                    if not j.has_piece():
                        move_log_string += "--- "
                    else:
                        name = j.piece.name[0].upper() if j.piece.name != 'knight' else 'N'
                        move_log_string += j.piece.color[0].upper() + "-" + name + " "
                move_log_string+= "\n"
            move_log_string+= "------------------------------------------------\n"
            # print(move_log_string)
            self.selected_piece = self.board.tiles[int(mv[1])][int(mv[2])].piece 
            self.move_piece(int(mv[3]),int(mv[4]))
            self.update_screen()
            self.update_game()
            self.general_move_cnt += 1
        elif self.general_move_cnt > 0 and command == 'b':
            self.general_move_cnt -= 1
            fen = self.board_history.pop()
            self.board = Board(fen=fen)
            self.current_player = 1 if self.board.turn == 'white' else 2
            self.update_screen()


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
        # self._draw_time_control(self.screen)
        self._draw_board(self.screen)
        self._draw_pieces(self.screen)
        if self.game_over:
            self._draw_game_end(self.winner)

    
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
            self.visual_move_log += move_log_string    
            self.log_to_file(move_log_string)
            self.add_move_to_move_log(self.selected_piece.name, r,f,pr,pf)

        return piece_moved

    def log_to_file(self, move_log_string):
        pass
        # if(self.log_file):
        #     with open("logs/move_log.out", "a") as file: 
        #         file.write(move_log_string)

        # else:
        #     with open("logs/move_log.out", "w") as file: 
        #         file.write(move_log_string)



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

        # with open("logs/ghistory.out", "a") as file:
        #     file.write(new_string)


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
                color = blk if (row + col) % 2 != 0 else wht
                # rect
                rect = (col * TSIZE, row * TSIZE, TSIZE, TSIZE)
                # blit
                pygame.draw.rect(display, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color =  wht  if row % 2 != 0 else blk
                    # label
                    lbl = self.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * TSIZE)
                    # blit
                    display.blit(lbl, lbl_pos)
                # col coordinates
                if row == 7:
                    # color
                    color = blk if (row + col) % 2 == 0 else wht
                    # label
                    lbl = self.font.render(chr(97 + col), 1, color)
                    lbl_pos = (col * TSIZE + TSIZE - 20, HEIGHT - 20)
                    # blit
                    display.blit(lbl, lbl_pos)
    
    def _draw_game_end(self,verdict = ''):
        font = pygame.font.SysFont('monospace', 26, bold=True)

        if self.winner != 'Stalemate':
            verdict = 'Checkmate' 
            winner = self.winner + ' wins'
        else:
            winner = ''
    
        label_s = 100
        label_w = W_WIDTH - WIDTH
        label = font.render(verdict, True, (255, 255, 255))
        label_rect = label.get_rect()
        label_rect.center = (label_w // 2, label_s//2 )
        
        font_under = pygame.font.SysFont('monospace', 18, bold=True)
        label_under = font_under.render(winner, True, (255, 255, 255))
        label_under_rect = label_under.get_rect()
        label_under_rect.center = (label_w // 2, label_s//2 + 26 )

        surface = pygame.Surface((label_w, label_s), flags=pygame.SRCALPHA)
        surface.set_alpha(300)
        # surface.fill((0, 0, 0))
        surface.blit(label, label_rect)
        surface.blit(label_under, label_under_rect)

        self.screen.blit(surface, (WIDTH, (HEIGHT // 2) - (label_s//2)))

        pygame.display.flip()

    def _draw_time_control(self, display):
        # Define the default values
        font = pygame.font.SysFont('monospace', 26, bold=True)

        time = "00:00"
        bg_color = '#2d2d2d'
        boarder = 1
        margin = 5
        padding = 120
        
        alpha = 300
        if self.game_over:
            alpha = 80

        line_w = WIDTH + margin
        # Create Big Box
        box_rect = pygame.Rect(WIDTH, 0, W_WIDTH - WIDTH, HEIGHT)
        # Draw the box with the appropriate color
        pygame.draw.rect(display, bg_color, box_rect)
        if not self.game_over:
            pygame.draw.line(display, 'gray', (line_w,HEIGHT//2),(W_WIDTH - margin,HEIGHT//2),boarder)
            
        # Create surface for time label above line
        time_label_top = font.render(time, True, (255, 255, 255))
        time_label_top.set_alpha(alpha)
        time_label_top_rect = time_label_top.get_rect()
        time_label_top_rect.center = ((W_WIDTH + WIDTH + margin) // 2, (HEIGHT // 2 ) - padding)
        
        # Create surface for time label below line
        time_label_bottom = font.render(time, True, (255, 255, 255))
        time_label_bottom.set_alpha(alpha)
        time_label_bottom_rect = time_label_bottom.get_rect()
        time_label_bottom_rect.center = ((W_WIDTH + WIDTH + margin) // 2, (HEIGHT // 2 ) + padding)

        # Draw the time labels above and below the line
        display.blit(time_label_top, time_label_top_rect)
        display.blit(time_label_bottom, time_label_bottom_rect)
    

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
        # self.engine2.save_model('QDNB')
        exit()
        # with open("logs/ghistory.out", "a") as file:
        #     file.write("\n")
    
    def load_model(self):
        try:
            self.engine.load_model('QDN')
            # self.engine2.load_model('QDNB')
        except IOError:
            print("Modal not found. Starting with an empty Modal.")

    
    def create_db(self, db='game_history.db'):
        # Connect to the database or create it if it doesn't exist
        connector = sqlite3.connect('databases/' + db)
        self.db_connector = connector

        # Create the table if it doesn't exist
        connector.execute('''CREATE TABLE IF NOT EXISTS chess_games (
                    game_id INTEGER PRIMARY KEY,
                    game_move_history TEXT,
                    visual_game_log TEXT,
                    winner TEXT,
                    move_count INTEGER,
                    FEN TEXT,
                    game_date_time TEXT
                            );''')
        # Commit the changes
        connector.commit()

    def close_db(self):
        self.db_add_row()
        self.db_connector.close()        
    
    def db_add_row(self):
        c = self.db_connector.cursor()

        c.execute("SELECT MAX(game_id) FROM chess_games")
        max_game_id = c.fetchone()[0]
        if max_game_id is None:
            max_game_id = 0
        
        game_id = max_game_id + 1
        game_move_history = self.move_log
        visual_game_log = self.visual_move_log
        winner = self.winner
        move_count = self.board.move_count
        FEN_ = self.board.save_to_FEN()
        import datetime
        now = datetime.datetime.now()
        game_date_ime =  now.strftime("%Y-%m-%d_%H:%M:%S")  

        self.db_connector.execute("INSERT INTO chess_games (game_id, game_move_history, visual_game_log, winner, move_count, FEN, game_date_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (game_id, game_move_history,visual_game_log, winner, move_count, FEN_, game_date_ime) )
        self.db_connector.commit()

   

    