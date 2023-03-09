import pygame
import pygame_menu
from pygame.locals import *
 
 
pygame.init()
 

 
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Chess')
 

def set_difficulty(value, difficulty):
        # Do the job here !
    pass

def start_the_game():
    # Do the job here !
    pass

menu = pygame_menu.Menu('Welcome', 400, 300,
                       theme=pygame_menu.themes.THEME_BLUE)


menu.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)

menu.mainloop(game_display)


