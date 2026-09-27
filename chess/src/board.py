from constants import *
from piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from utils import convert_pixel_to_matrix
class Square:
    def __init__(self, row:int, col:int, algebra, color, piece:Piece=None):
        self.row = row
        self.col = col
        self.algebra = algebra
        self.matrix = (self.row, self.col)
        self.color = color
        self.piece = piece




class Board:
    def __init__(self):
        self.board = []
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        self._create()
        self._add_pieces()

    def _create(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                algebra = f'{self.files[col]}{ROWS-row}'
                color = 'white' if (row+col) % 2 == 0 else 'black'
                self.board[row].append(Square(row, col, algebra,color))

    def _add_pieces(self):
        non_pawn_pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(COLS):
            # add pawn piece
            self.board[1][col].piece = Pawn('black')
            self.board[6][col].piece = Pawn('white')

            # add non pawn piece
            self.board[0][col].piece = non_pawn_pieces[col]('black')
            self.board[7][col].piece = non_pawn_pieces[col]('white')


    def get_square(self, row, col):
        return self.board[row][col]

    def get_squares(self):
        all_squares = []
        for row in self.board:
            for square in row:
                all_squares.append(square)

        return all_squares

    def get_enemy_squares(self, turn):
        enemy_squares = []
        for square in self.get_squares():
            if square.piece and square.piece.color != turn:
                enemy_squares.append(square)

        return enemy_squares


    
    def get_piece(self, row, col):
        return self.board[row][col].piece

    def set_piece(self, row, col, piece:Piece):
        if piece is None:
            pass
        self.board[row][col].piece = piece

    def remove_piece(self, row, col):
        self.board[row][col].piece = None

    def move_piece(self, row, col, dest_row, dest_col):
        piece = self.get_piece(row, col)
        if piece:
            self.remove_piece(row, col)
            self.remove_piece(dest_row, dest_col)
            self.set_piece(dest_row, dest_col, piece)

            if piece.name in ['pawn', 'rook', 'king']:
                piece.moved = True
            if piece.name == 'pawn' and abs(row-dest_row) == 2:
                piece.en_passantable = True
            else:
                piece.en_passantable = False

    def check_boundary(self, row, col):
        # check board boundary
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False
        return True

    def copy(self):
        copy = Board()
        for row in self.board:
            for square in row:
                if square.piece is None:
                    copy.board[square.row][square.col].piece = None

                else:
                    if square.piece.name == 'pawn':
                        original_piece = square.piece
                        copy.board[square.row][square.col].piece = Pawn(original_piece.color)
                        copy_piece = copy.board[square.row][square.col].piece
                        copy_piece.moved = original_piece.moved
                        copy_piece.en_passantable = original_piece.en_passantable

                    elif square.piece.name == 'knight':
                        copy.board[square.row][square.col].piece = Knight(square.piece.color)

                    elif square.piece.name == 'bishop':
                        copy.board[square.row][square.col].piece = Bishop(square.piece.color)

                    elif square.piece.name == 'rook':
                        original_piece = square.piece
                        copy.board[square.row][square.col].piece = Rook(original_piece.color)
                        copy_piece = copy.board[square.row][square.col].piece
                        copy_piece.moved = original_piece.moved

                    elif square.piece.name == 'queen':
                        copy.board[square.row][square.col].piece = Queen(square.piece.color)

                    else:
                        original_piece = square.piece
                        copy.board[square.row][square.col].piece = King(original_piece.color)
                        copy_piece = copy.board[square.row][square.col].piece
                        copy_piece.moved = original_piece.moved  
                        copy_piece.castled = original_piece.castled


        return copy


                        


                        




                    



    
           


    


