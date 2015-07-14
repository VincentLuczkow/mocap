import numpy as np

identity_matrix = np.zeros([4,4])
for i in range(4):
    identity_matrix[i][i] = 1

# Rotates vector by x_angle around the x axis, then y_angle around the y axis, then z_angle around
# the z_axis.
def euler_rotate(vector: np.ndarray, x_angle: float, y_angle: float, z_angle: float) ->np.ndarray:
    # The desires rotation matrix.
    rotation_matrix = calculate_euler_rotation_matrix(x_angle, y_angle, z_angle)

    # Rotate vector, in XYZ order.
    # Returned vector is Z * Y * X * vector
    rotated_vector = matrix_operate(rotation_matrix, vector)
    return rotated_vector


# Returns a matrix that rotates by x_angle around the x axis, then y_angle around the y_axis, then z_angle around
# the z_axis.
def calculate_euler_rotation_matrix(x_angle: float, y_angle: float, z_angle: float) -> np.ndarray:
    # Calculate X: the matrix for rotation around the x axis.
    x_rotation = x_rotate(x_angle)
    # Calculate Y: the matrix for rotation around the y axis.
    y_rotation = y_rotate(y_angle)
    # Calculate Z: the matrix for rotation around the z axis.
    z_rotation = z_rotate(z_angle)

    temp = np.dot(z_rotation, y_rotation)
    rotation_matrix = np.dot(temp, x_rotation)
    return rotation_matrix

# Returns a rotation in reverse order: z, then y, then x
def calculate_reverse_euler_rotation_matrix(x_angle: float, y_angle: float, z_angle: float) -> np.ndarray:
    # Calculate X: the matrix for rotation around the x axis.
    x_rotation = x_rotate(x_angle)
    # Calculate Y: the matrix for rotation around the y axis.
    y_rotation = y_rotate(y_angle)
    # Calculate Z: the matrix for rotation around the z axis.
    z_rotation = z_rotate(z_angle)

    temp = np.dot(x_rotation, y_rotation)
    rotation_matrix = np.dot(temp, z_rotation)
    return rotation_matrix


def z_rotate(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([np.cos(angle), -np.sin(angle), 0, 0])
    rotation[1] = np.array([np.sin(angle),  np.cos(angle), 0, 0])
    rotation[2] = np.array([0            , 0             , 1, 0])
    rotation[3] = np.array([0            , 0             , 0, 1])
    # rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation


def y_rotate(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([ np.cos(angle), 0, np.sin(angle), 0])
    rotation[1] = np.array([0             , 1, 0            , 0])
    rotation[2] = np.array([-np.sin(angle), 0, np.cos(angle), 0])
    rotation[3] = np.array([0             , 0, 0            , 1])
    # rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation


def x_rotate(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([1, 0            , 0             , 0])
    rotation[1] = np.array([0, np.cos(angle), -np.sin(angle), 0])
    rotation[2] = np.array([0, np.sin(angle),  np.cos(angle), 0])
    rotation[3] = np.array([0, 0            , 0             , 1])
    # rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation

# Applies a 4x4 matrix to a 3 vector.
def matrix_operate(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    new_vector = np.zeros(3)

    for i in range(3):
        for j in range(3):
            new_vector += matrix[i][j] * vector[j]

    return new_vector