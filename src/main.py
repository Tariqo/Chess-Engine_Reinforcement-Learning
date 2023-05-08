import pygame
from pygame.locals import *
import pygame_menu
import tkinter as tk
from tkinter import ttk

import os, sys

from game import *
from game_vars import *
from board import *

# set SDL to use the dummy NULL video driver, 
#   so it doesn't need a windowing system.
# os.environ["SDL_VIDEODRIVER"] = "dummy"


import pygame.transform
class Main:
    
    def __init__(self):
        pygame.init()
        self.game_display = pygame.display.set_mode((W_WIDTH, WIDTH))
        self.screen = pygame.display.set_mode( (W_WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game = Game(self.screen)
        self.menu = self._create_menu()
        self._engine_play = False
        self.simulate = False
        self.one_person = False
        self.two_persons = False
        self.menu.mainloop(self.game_display)


    def run(self):
        display = self.screen
        running = True

        self.game._draw_board(display)
        self.game._draw_pieces(display)
        self.game._draw_time_control(display)
        self.game.load_model()
        # self._engine_play = True
        # self.simulate= True
        # self.two_persons = True
        # self.one_person = True
        while running:
            if self._engine_play:
                if not self.game.game_over:
                    self.game.make_engine_play()
                for event in pygame.event.get():
                    if event.type == QUIT or (
                        event.type  == KEYDOWN and (
                        event.key == K_ESCAPE or
                        event.key == K_q
                        )):
                        pygame.quit()
                        quit()
            elif self.one_person:
                self.game.make_engine_play_black()
                self._event_handler()
            elif self.two_persons:
                self._event_handler()
            elif self.simulate:
                self._event_handler(self.simulate)
            pygame.display.update()


    def _event_handler(self, s = False):
        if s:
            
            # pygame.key.set_repeat(1,100)
            for event in pygame.event.get():
                if event.type == QUIT or (
                    event.type  == KEYDOWN and (
                    event.key == K_ESCAPE or
                    event.key == K_q
                    )):
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.game.simulate_game('n')
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_LEFT:
                        self.game.simulate_game('b')
                    elif event.key == K_RIGHT:
                        self.game.simulate_game('n')

        else:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT or (
                    event.type == KEYDOWN and (
                    event.key == K_ESCAPE or
                    event.key == K_q
                    )):
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN: 
                    my, mx = pygame.mouse.get_pos()[0]//TSIZE,pygame.mouse.get_pos()[1]//TSIZE
                    if my > 7:
                        continue
                    #check if selected piece 
                    if self.game.piece_selected():
                        if self.game.move_piece(mx,my):
                            self.game.update_game()
                            self.game.update_screen()
                        else:
                            self.game.deselect()
                            self.game.update_screen()
                    #select (or drag) a piece to move
                    else:

                        #check if current player's turn
                        #check if clicked piece 
                        #check if legal move
                        self.game.update_screen()
                        if self.game.select_piece(mx,my):
                            self.game.draw_select(self.screen, my,mx)
                            self.game.draw_hover(self.screen,my,mx)
                            self.game.animate.org_RF(mx,my)  
                            self.game.animate.hold(self.game.selected_piece)  

                elif event.type == pygame.MOUSEMOTION:
                    mx , my = pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]
                    if mx > WIDTH:
                        continue
                    self.game.animate.update_mouse(mx,my)
                    if self.game.animate.held:
                        self.game.animate.update_mouse(mx,my)
                        self.game.update_screen()
                        self.game.draw_select(self.screen, self.game.selected_piece.file,self.game.selected_piece.rank)

                        self.game._draw_highlights(self.screen)
                        self.game.draw_hover(self.screen,mx//TSIZE,my//TSIZE)
                        self.game.animate.draw(self.screen)


                elif event.type == pygame.MOUSEBUTTONUP: 
                    my, mx = pygame.mouse.get_pos()[0]//TSIZE,pygame.mouse.get_pos()[1]//TSIZE
                    if my > 7:
                        self.game.deselect()
                        self.game.update_screen()
                    if self.game.animate.held:
                        if self.game.piece_selected():
                            if self.game.move_piece(mx,my):
                                self.game.update_game()
                                self.game.update_screen()
                            else:
                                self.game.deselect()
                                self.game.update_screen()
                    self.game.animate.unhold()
                    self.game.update_screen()


            # if self.game.piece_selected():
            #     self.game.

        
    def engine_play(self):
        self._engine_play = True
        self.run()
    def simulate_play(self):
        if self.game.can_sim():
            self.open_table_window()
            if self.simulate:
                self.show_instructions()
                self.run()
        else:
            self.run_sim_err()
    
    def run_sim_err(self):
        root = tk.Tk()
        root.title("Game database")
        no_games = tk.Label(root, text='Database has no games', font=('Times New Roman', 20))

        no_games.pack(side='top', pady=15, padx=15)

        button1 = tk.Button(text="Exit",command=lambda: root.destroy())
        button1.pack(pady=20)
        root.mainloop()


    def view(self, tree: ttk.Treeview, root, play_B):
        con1 = self.game.db_connector

        cur1 = con1.cursor()

        cur1.execute("SELECT game_id, winner, move_count, game_date_time FROM chess_games")

        rows = cur1.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        def on_select(event):
            item = tree.focus()
            row = tree.item(item)['values']
            self.load_game(row[0])
            play_B["state"] = "normal"
        tree.bind("<<TreeviewSelect>>", on_select)


    def open_table_window(self):

        root = tk.Tk()
        root.title("Game database")
        root.protocol("WM_DELETE_WINDOW",lambda: None)
        tree = ttk.Treeview(root, column=("c1", "c2", "c3","c4"), show='headings', selectmode='browse')
        headers = ['Game ID', 'Winner', 'Move Count', 'Date and Time']

        for c,header in enumerate(headers, start=1):
            tree.column("#" + str(c), anchor=tk.CENTER)
            tree.heading("#" + str(c), text=header)

        tree.pack()
        def start_sim():
            self.simulate = True
            root.destroy()

        button2 = tk.Button(text="Replay selected",command=start_sim)
        button1 = tk.Button(text="Refresh data", command=self.view(tree, root, button2))
        button3 = tk.Button(text="Return to menu",command=lambda: root.destroy())

        button2["state"] = 'disabled'

        button1.pack(pady=10)
        button2.pack()
        button3.pack()
        root.mainloop()

    def load_game(self, game_id):
        conn = self.game.db_connector
        cur1 = conn.cursor()
        cur1.execute("SELECT game_move_history FROM chess_games WHERE game_id = " + str(game_id))
        move_history = cur1.fetchall()[0][0]
        self.game.moves = move_history.split(" ")

    def show_instructions(self):
        from PIL import Image, ImageTk

        HEIGHT = 500
        WIDTH = 800

        top_bg = 'white'

        ws = tk.Tk()
        ws.title("Simulation instructions")
        # ws['background']=bottom_bg
        # Create a frame to hold the images and text
        frame = tk.Frame(ws, width=WIDTH, height=HEIGHT)
        frame['background'] = top_bg
        frame.pack()

        # Create a label for the instructions
        instructions_label = tk.Label(frame, text='\nInstructions:', font=('Times New Roman', 20))
        instructions_label['background'] = top_bg

        instructions_label.pack(side='top', pady=15)

        # Load the images and resize them to 64x64 pixels
        image1 = Image.open('img/left_arrow.png')
        image1 = image1.resize((64, 64))
        image1_tk = ImageTk.PhotoImage(image1)

        image2 = Image.open('img/right_arrow.png')
        image2 = image2.resize((64, 64))
        image2_tk = ImageTk.PhotoImage(image2)

        # Create labels to display the images and text
        label1 = tk.Label(frame, text='\nLast Move', font=('Arial', 13))
        label1.config(image=image1_tk, compound='top')
        label1.image = image1_tk  # Keep a reference to the image to prevent garbage collection
        label1['background'] = top_bg
        label1.pack(side='left', padx=40, pady=15)

        label2 = tk.Label(frame, text='\nNext Move', font=('Arial', 13))
        label2.config(image=image2_tk, compound='top')
        label2.image = image2_tk  # Keep a reference to the image to prevent garbage collection
        label2['background'] = top_bg
        label2.pack(side='right', padx=40, pady=15)

        # Create a button to start the Pygame loop
        button = tk.Button(ws, text="Start Game", height=2,width=10,  bg='White', fg='Black', command=lambda: ws.destroy())
        button.pack(pady=7)

        ws.mainloop()
    

    def one_play(self):
        self.one_person = True
        self.run()
 
    def two_play(self):
        self.two_persons = True
        self.run()

    def _create_menu(self):
        menu = pygame_menu.Menu('', W_WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
        menu.add.button('Engine Play', self.engine_play)
        menu.add.button('Simulate Past Game', self.simulate_play)
        menu.add.button('Play Normal', self.one_play)
        menu.add.button('Multiplayer', self.two_play)
        return menu

import logging

main = Main()
LOG_FILENAME = 'logs/Main_logs.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

if os.path.isfile("logs/move_log.out"):
    os.remove("logs/move_log.out")
try:
    main.run()
except Exception as e:
    # with open("logs/ghistory.out", "a") as file:
    #     file.write("--Error\n")
    print("main crashed. Error: %s", e)
    logging.exception('Got exception on main handler')    
    exit(-1)
