from pdb import set_trace
from pyAcclaim.Bone import Bone
from numpy import pi


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
def parse_asf_file(asf_file_name: str) -> tuple:
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
                root = Bone.create_root_bone(root[1], root[3], root[0])
                bonedata['root'] = root
                hierarchy = parse_asf_hierarchy(lines, bonedata)

                return version, name, units, documentation, root, bones, bonedata, hierarchy
    # This code is only reachable if :version never gets read.
    raise EOFError("File's not in the right format. :version was never parsed")


# Makes sure the next line in lines matches "header"
def check_header(header: str, lines) -> bool:
    header_line = next(lines)
    try:
        assert header_line.strip() == header
    except AssertionError:
        print("Parser went wrong somewhere. Header: " + header + " not properly parsed.")
        set_trace()
    return True


def parse_asf_version(line: str) -> str:
    try:
        version = line.strip().split()[1]
    except IndexError:
        print(":version line does not contain a version number.")
        set_trace()
    return version


def parse_asf_name(line: str) -> str:
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
    # Check if this bone has any rotational degrees of freedom
    dof_order, degrees_of_freedom = parse_degrees_of_freedom(lines)
    bone = Bone(index, name, direction, length, axis, axis_values, dof_order, degrees_of_freedom)
    return bone


def parse_degrees_of_freedom(lines):
    dof_line = next(lines).strip().split(" ")
    # If the bone has no degrees of freedom i.e. can't rotate
    if dof_line[0] != "dof":
        return [], {}
    degrees_of_freedom = {}
    dof_order = dof_line[1:]

    # The first limit string is in the format:
    # limits (lower_limit upper_limit)
    limit_string = next(lines).strip().split()[1:]
    for direction in dof_line[1:]:

        # The lower limit is in the format (float.
        # We cut off the open paren
        lower_limit = float(limit_string[0][1:])

        # The upper limit is in the format float).
        # We cut off the close paren
        upper_limit = float(limit_string[1][:-1])
        degrees_of_freedom[direction] = (lower_limit, upper_limit)

        # Other limit strings are in the format:
        # (lower_limit upper_limit)
        limit_string = next(lines).strip().split()
    return dof_order, degrees_of_freedom


def parse_asf_hierarchy(lines, bonedata):
    hierarchy = {}
    assert next(lines).strip() == "begin"
    for line in lines:
        if line.strip() == 'end':
            return hierarchy
        split_line = line.strip().split(" ")
        parent = split_line[0]
        children = split_line[1:]
        # Set children
        for child in children:
            bonedata[child].parent = bonedata[parent]
            bonedata[child].siblings = [x for x in children if x != child]
        hierarchy[parent] = children
    return hierarchy
