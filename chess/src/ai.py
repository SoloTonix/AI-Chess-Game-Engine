from values import get_piece_square_value





class AI:
    def __init__(self, game, color):
        self.game = game
        self.color = color
        self.opponent_color = 'white' if self.color == 'black' else 'white'
        self.nodes = 0
        self.prunes = 0
        

    def _calculate_moves(self, game, board, color):
        moves = []
        real_board = game.board
        game.board =  board
        for row in board.board:
            for sq in row:
                if sq.piece and sq.piece.color == color:
                    game.valid_moves = []
                    game._calculate_valid_moves(sq)
                    for move in game.valid_moves:
                        source = sq.matrix
                        moves.append((source,move))

        game.board = real_board
        return moves

    def simulate_moves(self, moves, board):
        simulations = {}
        for source, dest in moves:
            simulated_board = board.copy()
            simulated_board.move_piece(source[0], source[1], dest[0], dest[1])
            simulations[(source, dest)] = simulated_board
        return simulations


    def _evaluate_mobility_value(self, game, board, color):
        opp_color = 'white' if color == 'black' else 'black'

        ai_moves = len(self._calculate_moves(game, board, color))
        opp_moves = len(self._calculate_moves(game, board, opp_color))

        return ai_moves-opp_moves * 0.05

    def _evaluate_double_pawn(self, board, color):
        counts = [0] * 8
       
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col].piece

                if piece is None:
                    continue
                if piece.name != 'pawn':
                    continue
                if piece.color != color:
                    continue

                counts[col] += 1

        penalty = 0

        for count in counts:
            if count > 1:
                extra_pawns = count-1
                penalty -= extra_pawns * 0.25

        return penalty


    def _evaluate_isolated_pawn(self, board, color):
        penalty = 0

        for row in range(8):
            for col in range(8):

                piece = board.board[row][col].piece

                # Check piece exists
                if piece is None:
                    continue

                # If piece exists, check if it is a pawn
                if piece.name != 'pawn':
                    continue

                # If piece is a pawn, confirm it is of the given color
                if piece.color != color:
                    continue

                has_adjacent_pawn = False

                # Check left file and ensure you are not out of bound
                if col > 0:
                    for adjacent_row in range(8):
                        adjacent_piece = board.board[adjacent_row][col-1].piece

                        if (
                            adjacent_piece is not None
                            and adjacent_piece.name == 'pawn'
                            and adjacent_piece.color == color
                        ):
                            has_adjacent_pawn = True
                            break

                # Check right fileand ensure you are not out of bound
                if not has_adjacent_pawn and col < 7:
                    for adjacent_row in range(8):
                        adjacent_piece = board.board[adjacent_row][col+1].piece

                        if (
                            adjacent_piece is not None
                            and adjacent_piece.name == 'pawn'
                            and adjacent_piece.color == color
                        ):
                            has_adjacent_pawn = True
                            break

                if not has_adjacent_pawn:
                    penalty -= 0.25

        return penalty


    def _evaluate_passed_pawn(self, board, color):
        score = 0

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col].piece

                if piece is None:
                    continue
                if piece.name != 'pawn':
                    continue
                if piece.color != color:
                    continue

              
                direction = piece.direction

                files_to_check = [col]

                if col < 7:
                    files_to_check.append(col+1)

                if col > 0:
                    files_to_check.append(col-1)

                check_row = row + direction

                passed = True

                while 0 <= check_row <= 7:

                    for file in files_to_check:
                        target_piece = board.board[check_row][file].piece

                        if (
                            target_piece is not None
                            and target_piece.name == 'pawn'
                            and target_piece.color != color
                        ):

                            passed = False
                            break

                    if not passed:
                        break

                    check_row += direction

                if passed:
                    score += 0.5

        return score 


    def _evaluate_king_pawn_shield(self, board, color):
        shield_score = 0

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col].piece

                if piece is None:
                    continue

                if piece.name != 'king':
                    continue

                if piece.color != color:
                    continue

                direction = -1 if color == 'white' else 1
                check_row = row + direction

                if not 0 <= check_row < 8:
                    return 0

                # Check shield squares in front of the king
                shield_cols = [col]

                if col > 0:
                    shield_cols.append(col - 1)

                if col < 7:
                    shield_cols.append(col + 1)

                for shield_col in shield_cols:
                    target_piece = board.board[check_row][shield_col].piece

                    if (
                        target_piece is None
                        or target_piece.color != color
                        or target_piece.name != 'pawn'
                    ):
                        shield_score -= 1
                    else:
                        shield_score += 1

        return shield_score * 0.2



    def _evaluate_king_attack_pressure(self, board, color):
        attack_score = 0

        surrounding_sqs = []

        # Find the king and build the squares surrounding it
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col].piece

                if piece is None:
                    continue

                if piece.name != 'king':
                    continue

                if piece.color != color:
                    continue

                king = piece

                for direction in king.directions:
                    check_row = row + direction[0]
                    check_col = col + direction[1]

                    if 0 <= check_row < 8 and 0 <= check_col < 8:
                        surrounding_sqs.append((check_row, check_col))

        # Find enemy pieces and determine whether
        # they attack any square around the king
        for row in board.board:
            for sq in row:
                if sq.piece is None:
                    continue

                if sq.piece.color == color:
                    continue

                attacking_piece = sq.piece

                # Pawn
                if attacking_piece.name == 'pawn':

                    left = (
                        sq.row + attacking_piece.direction,
                        sq.col - 1
                    )

                    right = (
                        sq.row + attacking_piece.direction,
                        sq.col + 1
                    )

                    attacking_sqs = [left, right]

                    for attack_sq in attacking_sqs:
                        if attack_sq in surrounding_sqs:
                            attack_score -= 0.1

                # Knight
                elif attacking_piece.name == 'knight':

                    attacking_sqs = []

                    for offset in attacking_piece.offsets:
                        attacking_sqs.append(
                            (
                                sq.row + offset[0],
                                sq.col + offset[1]
                            )
                        )

                    for attack_sq in attacking_sqs:
                        if attack_sq in surrounding_sqs:
                            attack_score -= 0.1

                # King
                elif attacking_piece.name == 'king':

                    attacking_sqs = []

                    for direction in attacking_piece.directions:
                        attacking_sqs.append(
                            (
                                sq.row + direction[0],
                                sq.col + direction[1]
                            )
                        )

                    for attack_sq in attacking_sqs:
                        if attack_sq in surrounding_sqs:
                            attack_score -= 0.1

                # Bishop, Rook and Queen
                else:

                    for direction in attacking_piece.directions:

                        check_row = sq.row + direction[0]
                        check_col = sq.col + direction[1]

                        while 0 <= check_row < 8 and 0 <= check_col < 8:

                            target_piece = board.board[check_row][check_col].piece

                            # Empty square
                            if target_piece is None:

                                if (check_row, check_col) in surrounding_sqs:
                                    attack_score -= 0.1

                            # Occupied square
                            else:

                                # The attacking piece can attack the target
                                # only if the target belongs to the opposite color.
                                if (
                                    target_piece.color != attacking_piece.color
                                    and (check_row, check_col) in surrounding_sqs
                                ):
                                    attack_score -= 0.1

                                # Any piece blocks the ray
                                break

                            check_row += direction[0]
                            check_col += direction[1]

        return attack_score

                    
    def _evaluate_king_castle(self, board, color):
        bonus = 0
        for row in board.board:
            for sq in row:
                if sq.piece is None:
                    continue
                if sq.piece.color != color:
                    continue
                if sq.piece.name != 'king':
                    continue

                if sq.piece.castled:
                    bonus += 0.2

        return bonus


    def evaluate_board(self, game, board):
        total_value = 0

        # add mobility value first
        mobility_value = self._evaluate_mobility_value(game, board, self.color)
        

        # AI pawn structure evaluation
        ai_pawn_structure = (
            self._evaluate_double_pawn(board, self.color)
            + self._evaluate_isolated_pawn(board, self.color)
            + self._evaluate_passed_pawn(board, self.color)
        )


        # Opponent pawn structure evalation
        opponent_pawn_structure = (
            self._evaluate_double_pawn(board, self.opponent_color)
            + self._evaluate_isolated_pawn(board, self.opponent_color)
            + self._evaluate_passed_pawn(board, self.opponent_color)
        )

        # AI king safety
        ai_king_safety = (
            self._evaluate_king_pawn_shield(board, self.color)
            + self._evaluate_king_attack_pressure(board, self.color)
            + self._evaluate_king_castle(board, self.color)
        )


        # Opponent king safety
        opponent_king_safety = (
            self._evaluate_king_pawn_shield(board, self.opponent_color)
            + self._evaluate_king_attack_pressure(board, self.opponent_color)
            + self._evaluate_king_castle(board, self.opponent_color)
        ) 


        total_value += ai_pawn_structure - opponent_pawn_structure
        total_value += ai_king_safety - opponent_king_safety
        total_value += mobility_value
        

        for row in board.board:
            for sq in row:
                if sq.piece is None:
                    continue

                material_value = sq.piece.value
                square_value = get_piece_square_value(sq.piece, sq.matrix[0], sq.matrix[1])*0.7
                value = material_value + square_value

                if sq.piece.color == self.color:
                    total_value += value
                else:
                    total_value -= value

        return total_value


    def _is_in_check(self, game, board, color):
        real_board = game.board
        real_turn = game.turn
        real_check = game.check

        game.board = board
        game.turn = color
        game._detect_check()

        in_check = game.check

        game.board = real_board
        game.turn = real_turn
        game.check = real_check

        return in_check



        

    def search(self, game, board, depth, alpha, beta, color):
        opponent_color = self.opponent_color if color == self.color else self.color
        moves = self._calculate_moves(game, board, color)
        checkmate_score = 100000
        self.nodes += 1
        

        if not moves:
            in_check = self._is_in_check(game, board, color)

            if in_check:
                if color == self.color:
                    return -checkmate_score
                else:
                    return checkmate_score

            return 0

        
        if depth == 0:
            return self.evaluate_board(game, board)

        
        simulations = self.simulate_moves(moves, board)

        best_score = None

        for move, position in simulations.items():
            value = self.search(
                game, 
                position, 
                depth-1,
                alpha, 
                beta,
                opponent_color
            )
            

            if color == self.color:
                if best_score is None or value > best_score:
                    best_score = value
                    alpha = max(alpha, best_score)

            else:
                if best_score is None or value < best_score:
                    best_score = value
                    beta = min(beta, best_score)

            if alpha >= beta:
                self.prunes += 1
                break


        return best_score



    def choose_best_move(self, game, board, color):
        self.nodes = 0
        self.prunes = 0
        best_move, best_score = None, None
        ai_moves = self._calculate_moves(game, board, color)
        simulations = self.simulate_moves(ai_moves, board)
        alpha, beta = float('-inf'), float('inf')
        for move, position in simulations.items():
            depth = 1
            print("SEARCH:", "depth =", depth, "color =", color)
            value = self.search(game, position, depth, alpha, beta, self.opponent_color)
            print(f'value nd move: {value}{move}')
            if best_score is None or value > best_score:
                best_score = value
                best_move = move
                alpha = max(alpha, best_score)

        print(f'No of nodes is {self.nodes}')
        print(f'No of prunes is {self.prunes}')


        return best_move
                



        

