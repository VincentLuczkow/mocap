import re
import sys
from numpy import pi
from Skeleton import Bone
from pdb import set_trace


def parse_pose(lines):
    angles = {}
    for line in lines:
        values = line.split(" ")
        new_angles = [float(x) for x in values[1:]]
        angles[values[0]] = new_angles

    return angles


def parse_amc_file(file_name):
    with open(file_name, "r") as pose_file:
        lines = pose_file.readlines()
    poses = []
    marker = 0
    while marker < len(lines):
        if re.match(r'\d+', lines[marker]):
            start = marker + 1
            marker += 1
            end = len(lines) - 1
            while marker < len(lines):
                if re.match(r'\d+', lines[marker]):
                    end = marker - 1
                    break
                marker += 1
            poses.append(parse_pose(lines[start:end]))
    return poses


# Assumes ASF file is in the following format:
# Comments
# ...
# :version version
# :name name
# :units
# ...
# :documentation
# ...
# :root
# ...
# :bonedata
# ...
# :hierarchy
# ...
def parse_asf_file(asf_file_name):
    with open(asf_file_name, "r") as ASF_file:
        lines = iter(ASF_file.readlines())
        # Skip past starting comments
        # Then read the whole file
        for line in lines:
            if line.strip().split(" ")[0] == ":version":
                version = parse_asf_version(line)
                name = parse_asf_name(next(lines))

                check_header(":units", lines)
                units = parse_asf_units(lines)

                check_header(":documentation", lines)
                documentation = parse_asf_documentation(lines)

                root = parse_asf_root(lines)

                check_header(":bonedata", lines)
                bones, bonedata = parse_asf_bonedata(lines, units[2])
                root = Bone.create_root_bone(root[1], root[3])
                root.rotation_from_parent = root.rotation_from_axes
                bonedata['root'] = root

                hierarchy = parse_asf_hierarchy(lines, bonedata)
                set_trace()

                return version, name, units, documentation, root, bones, bonedata, hierarchy
    # This code is only reachable if :version never gets read.
    raise EOFError("File's not in the right format. :version was never parsed")


# Makes sure the next line in lines matches "header"
def check_header(header, lines):
    header_line = next(lines)
    try:
        assert header_line.strip() == header
    except AssertionError:
        print("Parser went wrong somewhere. Header: " + header + " not properly parsed.")
        set_trace()


def parse_asf_version(line):
    try:
        version = line.strip().split()[1]
    except IndexError:
        print(":version line does not contain a version number.")
        exit(0)
    return version


def parse_asf_name(line):
    try:
        name = line.strip().split(" ")[1]
    except IndexError:
        print(":name line does not contain a name.")
        exit(0)
    return name


# Assumes :units is in the following format:
# :unit
#   mass float
#   length float
#   angle deg|rad
def parse_asf_units(lines):
    mass = float(next(lines).strip().split()[1])
    length = float(next(lines).strip().split()[1])
    deg = next(lines).strip().split()[1]
    return mass, length, deg


# Assumes :documentation is in the following format:
# :documentation
#   ...
def parse_asf_documentation(lines):
    documentation = ""
    for line in lines:
        if line.strip() == ":root":
            break
        else:
            documentation += line.strip() + "\n"
    return documentation


# Assumes root is in the following format:
# :root
#   order
#   axis
#   position
#   orientation
def parse_asf_root(lines):
    order = next(lines).strip().split(" ")[1:]
    axis = next(lines).strip().split(" ")[1]
    position = [float(x) for x in next(lines).strip().split(" ")[1:]]
    orientation = [float(x) for x in next(lines).strip().split(" ")[1:]]
    return order, axis, position, orientation


def parse_asf_bonedata(lines, degree_type):
    bones = ['root']
    bonedata = {}
    for line in lines:
        #print(line)
        if line.strip() == "begin":
            new_bone = parse_asf_bone(lines, degree_type)
            bones.append(new_bone.name)
            bonedata[new_bone.name] = new_bone
        elif line.strip() == ":hierarchy":
            break
        else:
            print("Parser went wrong somewhere. Bonedata not parsed correctly")
            set_trace()
    return bones, bonedata


# Assumes bone is in the format:
def parse_asf_bone(lines, degree_type):
    index = next(lines).strip().split()[1]
    name = next(lines).strip().split()[1]
    split_line = next(lines).strip().split()
    direction = [float(x) for x in split_line[1:]]
    length = float(next(lines).strip().split()[1])
    axis_line = next(lines).strip().split()
    # If angles are given as degrees
    if degree_type == "deg":
        multiplier = pi / 180
    # If angles are given as radians
    else:
        multiplier = 1.0
    # The rotations from each axis for this bone.
    axis_values = [float(x) * multiplier for x in axis_line[1:4]]
    axis = axis_line[4]
    # Check if this bone has any degrees of freedom
    degrees_of_freedom = parse_degrees_of_freedom(lines)
    bone = Bone(index, name, direction, length, axis, axis_values, degrees_of_freedom)
    return bone


def parse_degrees_of_freedom(lines):
    dof_line = next(lines).strip().split(" ")
    # If no limitations are being declared.
    if dof_line[0] != "dof":
        return None
    degrees_of_freedom = {}
    # The first limits string is in the format:
    # limits (lower_limit upper_limit)
    limits_string = next(lines).strip().split(" ")[1:]
    for direction in dof_line[1:]:
        # The lower limit is in the format (float.
        # We cut off the open paren
        lower_limit = float(limits_string[0][1:])
        # The upper limit is in the format float).
        # We cut off the close paren
        upper_limit = float(limits_string[1][:-1])
        degrees_of_freedom[direction] = (lower_limit, upper_limit)
        # Other limit strings are in the format:
        # (lower_limit upper_limit)
        limits_string = next(lines).strip().split(" ")
    #pdb.set_trace()
    return degrees_of_freedom


def parse_asf_hierarchy(lines, bonedata):
    hierarchy = {}
    for line in lines:
        split_line = line.strip().split(" ")
        parent = split_line[0]
        children = split_line[1:]
        # Set children
        for child in children:
            bonedata[child].parent = bonedata[parent]
            bonedata[child].compute_rotation_from_parent()
            bonedata[child].siblings = [x for x in children if x != child]
        hierarchy[parent] = children
    return hierarchy


def main():
    file_name = sys.argv[1]
    #poses = parse_amc_file(file_name)
    asf_data = parse_asf_file(file_name)
    return 0

if __name__ == "__main__":
    main()