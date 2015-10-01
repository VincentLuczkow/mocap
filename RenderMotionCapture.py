import pyAcclaim.Render
from pyAcclaim.ParseAMCFile import parse_amc_file
from pyAcclaim.ParseASFFile import parse_asf_file
from pyAcclaim.MotionCapture import MotionCapture
from sys import argv
from pdb import set_trace

def main():
    asf_file_name = argv[1]
    amc_file_name = argv[2]
    data = parse_asf_file(asf_file_name)
    root = data[4]
    bones = data[5]
    bone_data = data[6]
    hierarchy = data[7]
    poses = parse_amc_file(amc_file_name)
    scene = MotionCapture(root, bones, bone_data, poses, hierarchy)
    scene.render()

if __name__ == "__main__":
    main()