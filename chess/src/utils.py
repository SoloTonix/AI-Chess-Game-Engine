from constants import *

def convert_pixel_to_matrix(pos):
    row, col= pos[1]//SQSIZE, pos[0]//SQSIZE
    
    return (row, col)

def outside_board(row, col):
    if row < 0 or row > 7 or col < 0 or col > 7:
        return True
    return False
