import numpy as np
import pyAcclaim.MatrixMath as matrix

class MotionCapture:

    def __init__(self, root, bones, bone_data, poses, hierarchy):
        self.root = root
        self.bones = bones
        self.bone_data = bone_data
        self.poses = poses
        self.hierarchy = hierarchy
        self.number_of_bones = len(bones)
        self.number_of_poses = len(poses)
        self.root_translations = self.generate_root_translations()
        self.parent_to_child_rotations = self.calculate_parent_to_child_transformations()
        self.pose_rotations = self.calculate_pose_rotations()
        self.bone_end_points = self.calculate_bone_end_points()
        self.indexed_hierarchy = self.generate_indexed_hierarchy()

    # Create an array containing all the root translations in the scene-
    def generate_root_translations(self):
        root_translations = np.zeros([self.number_of_poses, 3])
        indices = self.root[0]
        x_index = indices.index("TX")
        y_index = indices.index("TY")
        z_index = indices.index("TZ")
        for i in range(self.number_of_poses):
            root_translations[i][0] = self.poses[i]['root'][x_index]
            root_translations[i][1] = self.poses[i]['root'][y_index]
            root_translations[i][2] = self.poses[i]['root'][z_index]
        return root_translations

    # Calculates the rotations from child coordinate systems to parent coordinate systems.
    def calculate_child_to_parent_transformations(self) -> np.ndarray:
        child_to_parent_rotations = np.zeros([self.number_of_bones, 4, 4])
        for bone_name in [y for y in self.bone_data if y is not 'root']:
            bone = self.bone_data[bone_name]
            parent = bone.parent
            rotation = np.dot(parent.rotation_to_global, bone.rotation_from_global)
            child_to_parent_rotations[bone.index] = rotation
        child_to_parent_rotations[0] = matrix.identity_matrix
        return child_to_parent_rotations

    # Calculates the rotations from parent coordinate systems to child coordinate systems.
    def calculate_parent_to_child_transformations(self) -> np.ndarray:
        parent_to_child_rotations = np.zeros([self.number_of_bones, 4, 4], dtype=np.double)
        for bone_name in [y for y in self.bone_data if y is not 'root']:
            bone = self.bone_data[bone_name]
            parent = bone.parent
            rotation = np.dot(bone.rotation_to_global, parent.rotation_from_global)
            parent_to_child_rotations[bone.index] = rotation
        parent_to_child_rotations[0] = matrix.identity_matrix
        return parent_to_child_rotations

    # Calculate the end points of each bone
    def calculate_bone_end_points(self) -> np.ndarray:
        bone_end_points = np.zeros([self.number_of_bones, 3], dtype=np.double)
        for bone_name in self.bone_data:
            bone = self.bone_data[bone_name]
            global_end_points = np.ones(4)
            # The x coordinate of the end point.
            global_end_points[0] = bone.length * bone.direction[0]
            # The y coordinate of the end point.
            global_end_points[1] = bone.length * bone.direction[1]
            # The z coordinate of the end point.
            global_end_points[2] = bone.length * bone.direction[2]
            rotated_end_points = np.dot(bone.rotation_to_global, global_end_points)

            bone_end_points[bone.index] = rotated_end_points[:3]
        return bone_end_points

    # Each pose consists of a set of rotations for each bone (and very rarely translations and length changes.
    # That's not supported yet). This returns the set of all rotations.
    def calculate_pose_rotations(self) -> np.ndarray:
        # The values for each rotation of each bone of each pose. XYZ ordering.
        pose_rotations = np.zeros([self.number_of_poses, self.number_of_bones, 3])
        for i in range(self.number_of_poses):
            for bone_name in self.bone_data:
                bone = self.bone_data[bone_name]
                if "rx" in bone.dof_order:
                    pose_rotations[i][bone.index][0] = self.poses[i][bone_name][bone.dof_order.index("rx")]
                if "ry" in bone.dof_order:
                    pose_rotations[i][bone.index][1] = self.poses[i][bone_name][bone.dof_order.index("ry")]
                if "rz" in bone.dof_order:
                    pose_rotations[i][bone.index][2] = self.poses[i][bone_name][bone.dof_order.index("rz")]
        return pose_rotations

    def generate_directions(self) -> np.ndarray:
        directions = np.zeros([self.number_of_bones, 3], dtype=np.double)
        for bone_name in self.bone_data:
            bone_index = self.bone_data[bone_name].index
            directions[bone_index] = self.bone_data[bone_name].direction
        return directions

    # Used to rotate the local coordinate system of a bone
    def calculate_direction_rotations(self) -> np.ndarray:
        # Each rotation is an axis (3 doubles) and an angle
        direction_rotations = np.zeros([self.number_of_bones, 4], dtype=np.double)
        z_axis = np.array([0, 0, 1])
        z_axis_length = np.linalg.norm(z_axis)
        for bone_name in self.bone_data:
            bone = self.bone_data[bone_name]
            # We need to rotate to the z-axis
            axis = np.cross(bone.direction, z_axis)
            dot_product = np.dot(bone.direction, z_axis)
            try:
                # To get the angle we only need to divide by the length of the z axis,
                # since direction is always a unit vector (or 0).
                angle = np.arccos(dot_product / z_axis_length)
            except ZeroDivisionError:
                angle = 0
            direction_rotations[bone.index][:3] = axis
            direction_rotations[bone.index][3] = angle

        return direction_rotations

    def generate_indexed_hierarchy(self) -> list:
        indexed_hierarchy = [[]] * self.number_of_bones
        for parent in self.hierarchy:
            index = self.bone_data[parent].index
            indexed_hierarchy[index] = [self.bone_data[x].index for x in self.hierarchy[parent]]
        return indexed_hierarchy

MotionCapture.generate_root_translations()