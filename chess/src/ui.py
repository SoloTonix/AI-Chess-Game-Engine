from constants import *
from board import Board
from game import Game
import pygame

class UI:
    def __init__(self, game:Game, surface):
        self.game = game
        self.board = self.game.board.board
        self.surface =  surface
        self.white_pieces, self.black_pieces = self._load_pieces()
        self.promotion_pieces = self._load_promotion_pieces()


    def _draw_board(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if (row+col) % 2 == 0:
                    pygame.draw.rect(self.surface, WHITE, (col*SQSIZE, row*SQSIZE, SQSIZE, SQSIZE))
                else:
                    pygame.draw.rect(self.surface, BLACK, (col*SQSIZE, row*SQSIZE, SQSIZE, SQSIZE))

    def _draw_pieces(self):
        
        for row in self.board:
            for square in row:
                if square.piece is None:
                    pass
                else:
                    if square.piece.color == 'white':
                        self.surface.blit(self.white_pieces[square.piece.name], (square.col*SQSIZE, square.row*SQSIZE))
                    else:
                        self.surface.blit(self.black_pieces[square.piece.name], (square.col*SQSIZE, square.row*SQSIZE))



    def _load_pieces(self):
        

        pawn = pygame.image.load('chess/assets/pieces/pawn-w.svg')
        knight = pygame.image.load('chess/assets/pieces/knight-w.svg')
        bishop = pygame.image.load('chess/assets/pieces/bishop-w.svg')
        rook = pygame.image.load('chess/assets/pieces/rook-w.svg')
        queen = pygame.image.load('chess/assets/pieces/queen-w.svg')
        king = pygame.image.load('chess/assets/pieces/king-w.svg')

        white_pieces = {
            'pawn':pawn,
            'knight':knight,
            'bishop':bishop,
            'rook':rook,
            'queen':queen,
            'king':king
        }


        pawn = pygame.image.load('chess/assets/pieces/pawn-b.svg')
        knight = pygame.image.load('chess/assets/pieces/knight-b.svg')
        bishop = pygame.image.load('chess/assets/pieces/bishop-b.svg')
        rook = pygame.image.load('chess/assets/pieces/rook-b.svg')
        queen = pygame.image.load('chess/assets/pieces/queen-b.svg')
        king = pygame.image.load('chess/assets/pieces/king-b.svg')

        black_pieces ={
            'pawn':pawn,
            'knight':knight,
            'bishop':bishop,
            'rook':rook,
            'queen':queen,
            'king':king
        }

        return (white_pieces, black_pieces)

    def _load_promotion_pieces(self):
        pieces = self.white_pieces if self.game.turn == 'white' else self.black_pieces
        pieces = {k:v for k, v in pieces.items() if k not in ['king', 'pawn']}
        print(pieces['rook'].get_width())

        return pieces


    def _highlight_square(self):
        sq = self.game.selected_sq
        if sq is None:
            pass
        else:
            pygame.draw.rect(self.surface, GREY, (sq.col*SQSIZE, sq.row*SQSIZE, SQSIZE, SQSIZE))

    def _highlight_squares(self):
        valid_moves = self.game.valid_moves

    
        for row, col in valid_moves:
            pygame.draw.rect(self.surface, GREY, (col*SQSIZE, row*SQSIZE, SQSIZE, SQSIZE))

    def _display_promotion_pieces(self):
        for name, piece in self.promotion_pieces.items():
            if name == 'queen':
                self.surface.blit(piece, ((WIDTH / 8) - PROMOTION_PIECE_SIZE/2, PROMOTION_Y - PROMOTION_PIECE_SIZE/2))
            elif name == 'rook':
                self.surface.blit(piece, ((3 * WIDTH / 8) -  PROMOTION_PIECE_SIZE/2, PROMOTION_Y - PROMOTION_PIECE_SIZE/2))
            elif name == 'bishop':
                self.surface.blit(piece, ((5 * WIDTH / 8) -  PROMOTION_PIECE_SIZE/2, PROMOTION_Y - PROMOTION_PIECE_SIZE/2))
            else:
                self.surface.blit(piece, ((7 * WIDTH / 8) -  PROMOTION_PIECE_SIZE/2, PROMOTION_Y - PROMOTION_PIECE_SIZE/2))
            
 


    def render(self):
        self._draw_board()
        self._highlight_squares()
        self._highlight_square()
        self._draw_pieces()
        if self.game.promotion_pending:
            self._display_promotion_pieces()
        

