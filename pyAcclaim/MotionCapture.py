import numpy as np
import pyAcclaim.MatrixMath as matrix
import pyAcclaim.Render
import pyAcclaim.Bone
from copy import copy
from pdb import set_trace

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
        self.parent_to_child_rotations = self.calculate_parent_to_child_rotations()
        self.pose_rotations = self.calculate_pose_rotation_matrices()
        self.bone_end_points = self.calculate_bone_end_points()
        self.indexed_hierarchy = self.generate_indexed_hierarchy(hierarchy)
        self.bone_vectors, self.transformations = self.calculate_bone_vectors()

    # Create an array containing all the root translations in the scene-
    def generate_root_translations(self):
        root_translations = np.zeros([self.number_of_poses, 3])
        indices = self.root[0]
        x_index = indices.index("tx")
        y_index = indices.index("ty")
        z_index = indices.index("tz")
        for i in range(self.number_of_poses):
            root_translations[i][0] = self.poses[i]['root'][x_index]
            root_translations[i][1] = self.poses[i]['root'][y_index]
            root_translations[i][2] = self.poses[i]['root'][z_index]
        return root_translations

    # Calculates the rotations from parent coordinate systems to child coordinate systems.
    def calculate_parent_to_child_rotations(self) -> np.ndarray:
        parent_to_child_rotations = np.zeros([self.number_of_bones, 4, 4], dtype=np.double)
        for bone_name in [y for y in self.bone_data if y is not 'root']:
            bone = self.bone_data[bone_name]
            parent = bone.parent
            rotation = np.dot(bone.local_to_global_rotation, parent.global_to_local_rotation)
            parent_to_child_rotations[bone.index] = rotation
        parent_to_child_rotations[0] = matrix.identity_matrix
        return parent_to_child_rotations

    # Calculate the end points of each bone
    def calculate_bone_end_points(self) -> np.ndarray:
        bone_end_points = np.zeros([self.number_of_bones, 3], dtype=np.double)
        for bone_name in self.bone_data:
            bone = self.bone_data[bone_name]
            bone_vector = np.ones(4)
            # The x coordinate of the end point.
            bone_vector[0] = bone.length * bone.direction[0]
            # The y coordinate of the end point.
            bone_vector[1] = bone.length * bone.direction[1]
            # The z coordinate of the end point.
            bone_vector[2] = bone.length * bone.direction[2]
            # The end points of the bone in the bone's coordinate system
            rotated_end_points = np.dot(bone.local_to_global_rotation, bone_vector)

            bone_end_points[bone.index] = rotated_end_points[:3]
        return bone_end_points

    def calculate_bone_vectors(self) -> np.ndarray:
        bone_vectors = np.zeros([self.number_of_poses, self.number_of_bones, 2, 3], dtype=np.double)

        local_start = np.array([0, 0, 0, 1])
        all_transforms = np.zeros([self.number_of_poses, self.number_of_bones, 4, 4])

        for pose in range(self.number_of_poses):
            unvisited = ["root"]

            while unvisited:
                current_bone_name = unvisited.pop(0)
                bone = self.bone_data[current_bone_name]

                if bone.name in self.hierarchy:
                    for child in self.hierarchy[bone.name]:
                        unvisited.insert(0, child)

                parent = bone.parent
                if current_bone_name != "root":
                    pre_transformation = all_transforms[pose][parent.index]
                else:
                    pre_transformation = pyAcclaim.MatrixMath.identity_matrix
                    x, y, z = self.root_translations[pose]
                    translation_matrix = pyAcclaim.MatrixMath.create_translation_matrix(x, y, z)
                    translation_matrix = np.transpose(translation_matrix)
                    pre_transformation = np.dot(translation_matrix, pre_transformation)

                # Apply a rotation from the parent to the child
                transformation = np.dot(pre_transformation, self.parent_to_child_rotations[bone.index])
                # Apply the local rotation specific to this pose
                transformation = np.dot(self.pose_rotations[pose][bone.index], transformation)

                #start = np.dot(local_start, transformation)

                start = bone_vectors[pose][bone.parent.index][1]

                # The bone vector in local coordinates.
                x_translation = bone.length * bone.direction[0]
                y_translation = bone.length * bone.direction[1]
                z_translation = bone.length * bone.direction[2]

                # Create actual local bone vector
                local_end = copy(local_start)
                local_end[0] += x_translation
                local_end[1] += y_translation
                local_end[2] += z_translation

                end = np.dot(local_end, transformation)

                # Create a translation matrix to go to the end of the current bone.
                translation_matrix = pyAcclaim.MatrixMath.create_translation_matrix(x_translation, y_translation, z_translation)
                # Transpose it because OpenGL is in column-major order.
                translation_matrix = np.transpose(translation_matrix)
                #set_trace()
                # Apply the translation.
                transformation = np.dot(translation_matrix, transformation)

                end = np.dot(local_end, transformation)

                bone_vectors[pose][bone.index][0] = start[:3]
                bone_vectors[pose][bone.index][1] = end[:3]

                all_transforms[pose][bone.index] = transformation

        set_trace()
        return bone_vectors, all_transforms

    def calculate_pose_rotation_matrices(self) -> np.ndarray:
        pose_rotations = np.zeros([self.number_of_poses, self.number_of_bones, 4, 4])
        for pose in range(self.number_of_poses):
            for bone_name in self.bone_data:
                bone = self.bone_data[bone_name]

                x_angle = 0
                y_angle = 0
                z_angle = 0

                if "rx" in bone.dof_order:
                    x_angle = self.poses[pose][bone_name][bone.dof_order.index("rx")]
                if "ry" in bone.dof_order:
                    y_angle = self.poses[pose][bone_name][bone.dof_order.index("ry")]
                if "rz" in bone.dof_order:
                    z_angle = self.poses[pose][bone_name][bone.dof_order.index("rz")]

                x_angle *= np.pi / 180
                y_angle *= np.pi / 180
                z_angle *= np.pi / 180

                rotation_matrix = pyAcclaim.MatrixMath.calculate_euler_rotation_matrix(x_angle, y_angle, z_angle)

                rotation_matrix = np.transpose(rotation_matrix)

                pose_rotations[pose][bone.index] = rotation_matrix

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

    def generate_indexed_hierarchy(self, hierarchy) -> list:
        indexed_hierarchy = [[]] * self.number_of_bones
        for parent in hierarchy:
            index = self.bone_data[parent].index
            indexed_hierarchy[index] = [self.bone_data[x].index for x in hierarchy[parent]]
        return indexed_hierarchy

    def render(self):
        data = (self.bone_end_points, self.root_translations, self.parent_to_child_rotations, self.pose_rotations, self.indexed_hierarchy)
        pyAcclaim.Render.render(data)

    def render_global(self):
        #set_trace()
        pyAcclaim.Render.render_from_global(self.bone_vectors)

    def render_from_transforms(self):
        pyAcclaim.Render.render_from_transforms((self.bone_vectors, self.bone_end_points))

    def render_global_2(self):
        start_and_end = np.zeros([2,2,3])
        start_and_end[0][0] = [0,0,10]
        start_and_end[0][1] = [0,0,-10]
        start_and_end[1][0] = [-10,0,0]
        start_and_end[1][1] = [10,0,0]

        pyAcclaim.Render.render_from_global(start_and_end)
