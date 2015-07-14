import pyAcclaim.Render
from pyAcclaim.ParseAMCFile import parse_amc_file
from pyAcclaim.ParseASFFile import parse_asf_file
from pyAcclaim.Setup import do_full_setup
from sys import argv
from pdb import set_trace

def main():
    ASF_file_name = argv[1]
    AMC_file_name = argv[2]
    data = parse_asf_file(ASF_file_name)
    root = data[4]
    bones = data[5]
    bonedata = data[6]
    hierarchy = data[7]
    poses = parse_amc_file(AMC_file_name)
    data = do_full_setup(root, bones, bonedata, poses, hierarchy)
    #set_trace()
    pyAcclaim.Render.render(data)

if __name__ == "__main__":
    main()