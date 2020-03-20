import numpy as np
#TODO: Refactor to rotation_matrix
def matrix_rotation(theta):
    theta = np.radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s,c)))
    return R
