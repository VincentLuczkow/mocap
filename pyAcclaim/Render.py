from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from .Bone import Bone
import numpy as np
from time import time
import sys


name = "Motion Capture"
# Time between poses in milliseconds
time_between_poses = 0
pose_list = []
current_pose_number = 0
current_pose = {}
root = None
bone_color = np.array([1.0, 50.0, 50.0, 1.0])
light_diffuse_values = np.array([[0.0, 0.0, 1.0, 1.0]])
light_ambient_values = np.array([[0.0, 0.0, 1.0, 1.0]])
light_positions = np.array([[1.0, 1.0, 1.0, 0.0]])
start_time = time()

# Renders a "bone" with length and direction in the local coordinate system
# For now this just renders a line. Later this will probably switch to an ellipsoid of some sort.
def render_single_bone(length, direction):
    print(length)
    print(direction)

    glPushMatrix()
    glLineWidth(5)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(5, 0, 0)
    glEnd()


# Renders bone at the origin of the local coordinate system. Then renders
# all of its descendents.
def display_bone_tree(bone: Bone):

    # Render the current bone
    render_single_bone(bone.length, bone.direction)
    #for child in bone.children:
        # Rotate to child's coordinate system
        #display_bone_tree(child)
        # Pop the rotation

    return 0


def display_root():
    global root, current_pose_number, current_pose
    display_bone_tree(root)
    current_pose_number += 1
    current_pose = pose_list[current_pose_number]
    return 0


def init():
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    for i in range(len(light_positions)):
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse_values[i])
        glLightfv(GL_LIGHT0, GL_POSITION, light_positions[i])
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    # Field of view in degrees, aspect ratio, Z near, Z far
    gluPerspective( 40.0, 1.0, 1.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    # Three tuples:
    # Eye
    # Center
    # Up
    gluLookAt(0.0, 0.0, 5.0,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

    # Causes pixel colors to be interpolated based on colors at each vertex
    glShadeModel(GL_SMOOTH)
    # Enable face culling
    glEnable(GL_CULL_FACE)


def draw_bone(length: float, pose: np.ndarray) -> int:
    glPushMatrix()
    glMultMatrixd(pose)

    glPopMatrix()
    return 0


def render_single_pose(pose: np.ndarray, root_translation: np.ndarray, parent_to_child_rotations: np.ndarray,
                       hierarchy: list) -> int:
    current_bone = 0
    return 0


def draw_line():
    glLineWidth(5)
    glBegin(GL_LINES)
    # draw x axis in red, y axis in green, z axis in blue

    glColor3f(1.0, 0.2, 0.2)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(20, 0.0, 0.0)

    glColor3f(0.2, 1.0, 0.2)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 20, 0.0)

    glColor3f(0.2, 0.2, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 20)

    glEnd()
    time_passed = time() - start_time
    glPushMatrix()
    glRotate(180.0 - time_passed*5, 0.0, 0.0, 1.0)
    glLineWidth(5)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(5, 0, 0)
    glEnd()
    glPopMatrix()


def display():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_line()
    glutSwapBuffers()


def render():
    glutInit()
    glutInitWindowSize(1000, 500)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow("Red 3D Lighted Cube")
    glutDisplayFunc(display)
    glutIdleFunc(display)
    init()
    glutMainLoop()
    return 0


# Create the basic scene
def scene_init():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)

    # Set initial window size
    glutInitWindowSize(1000, 1000)
    # Creates a window whose name is name
    glutCreateWindow(name)
    # The default color
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Causes pixel colors to be interpolated based on colors at each vertex
    glShadeModel(GL_SMOOTH)
    # Enable face culling
    glEnable(GL_CULL_FACE)
    # Enable depth comparisons and update the depth buffer
    glEnable(GL_DEPTH_TEST)

    return 0


# Set up lighting
def lighting():
    glEnable(GL_LIGHTING)

    # Set light zero position
    glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 4.0, 10.0, 1.0])
    # Set light zero diffuse color
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.25, 1.25, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.25, 0.25, 0.25, 1.0])
    # Set light zero attenuation
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)

    # Enable light zero
    glEnable(GL_LIGHT0)
    return 0


def render_motion_capture(root_bone: Bone, poses: list) -> int:
    global pose_list, current_pose, root
    # Do basic scene initialization
    scene_init()
    # Do scene lighting
    lighting()

    pose_list = poses
    current_pose = pose_list[0]
    root = root_bone

    # Set scene display function
    glutDisplayFunc(display_root)
    # Called over and over again
    #glutIdleFunc(display_root)
    glMatrixMode(GL_PROJECTION)
    # Sets up projection matrix
    gluPerspective(80.0, 1.0, 1.0, 80.0)
    glMatrixMode(GL_MODELVIEW)
    # Look from first three coordinates towards second three with orientation last three.
    gluLookAt(0, 0, 10,
              0, 0, 0,
              0, 1, 0)
    glPushMatrix()

    # Display everything
    glutMainLoop()

    return 0
