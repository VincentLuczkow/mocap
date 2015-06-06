import ReadFile
import pdb

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
    version, name, units, documentation, root, bones, bonedata, hierarchy = ReadFile.parse_asf_file(test_asf_file_name)
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

def main():

    return None


class ParsingError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        repr(self.message)


if __name__ == "__main__":
    main()