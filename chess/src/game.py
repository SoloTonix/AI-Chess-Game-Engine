from board import Board, Square
from piece import *
from constants import *
from utils import *
import pygame



class Game:
    def __init__(self, board):
        self.board = board

        self.turn = 'white'
        self.check = False
        self.check_mate = False
        self.stale_mate = False

        self.selected_sq = None
        self.selected_piece = None
        self.valid_moves = []

        self.white_king_sq = None
        self.black_king_sq = None

        self.promotion_pending = False
        self.promotion_sq = None


    def handle_event(self, event):
        if self.promotion_pending:
            self.handle_promotion_event(event)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:

            row, col = convert_pixel_to_matrix(event.pos)
            piece = self.board.get_piece(row, col)

            if self.selected_piece is None:

                if piece and piece.color == self.turn:
                    self.selected_piece = piece
                    self.selected_sq = self.board.get_square(row, col)
                    self.valid_moves = []
                    self._calculate_valid_moves(self.selected_sq)

            else:

                if (row, col) in self.valid_moves:


                    is_castling = (self.selected_piece.name == 'king' and abs(col-self.selected_sq.col) == 2)
                    is_en_passant = (self.selected_piece.name == 'pawn' and self._validate_en_passant_capture((row, col), self.selected_piece))


                    self.board.move_piece(
                        self.selected_sq.row,
                        self.selected_sq.col,
                        row,
                        col
                    )

                    if self._is_promotion_move(row, col):
                        self.promotion_pending = True
                        self.promotion_sq = (row, col)
                        

                    else:
                        self.promotion_pending = False
                        

                    if is_castling:
                        if col > self.selected_sq.col:
                            self.board.move_piece(self.selected_sq.row, 7, self.selected_sq.row, 5)
                        else:
                            self.board.move_piece(self.selected_sq.row, 0, self.selected_sq.row, 3)
                        self.selected_piece.castled = True
                        
                        

                    if is_en_passant:
                        self.board.remove_piece(row-self.selected_piece.direction, col)

                    self.valid_moves = []
                    self.selected_piece = None
                    self.selected_sq = None

                    if not self.promotion_pending:
                        self.turn = 'black' if self.turn == 'white' else 'white'

                        self._detect_check()

                        if self.check:
                            self._detect_checkmate()

                        else:
                            self._detect_stalemate()


                elif piece and piece.color == self.selected_piece.color:
                    self.selected_piece = piece
                    self.selected_sq = self.board.get_square(row, col)
                    self.valid_moves = []
                    self._calculate_valid_moves(self.selected_sq)


    def handle_ai_move(self, best_move):
        self.board.move_piece(
            best_move[0][0],
            best_move[0][1],
            best_move[1][0],
            best_move[1][1]
        )

        self.turn = 'white' if self.turn == 'black' else 'white'

        self._detect_check()

        if self.check:
            self._detect_checkmate()

        else:
            self._detect_stalemate()



        



    def handle_promotion_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            piece_choice = None


            # Check if queen is clicked
            queen_x = (WIDTH / 8) - PROMOTION_PIECE_SIZE/2
            queen_y = PROMOTION_Y - PROMOTION_PIECE_SIZE/2

            if queen_x <= x <= queen_x + PROMOTION_PIECE_SIZE \
                and queen_y <= y <= queen_y + PROMOTION_PIECE_SIZE:
                piece_choice = 'queen'

            # rook
            rook_x = (3*WIDTH / 8) - PROMOTION_PIECE_SIZE/2
            rook_y = PROMOTION_Y - PROMOTION_PIECE_SIZE/2
            if rook_x <= x <= rook_x + PROMOTION_PIECE_SIZE \
                and rook_y <= y <= rook_y + PROMOTION_PIECE_SIZE:
                piece_choice = 'rook'

            bishop_x = (5*WIDTH / 8) - PROMOTION_PIECE_SIZE/2
            bishop_y = PROMOTION_Y - PROMOTION_PIECE_SIZE/2
            if bishop_x <= x <= bishop_x + PROMOTION_PIECE_SIZE \
                and bishop_y <= y <= bishop_y + PROMOTION_PIECE_SIZE:
                piece_choice = 'bishop'

            knight_x = (7*WIDTH / 8) - PROMOTION_PIECE_SIZE/2
            knight_y = PROMOTION_Y - PROMOTION_PIECE_SIZE/2
            if knight_x <= x <= knight_x + PROMOTION_PIECE_SIZE \
                and knight_y <= y <= knight_y + PROMOTION_PIECE_SIZE:
                piece_choice = 'knight'

            if piece_choice:
                self._get_player_choice(piece_choice)
                self.promotion_pending = False
                self.promotion_sq = None

                self.turn = 'black' if self.turn == 'white' else 'white'
                self._detect_check()

                if self.check:
                    self._detect_checkmate()

                else:
                    self._detect_stalemate()





        

            
            
            
            
            



    def _validate_move(self, move, moving_piece):
        row, col = move

        # Check board boundary
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False

        # Check if square is occupied by a friendly piece
        piece = self.board.get_piece(row, col)

        if piece and piece.color == moving_piece.color:
            return False

        return True


    def _validate_pawn_move(self, move):
        row, col = move

        # Check board boundary
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False

        # Pawn cannot move forward onto an occupied square
        piece = self.board.get_piece(row, col)

        if piece:
            return False

        return True


    def _validate_pawn_capture(self, move, pawn):
        row, col = move

        # Check board boundary
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False

        piece = self.board.get_piece(row, col)

        # Pawn can only capture an opponent's piece
        if not piece:
            return False

        if piece.color == pawn.color:
            return False

        return True

    def _validate_en_passant_capture(self, move, pawn):
        row, col = move

        if outside_board(row, col):
            return False

        if self.board.get_piece(row, col):
            return False

        if pawn.color == 'white':
            side_piece = self.board.get_piece(row+1, col)
        else:
            side_piece = self.board.get_piece(row-1, col)
        

        if not side_piece:
            return False

        if side_piece.color == pawn.color:
            return False

        if side_piece.name != 'pawn':
            return False

        if not side_piece.en_passantable:
            return False

        return True

        




    def _calculate_valid_moves(self, sq):
        pc = sq.piece

        if pc is None:
            return None

        if pc.name == 'knight':

            for move in pc.offsets:
                move = (
                    sq.row + move[0],
                    sq.col + move[1]
                )

                if self._validate_move(move, pc):
                    self.valid_moves.append(move)


        elif pc.name == 'pawn':

            forward = (sq.row + pc.direction, sq.col)

            if self._validate_pawn_move(forward):
                self.valid_moves.append(forward)

                if not pc.moved:
                    two_steps_forward = (
                        sq.row + pc.direction * 2,
                        sq.col
                    )

                    if self._validate_pawn_move(two_steps_forward):
                        self.valid_moves.append(two_steps_forward)

            left_capture = (
                sq.row + pc.direction,
                sq.col - 1
            )

            right_capture = (
                sq.row + pc.direction,
                sq.col + 1
            )


            if self._validate_pawn_capture(left_capture, pc):
                self.valid_moves.append(left_capture)

            if self._validate_pawn_capture(right_capture, pc):
                self.valid_moves.append(right_capture)

            if self._can_en_passant(pc, sq):
                if self._validate_en_passant_capture(right_capture, pc):
                    self.valid_moves.append(right_capture)

                if self._validate_en_passant_capture(left_capture, pc):
                    self.valid_moves.append(left_capture)

                
            


        elif pc.name == 'king':

            for move in pc.directions:
                move = (
                    sq.row + move[0],
                    sq.col + move[1]
                )

                if self._validate_move(move, pc):
                    self.valid_moves.append(move)

            if self._can_castle(sq, 1):
                self.valid_moves.append((sq.row, sq.col+2))
            if self._can_castle(sq, -1):
                self.valid_moves.append((sq.row, sq.col-2))

        else:

            for move in pc.directions:
                start = (sq.row, sq.col)

                current = (
                    start[0] + move[0],
                    start[1] + move[1]
                )

                while self._validate_move(current, pc):
                    self.valid_moves.append(current)

                    piece = self.board.get_piece(
                        current[0],
                        current[1]
                    )

                    if piece:
                        break

                    current = (
                        current[0] + move[0],
                        current[1] + move[1]
                    )

        # Remove moves that leave own king in check
        self.valid_moves = self._filter_legal_moves(sq)


    def _find_king(self):
        for row in self.board.board:
            for square in row:

                if square.piece and square.piece.name == 'king':

                    if square.piece.color == 'white':
                        self.white_king_sq = square
                    else:
                        self.black_king_sq = square


    def _is_attacking_king(self, square):
        king_sq = (
            self.white_king_sq
            if self.turn == 'white'
            else self.black_king_sq
        )

        if not square.piece:
            return False

        # Only opponent pieces can attack the current player's king
        if square.piece.color == self.turn:
            return False


        # Pawn attack
        if square.piece.name == 'pawn':

            if square.piece.color == 'white':
                left = (
                    square.row - 1,
                    square.col - 1
                )

                right = (
                    square.row - 1,
                    square.col + 1
                )

            else:
                left = (
                    square.row + 1,
                    square.col - 1
                )

                right = (
                    square.row + 1,
                    square.col + 1
                )

            if left == (king_sq.row, king_sq.col):
                return True

            if right == (king_sq.row, king_sq.col):
                return True


        # Knight attack
        elif square.piece.name == 'knight':

            for move in square.piece.offsets:
                target = (
                    square.row + move[0],
                    square.col + move[1]
                )

                if target == (king_sq.row, king_sq.col):
                    return True


        # King attack
        elif square.piece.name == 'king':

            for move in square.piece.directions:
                target = (
                    square.row + move[0],
                    square.col + move[1]
                )

                if target == (king_sq.row, king_sq.col):
                    return True


        # Bishop, rook and queen attacks
        else:

            for move in square.piece.directions:

                current = (
                    square.row + move[0],
                    square.col + move[1]
                )

                while self._validate_move(current, square.piece):

                    if current == (king_sq.row, king_sq.col):
                        return True

                    piece = self.board.get_piece(
                        current[0],
                        current[1]
                    )

                    if piece:
                        break

                    current = (
                        current[0] + move[0],
                        current[1] + move[1]
                    )

        return False


    def _detect_check(self):
        self._find_king()

        for row in self.board.board:
            for square in row:

                if self._is_attacking_king(square):
                    self.check = True
                    return True

        self.check = False
        return False

    def _detect_checkmate(self):
        if not self.check:
            return False
        
        for row in self.board.board:
            for square in row:
                if square.piece and square.piece.color == self.turn:
                    self.selected_square = square
                    self.selected_piece = square.piece

                    self.valid_moves = []
                    self._calculate_valid_moves(self.selected_square)

                    if self.valid_moves:
                        self.valid_moves = []
                        self.check_mate = False
                        return False
                    
               
        self.valid_moves = []
        self.check_mate = True   
        return True


    def _detect_stalemate(self):
        self.stale_mate = False
        self.valid_moves = []

        if self.check:
            return False

        for row in self.board.board:
            for square in row:
                if square.piece and square.piece.color == self.turn:
                    self._calculate_valid_moves(square)
                    if self.valid_moves:
                        self.valid_moves = []
                        return False

        self.valid_moves = []
        self.stale_mate = True
        return True

    def _can_castle(self, king_sq, direction):
        king = self.board.get_piece(king_sq.row, king_sq.col)

        if self.check or king.moved:
            return False
        
        if direction == 1:
            rook_sq = self.board.get_square(king_sq.row, king_sq.col+3)

        else:
            rook_sq = self.board.get_square(king_sq.row, king_sq.col-4)
        
        if not rook_sq.piece or rook_sq.piece.name != 'rook' or rook_sq.piece.color != self.turn:
            return False

        while king_sq.col <= 7 or king_sq.col >= 0:
            sq = (king_sq.row, king_sq.col)
            if self._is_square_attacked(sq):
                return False
            
            sq = (sq[0], sq[1]+direction)

        return True

    def _can_en_passant(self, pawn, pawn_sq):
        if pawn.color == 'white' and pawn_sq.row != 3:
            return False
        if pawn.color == 'black' and pawn_sq.row != 4:
            return False
        
        # Check neighboring colums
        right_piece = None
        left_piece = None
        if not outside_board(pawn_sq.row, pawn_sq.col+1):
            right_piece = self.board.get_piece(pawn_sq.row, pawn_sq.col+1)
        
        if not outside_board(pawn_sq.row, pawn_sq.col-1):
            left_piece = self.board.get_piece(pawn_sq.row, pawn_sq.col-1)

        if right_piece and right_piece.color != pawn.color\
              and right_piece.name == 'pawn'\
                  and right_piece.en_passantable:
            
            return True
        
        if left_piece and left_piece.color != pawn.color\
              and left_piece.name == 'pawn'\
                  and left_piece.en_passantable:
            
            return True

        return False

    def _is_promotion_move(self, row, col):
        if row not in (0,7):
            return False
        
        sq = self.board.get_square(row, col)

        if not sq.piece or sq.piece.name != 'pawn':
            return False
       
        if sq.piece.color == 'black' and sq.row == 7:
            return True
        
        if sq.piece.color == 'white' and sq.row == 0:
            return True


    def _get_player_choice(self, piece_choice:str):
        options = {'queen':Queen(self.turn),
        'rook':Rook(self.turn),
        'bishop':Bishop(self.turn), 
        'knight':Knight(self.turn)}

        if piece_choice not in options:
            return None
        
        piece = options[piece_choice]
        row, col = self.promotion_sq
        self.board.remove_piece(row, col)
        self.board.set_piece(row, col, piece)
    


        






    def _is_square_attacked(self, sq):
        enemy_sqs = self.board.get_enemy_squares(self.turn)
        for enemy_sq in enemy_sqs:
            # Check for squares attacked by pawns
            if enemy_sq.piece.name == 'pawn':
                left = (enemy_sq.row+enemy_sq.piece.direction, enemy_sq.col-1)
                right = (enemy_sq.row+enemy_sq.piece.direction, enemy_sq.col+1)

                if sq in (left, right):
                    return True

            # Check for squares attackd by knights
            elif enemy_sq.piece.name == 'knight':
                for offset in enemy_sq.piece.offsets:
                    attacked_sq = (enemy_sq.row+offset[0], enemy_sq.col+offset[1])
                    if attacked_sq == sq:
                        return True

            # Check for squares attacked by king
            elif enemy_sq.piece.name == 'king':
                for direction in enemy_sq.piece.directions:
                    attacked_sq = (enemy_sq.row+direction[0], enemy_sq.col+direction[1])
                    if attacked_sq == sq:
                        return True

            # Check for squares attacked by bishops, rooks, and queen
            else:
                for direction in enemy_sq.piece.directions:
                    attacked_sq = (enemy_sq.row+direction[0], enemy_sq.col+direction[1])

                    while not outside_board(attacked_sq[0], attacked_sq[1]):
                        if attacked_sq == sq:
                            return True
                        
                        if self.board.get_piece(attacked_sq[0], attacked_sq[1]):
                            break

                        attacked_sq = (attacked_sq[0]+direction[0], attacked_sq[1]+direction[1])

        return False

    def _can_castle(self, king_sq, direction):
        king = self.board.get_piece(king_sq.row, king_sq.col)

        if self.check or king.moved:
            return False
        if direction == 1:
            rook_col = king_sq.col+3
        else:
            rook_col = king_sq.col-4
        rook_sq = (king_sq.row, rook_col)

        piece = self.board.get_piece(rook_sq[0], rook_sq[1])

        if not piece or piece.name != 'rook':
            return False

        if piece.color != self.turn:
            return False

        if piece.moved:
            return False

        current_col = (king_sq.col+direction)

        while current_col != rook_col:

            if self.board.get_piece(king_sq.row, current_col):
                return False
            
            current_col = current_col+direction

        for i in range(3):
            current_col = king_sq.col+(i*direction)
            if self._is_square_attacked((king_sq.row, current_col)):
                return False

        return True

        





    def _filter_legal_moves(self, sq):
        legal_moves = []

        for move in self.valid_moves:

            source_row = sq.row
            source_col = sq.col

            dest_row, dest_col = move

            moving_piece = self.board.get_piece(
                source_row,
                source_col
            )

            captured_piece = self.board.get_piece(
                dest_row,
                dest_col
            )

            # Save pawn state before temporary move
            pawn_moved = None
            rook_moved = None
            king_moved = None

            if moving_piece.name == 'pawn':
                pawn_moved = moving_piece.moved
            if moving_piece.name == 'rook':
                rook_moved = moving_piece.moved
            if moving_piece.name == 'king':
                king_moved = moving_piece.moved

            # Make temporary move
            self.board.move_piece(
                source_row,
                source_col,
                dest_row,
                dest_col
            )

            self._find_king()
            self._detect_check()

            if not self.check:
                legal_moves.append(move)

            # Undo temporary move
            self.board.set_piece(
                source_row,
                source_col,
                moving_piece
            )

            self.board.set_piece(
                dest_row,
                dest_col,
                captured_piece
            )

            # Restore pawn state
            if moving_piece.name == 'pawn':
                moving_piece.moved = pawn_moved
            if moving_piece.name == 'rook':
                moving_piece.moved = rook_moved
            if moving_piece.name == 'king':
                moving_piece.moved = king_moved

            self._find_king()

        return legal_moves