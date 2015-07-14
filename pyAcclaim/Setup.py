from .MatrixMath import identity_matrix
from pdb import set_trace
import numpy as np


def do_full_setup(root: list, bones: list, bone_data: dict, poses: list, hierarchy: dict) -> tuple:
    number_of_bones = len(bones)
    number_of_poses = len(poses)
    assert(number_of_bones == len(bone_data))

    root_translations = generate_root_translations(root, poses)
    child_to_parent_rotations = calculate_parent_to_child_transformations(bone_data)
    pose_rotations = calculate_pose_rotations(bone_data, poses)
    bone_end_points = calculate_bone_end_points(bone_data)
    # Unused for now.
    # directions = generate_directions(bonedata, poses)
    # direction_rotations = calculate_direction_rotations(bonedata)
    # lengths = np.zeros([number_of_bones], dtype=np.double)
    indexed_hierarchy = generate_indexed_hierarchy(hierarchy, bone_data)
    return (bone_end_points, root_translations, child_to_parent_rotations, pose_rotations, indexed_hierarchy)


def generate_root_translations(root: list, poses: list) -> np.ndarray:
    number_of_poses = len(poses)
    root_translations = np.zeros([number_of_poses, 3])
    indices = root[0]
    x_index = indices.index("TX")
    y_index = indices.index("TY")
    z_index = indices.index("TZ")
    for i in range(number_of_poses):
        root_translations[i] = poses[i]['root'][:3]
    return root_translations


# Calculates the rotations from child coordinate systems to parent coordinate systems.
def calculate_child_to_parent_transformations(bonedata: dict) -> np.ndarray:
    number_of_bones = len(bonedata)
    child_to_parent_rotations = np.zeros([number_of_bones, 4, 4])
    for bone_name in [y for y in bonedata if y is not 'root']:
        bone = bonedata[bone_name]
        parent = bone.parent
        rotation = np.dot(parent.rotation_from_global, bone.rotation_to_global)
        child_to_parent_rotations[bone.index] = rotation
    child_to_parent_rotations[0] = identity_matrix
    return child_to_parent_rotations


# Calculates the rotations from parent coordinate systems to child coordinate systems.
def calculate_parent_to_child_transformations(bonedata: dict) -> np.ndarray:
    number_of_bones = len(bonedata)
    parent_to_child_rotations = np.zeros([number_of_bones, 4, 4], dtype=np.double)
    for bone_name in [y for y in bonedata if y is not 'root']:
        bone = bonedata[bone_name]
        parent = bone.parent
        rotation = np.dot(bone.rotation_from_global, parent.rotation_to_global)
        parent_to_child_rotations[bone.index] = rotation
    parent_to_child_rotations[0] = identity_matrix
    return parent_to_child_rotations


# Calculate the end points of each bone
def calculate_bone_end_points(bone_data: dict) -> np.ndarray:
    bone_end_points = np.zeros([len(bone_data), 3], dtype=np.double)
    for bone_name in bone_data:
        bone = bone_data[bone_name]
        global_end_points = np.ones(4)
        # The x coordinate of the end point.
        global_end_points[0] = bone.length * bone.direction[0]
        # The y coordinate of the end point.
        global_end_points[1] = bone.length * bone.direction[1]
        # The z coordinate of the end point.
        global_end_points[2] = bone.length * bone.direction[2]
        rotated_end_points = np.dot(bone.rotation_from_global, global_end_points)

        bone_end_points[bone.index] = rotated_end_points[:3]
    return bone_end_points


# Each pose consists of a set of rotations for each bone (and very rarely translations and length changes. That's not
# supported yet). This returns the set of all rotations.
def calculate_pose_rotations(bonedata: dict, poses: list) -> np.ndarray:
    number_of_bones = len(bonedata)
    number_of_poses = len(poses)
    # The values for each rotation of each bone of each pose. XYZ ordering.
    pose_rotations = np.zeros([number_of_poses, number_of_bones, 3])
    for i in range(len(poses)):
        for bone_name in bonedata:
            bone = bonedata[bone_name]
            if "rx" in bone.dof_order:
                pose_rotations[i][bone.index][0] = poses[i][bone_name][bone.dof_order.index("rx")]
            if "ry" in bone.dof_order:
                pose_rotations[i][bone.index][1] = poses[i][bone_name][bone.dof_order.index("ry")]
            if "rz" in bone.dof_order:
                pose_rotations[i][bone.index][2] = poses[i][bone_name][bone.dof_order.index("rz")]
    return pose_rotations


def generate_directions(bonedata: dict, poses: list) -> np.ndarray:
    directions = np.zeros([len(bonedata), 3], dtype=np.double)
    for bone_name in bonedata:
        bone_index = bonedata[bone_name].index
        directions[bone_index] = bonedata[bone_name].direction
    return directions


# Used to rotate the local coordinate system of a bone
def calculate_direction_rotations(bonedata: dict) -> np.ndarray:
    # Each rotation is an axis (3 doubles) and an angle
    direction_rotations = np.zeros([len(bonedata), 4], dtype=np.double)
    z_axis = np.array([0, 0, 1])
    z_axis_length = np.linalg.norm(z_axis)
    for bone_name in bonedata:
        bone = bonedata[bone_name]
        # We need to rotate to the z-axis
        axis = np.cross(bone.direction, z_axis)
        dot_product = np.dot(bone.direction, z_axis)
        try:
            # To get the angle we only need to divide by the length of the z axis,
            # since direction is always a unit vector (or 0).
            angle = np.arccos(dot_product / z_axis_length)
        except Exception:
            angle = 0
        direction_rotations[bone.index][:3] = axis
        direction_rotations[bone.index][3] = angle

    return direction_rotations


def generate_indexed_hierarchy(hierarchy: dict, bonedata: dict) -> list:
    indexed_hierarchy = [[]] * len(bonedata)
    for parent in hierarchy:
        index = bonedata[parent].index
        indexed_hierarchy[index] = [bonedata[x].index for x in hierarchy[parent]]
    return indexed_hierarchy
