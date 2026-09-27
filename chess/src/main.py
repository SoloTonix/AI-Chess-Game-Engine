import pygame 
from constants import *
from board import Board
from game import Game
from ai import AI
from ui import UI
from utils import convert_pixel_to_matrix




def main():
    pygame.init()

    pygame.display.set_caption('Chess Game with AI.')
    
    
    
    FPS = 60
    clock = pygame.time.Clock()

    board = Board()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(board)
    ai = AI(game, 'black')
    ui = UI(game, screen)

    rook = board.board[0][0].piece

    running = True
    while running:
        for event in pygame.event.get():

            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_event(event)
        
            if event.type == pygame.QUIT:
                running = False

        if game.turn == ai.color:
            best_move = ai.choose_best_move(game, board, ai.color)
            game.handle_ai_move(best_move)

        if game.check_mate == True:
            running = False
        if game.stale_mate == True:
            running = False


        ui.render()
        pygame.display.flip()
        clock.tick(FPS)

    
    pygame.quit()


if __name__ == '__main__':
    main()
    



        