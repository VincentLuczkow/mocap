import pdb
from sys import argv
from pyAcclaim import ParseASFFile
from pyAcclaim import ParseAMCFile
from pyAcclaim import Render


# Feel free to overwrite this test data with data from another file. Just make sure what you use to overwrite
# is accurate.
actual_version = '1.10'
actual_name = 'TEST'
actual_units = (1.0, 0.45, 'deg')
actual_documentation = 'Test documentation.\nThis file contains 30 bones.\n'
actual_root = (['TX', 'TY', 'TZ', 'RX', 'RY', 'RZ'], 'XYZ', [0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
actual_bones = ['root', 'lhipjoint', 'lfemur', 'ltibia', 'lfoot', 'ltoes', 'rhipjoint', 'rfemur', 'rtibia', 'rfoot', 'rtoes', 'lowerback', 'upperback', 'thorax', 'lowerneck', 'upperneck', 'head', 'lclavicle', 'lhumerus', 'lradius', 'lwrist', 'lhand', 'lfingers', 'lthumb', 'rclavicle', 'rhumerus', 'rradius', 'rwrist', 'rhand', 'rfingers', 'rthumb']
actual_hierarchy = {'upperback': ['thorax'], 'rfoot': ['rtoes'], 'lradius': ['lwrist'], 'rradius': ['rwrist'], 'lwrist': ['lhand', 'lthumb'], 'rhand': ['rfingers'], 'rhumerus': ['rradius'], 'lowerneck': ['upperneck'], 'lhand': ['lfingers'], 'end': [], 'ltibia': ['lfoot'], 'rwrist': ['rhand', 'rthumb'], 'lowerback': ['upperback'], 'lhipjoint': ['lfemur'], 'rhipjoint': ['rfemur'], 'lclavicle': ['lhumerus'], 'upperneck': ['head'], 'rfemur': ['rtibia'], 'thorax': ['lowerneck', 'lclavicle', 'rclavicle'], 'rclavicle': ['rhumerus'], 'rtibia': ['rfoot'], 'lfoot': ['ltoes'], 'lhumerus': ['lradius'], 'root': ['lhipjoint', 'rhipjoint', 'lowerback'], 'lfemur': ['ltibia']}


def check_bones(bones, bonedata):
    # Check that all bones exist
    for bone in bones:
        if bone not in bonedata:
            raise Exception("Bone: " + bone + " not properly parsed.")
    return None


def test_asf_parser():
    test_asf_file_name = "test.asf"
    # Run test
    version, name, units, documentation, root, bones, bonedata, hierarchy = ParseASFFile.parse_asf_file(test_asf_file_name)
    try:
        assert version == actual_version
    except AssertionError:
        pdb.set_trace()
    try:
        assert name == actual_name
    except AssertionError:
        pdb.set_trace()
    try:
        assert units == actual_units
    except AssertionError:
        pdb.set_trace()
    try:
        assert documentation == actual_documentation
    except AssertionError:
        pdb.set_trace()
    try:
        assert root == actual_root
    except AssertionError:
        pdb.set_trace()
    try:
        assert bones == actual_bones
    except AssertionError:
        pdb.set_trace()
    try:
        assert hierarchy == actual_hierarchy
    except AssertionError:
        pdb.set_trace()
    return True


def test_amc_parser():

    return True



def main():
    if argv[1] == "testasf":
        test_asf_parser()
    elif argv[1] == "testamc":
        test_amc_parser()
    else:
        asf_file_name = argv[1]
        data = ParseASFFile.parse_asf_file(asf_file_name)
        bone_data = data[6]
        root = bone_data['root']
        amc_file_name = argv[2]
        poses = ParseAMCFile.parse_amc_file(amc_file_name)
        Render.render_motion_capture(root, poses)


if __name__ == "__main__":
    main()