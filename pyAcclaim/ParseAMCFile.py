from re import match

# Assumes AMC file is in the following format:
# comments
# ...
# :Specification level
# :Angle type
# 1
# pose1
# 2
# pose2
# ...
# n
# posen
def parse_amc_file(file_name: str) -> list:
    poses = []
    with open(file_name, "r") as pose_file:
        lines = iter(pose_file.readlines())
        # Read past header data
        line = next(lines).strip()
        while not match(r':.*', line):
            line = next(lines).strip()
        specification_level = line
        angle_type = next(lines).strip()
        # Read pose numbering
        line = next(lines).strip()
        assert line == "1"
        for line in lines:
            poses.append(parse_pose(line, lines, angle_type))
    return poses

# Assumes pose is in the following format:
# root root_data
# bone1 bone1_data
# ...
# lastbone lastbone_data
def parse_pose(first_line: str, lines, angle_type: str):
    values = parse_single_bone_pose(first_line, angle_type)
    for line in lines:
        if match(r'\d+', line.strip()):
            break
        else:
            values.update(parse_single_bone_pose(line, angle_type))
    return values


# Assumes a line is in the following format:
# bonename dof1 dof2 ... dofn
# where each dof was defined for bonename in the
# ASF file corresponding to this AMC file.
def parse_single_bone_pose(line, angle_type: str):
    split_line = line.strip().split()
    name = split_line[0]
    # TODO
    if angle_type == "DEGREES":
        pass
    else:
        pass
    values = [float(x) for x in split_line[1:]]
    return {name : values}