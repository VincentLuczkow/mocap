from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from .Bone import Bone
from pdb import set_trace
import numpy as np
from time import time
import sys


name = "Motion Capture"
# Time between poses in milliseconds
time_between_poses = 0
# Display properties
start_time = time()

# Pose data
bone_end_points = []
root_translations = []
parent_to_child_rotations = []
pose_rotations = []
direction_rotations = []
hierarchy = []

# Current values
current_pose = 0
current_bone = 0

ground_display_list = []


def draw_bone(index: int) -> int:
    global current_pose

    x_end, y_end, z_end = bone_end_points[index]
    glPushMatrix()
    # Rotate from the bone's local coordinate system to its parent's coordinate system.
    glMultMatrixd(parent_to_child_rotations[index])
    # Perform pose rotations. Order is XYZ, which means
    # the multiplications are Z * Y * X
    glRotated(pose_rotations[current_pose][index][2], 0.0, 0.0, 1.0)
    glRotated(pose_rotations[current_pose][index][1], 0.0, 1.0, 0.0)
    glRotated(pose_rotations[current_pose][index][0], 1.0, 0.0, 0.0)

    # Draw the bone
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(5)

    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(x_end, y_end, z_end)
    glEnd()

    # Translate to the end point of the bone.
    glTranslated(x_end, y_end, z_end)

    children = hierarchy[index]
    for child in children:
        draw_bone(child)
    glPopMatrix()
    return 0


def render_pose() -> int:
    global current_pose
    # Rotate to local coordinate system.
    glPushMatrix()
    # Root translation
    x_trans, y_trans, z_trans = root_translations[current_pose]
    glTranslated(x_trans, y_trans, z_trans)

    draw_bone(0)

    glPopMatrix()
    return 0


def display_bone():
    global current_pose
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    display_background()
    render_pose()
    glutSwapBuffers()
    current_pose += 1
    current_pose %= len(pose_rotations)


def do_nothing():
    return 0


def render(data):
    global bone_end_points, root_translations, parent_to_child_rotations, pose_rotations, hierarchy
    bone_end_points, root_translations, parent_to_child_rotations, pose_rotations, hierarchy = data

    init()
    glutMainLoop()
    return 0


def display_background():
    glLineWidth(2)
    glBegin(GL_LINES)
    # x axis in red
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(200, 0.0, 0.0)
    # y axis in green
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 200, 0.0)
    # z axis in blue
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 200)
    glEnd()

    glColor3f(0.1, 0.5, 0.1)
    glBegin(GL_QUADS)
    # bl
    glVertex3f(-500.0, 0.0, 500.0)
    # br
    glVertex3f(500.0, 0.0, 500.0)
    # tr
    glVertex3f(500.0, 0.0, -500.0)
    # tl
    glVertex3f(-500.0, 0.0, -500.0)
    glEnd()


def init():
    global ground_display_list

    glutInit()
    glutInitWindowSize(1000, 500)
    # The default color
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow("Motion Capture")
    glutDisplayFunc(display_bone)
    glutIdleFunc(display_bone)

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    # Field of view in degrees, aspect ratio, Z near, Z far
    gluPerspective(80.0, 2.0, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    # Three tuples:
    # Eye
    # Center
    # Up
    gluLookAt(45.0, 45.0, 45.0,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

    # Causes pixel colors to be interpolated based on colors at each vertex
    glShadeModel(GL_SMOOTH)
    # Enable face culling
    glEnable(GL_CULL_FACE)
    # Enable depth comparisons and update the depth buffer
    glEnable(GL_DEPTH_TEST)
