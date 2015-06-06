import numpy as np
import pdb

# Why doesn't numpy have methods for these? Nonsense, I assume.
# For readability, I didn't combine these methods
def rotation_around_x_axis(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([1, 0            , 0             , 0])
    rotation[1] = np.array([0, np.cos(angle), -np.sin(angle), 0])
    rotation[2] = np.array([0, np.sin(angle),  np.cos(angle), 0])
    rotation[3] = np.array([0, 0            , 0             , 1])
    rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation

def rotation_around_y_axis(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([ np.cos(angle), 0, np.sin(angle), 0])
    rotation[1] = np.array([0             , 1, 0            , 0])
    rotation[2] = np.array([-np.sin(angle), 0, np.cos(angle), 0])
    rotation[3] = np.array([0             , 0, 0            , 1])
    rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation

def rotation_around_z_axis(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([np.cos(angle), -np.sin(angle), 0, 0])
    rotation[1] = np.array([np.sin(angle),  np.cos(angle), 0, 0])
    rotation[2] = np.array([0            , 0             , 1, 0])
    rotation[3] = np.array([0            , 0             , 0, 1])
    rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation


class Bone:

    def __init__(self, index, name, direction, length, axis, axis_values, degrees_of_freedom):
        self.index = index
        self.name = name
        self.direction = direction
        self.length = length
        self.axis = axis
        # These values represent the rotation from global coordinates to local coordinates
        # Order of rotation is x, y, z.
        self.x_axis, self.y_axis, self.z_axis = axis_values
        self.rotation_from_axes = self.compute_rotation_from_axes()
        self.rotation_to_axes = np.transpose(self.rotation_from_axes)
        self.rotation_from_parent = None
        self.degrees_of_freedom = degrees_of_freedom
        self.doftl = None
        self.sibling = None
        self.parent = None
        self.rotation_to_parent = np.zeros([4,4])
        self.rotation = None
        self.translation = None
        self.tl = None

    @staticmethod
    def create_root_bone(axis, axis_values):
        return Bone(0, "root", [0,0,0], 0, axis, axis_values, None)

    def compute_rotation_from_axes(self):
        x_rotation = rotation_around_x_axis(self.x_axis)
        y_rotation = rotation_around_y_axis(self.y_axis)
        z_rotation = rotation_around_z_axis(self.z_axis)
        # Full rotation is RzRyRx
        rotation = np.dot(z_rotation, np.dot(y_rotation, x_rotation))
        return rotation

    def compute_rotation_from_parent(self):
        rotation_to_parent = np.dot(self.parent.rotation_to_axes, self.rotation_from_axes)
        rotation_from_parent = np.transpose(rotation_to_parent)
        self.rotation_from_parent = rotation_from_parent