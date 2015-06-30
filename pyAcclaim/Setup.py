import numpy as np

from pdb import set_trace


# When we render the data, we want to avoid
def do_full_setup(bones: list, bonedata: dict, pose_rotations: list, hierarchy: dict):
    number_of_bones = len(bones)
    number_of_poses = len(pose_rotations)
    assert(number_of_bones == len(bonedata))
    lengths = np.ndarray([number_of_bones], dtype=np.double)
    root_translations = np.ndarray([number_of_poses, 3])
    parent_to_child_rotations = calculate_parent_child_transforms(bonedata)
    pose_rotations = calculate_pose_rotations(bonedata, pose_rotations)
    direction_rotations = calculate_direction_rotations(bonedata)
    indexed_hierarchy = generate_indexed_hierarchy(hierarchy, bonedata)
    render()
    return 0


def calculate_parent_child_transforms(bonedata: dict) -> np.ndarray:
    number_of_bones = len(bonedata)
    parent_to_child_rotations = np.ndarray([number_of_bones, 4, 4], dtype=np.double)
    for x in [y for y in bonedata if y is not 'root']:
        bone = bonedata[x]
        parent = bone.parent
        rotation = np.dot(bone.rotation_from_global, parent.rotation_to_global)
        #set_trace()
        parent_to_child_rotations[bone.index] = rotation
    return parent_to_child_rotations


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


def calculate_direction_rotations(bonedata: dict) -> np.ndarray:
    # Each rotation is an axes (3 doubles) and an angle
    direction_rotations = np.ndarray([len(bonedata), 4], dtype=np.double)
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
    set_trace()
    return indexed_hierarchy

def x_rotate(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([1, 0            , 0             , 0])
    rotation[1] = np.array([0, np.cos(angle), -np.sin(angle), 0])
    rotation[2] = np.array([0, np.sin(angle),  np.cos(angle), 0])
    rotation[3] = np.array([0, 0            , 0             , 1])
    rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation


def y_rotate(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([ np.cos(angle), 0, np.sin(angle), 0])
    rotation[1] = np.array([0             , 1, 0            , 0])
    rotation[2] = np.array([-np.sin(angle), 0, np.cos(angle), 0])
    rotation[3] = np.array([0             , 0, 0            , 1])
    rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation


def z_rotate(angle):
    rotation = np.zeros([4,4])
    rotation[0] = np.array([np.cos(angle), -np.sin(angle), 0, 0])
    rotation[1] = np.array([np.sin(angle),  np.cos(angle), 0, 0])
    rotation[2] = np.array([0            , 0             , 1, 0])
    rotation[3] = np.array([0            , 0             , 0, 1])
    rotation.real[abs(rotation.real) < 1e-16] = 0.0
    return rotation