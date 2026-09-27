from constants import *
class Piece:
    def __init__(self, name, value, color):
        self.name = name
        self.value = value
        self.color = color
       


class Pawn(Piece):
    def __init__(self, color):
        super().__init__("pawn", 1, color)
        self.moved = False
        self.direction = -1 if self.color == 'white' else 1
        self.en_passantable = False


class Knight(Piece):
    def __init__(self, color):
        super().__init__("knight", 3.0, color)
        self.offsets = [[2, -1],[2, 1],[-2, -1],[-2, 1],[1, -2],[1, 2],[-1, -2],[-1, 2]]
   

class Bishop(Piece):
    def __init__(self, color):
        super().__init__("bishop", 3.0, color)
        self.directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        

class Rook(Piece):
    def __init__(self, color):
        super().__init__("rook", 5.0, color)
        self.moved = False
        self.directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

class Queen(Piece):
    def __init__(self, color):
        super().__init__("queen", 9.0, color)        
        self.directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]


class King(Piece):
    def __init__(self, color):
        super().__init__("king", 10000.0, color) 
        self.moved = False
        self.castled = False
        self.directions = [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]


        

