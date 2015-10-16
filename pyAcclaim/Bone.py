import numpy as np
from .MatrixMath import calculate_euler_rotation_matrix
from pdb import set_trace

# Why doesn't numpy have methods for these? Nonsense, I assume.
# For readability, I didn't combine these methods
from pyAcclaim.MatrixMath import z_rotate, y_rotate, x_rotate


class Bone:
    def __init__(self, index: int, name: str, direction: list, length: float, axes: str, rotation_from_global_axes: list,
                 dof_order: list, degrees_of_freedom: dict):
        self.index = int(index)
        self.name = name
        self.direction = np.array(direction)
        self.length = length
        # These values represent the rotation from global coordinates to local coordinates
        # Order of rotation is x, y, z.
        self.global_to_local_angles = Bone.get_axis_values(axes, rotation_from_global_axes)
        self.global_to_local_rotation = self.compute_rotation_from_global()
        # Inverse of a rotation is its transpose
        self.local_to_global_rotation = np.transpose(self.global_to_local_rotation)
        self.rotation_from_parent = None
        self.dof_order = dof_order
        self.degrees_of_freedom = degrees_of_freedom
        self.children = {}
        self.parent = None

    @staticmethod
    def create_root_bone(axis: str, rotation_from_global_axes: list, order: list):
        root_bone = Bone(0, "root", [0, 0, 1], 0, axis.lower(), rotation_from_global_axes, order, {})
        root_bone.parent = root_bone
        return root_bone

    @staticmethod
    # The axes do not have to be in XYZ order in the ASF file. This function converts them to XYZ order.
    def get_axis_values(axes: str, values: list) -> np.ndarray:
        angles = np.zeros(3)
        angles[0] = values[axes.index('x')]
        angles[1] = values[axes.index('y')]
        angles[2] = values[axes.index('z')]
        return angles

    # Computes a rotation matrix that converts from global coordinates to local coordinates.
    def compute_rotation_from_global(self)-> np.ndarray:
        x_angle = self.global_to_local_angles[0]
        y_angle = self.global_to_local_angles[1]
        z_angle = self.global_to_local_angles[2]
        rotation = calculate_euler_rotation_matrix(x_angle, y_angle, z_angle)
        return rotation
