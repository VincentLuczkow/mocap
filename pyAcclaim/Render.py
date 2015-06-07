from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from .Bone import Bone
import sys


name = "Motion Capture"


# Renders a "bone" with length and direction in the local coordinate system
# For now this just renders a line. Later this will probably switch to an ellipsoid of some sort.
def render_single_bone(length, direction):

    return 0


# Renders bone at the origin of the local coordinate system. Then renders
# all of its descendents.
def render_bone_tree(bone: Bone):
    # Render the current bone
    render_single_bone(bone.length, bone.direction)
    for child in bone.children:
        # Rotate to child's coordinate system
        render_bone_tree(child)
        # Pop the rotation
    return 0


# Create the basic scene
def scene_init():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

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


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    color = [1.0, 0.0, 0.0, 1.0]
    glMaterialfv(GL_FRONT, GL_DIFFUSE,color)
    glutSolidSphere(2,20,20)
    glPopMatrix()
    glutSwapBuffers()
    return 0


def main():
    # Do basic scene initialization
    scene_init()
    # Do scene lighting
    lighting()

    # Set scene display function
    glutDisplayFunc(display)
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

if __name__ == '__main__':
    main()