#! /usr/bin/env python
import OpenGL
OpenGL.USE_ACCELERATOR = True
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import random
import time
import sys



# *********************** Globals ***********************
# Python 2.2 defines these directly

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0


# // User Defined Variables

# // General Loops (Used For Seeking)
mx = 0
my = 0
done = False												# // Flag To Let Us Know When It's Done

width = 128												# // Maze Width  (Must Be A Power Of 2)
height = 128												# // Maze Height (Must Be A Power Of 2)

tex_data = None													# numarray of unsigned bytes - # // Holds Our RGB Texture Data

quadric = None													# // The Quadric Object

xrot = 0
yrot = 0
zrot = 0														# // Use For Rotation Of Objects


def update_tex(dmx, dmy):
	""" // Update Pixel dmx, dmy On The Texture """
	global tex_data

	tex_data[0 + ((dmx + (width * dmy)) * 3)] = 255					# // Set Red Pixel To Full Bright
	tex_data[1 + ((dmx + (width * dmy)) * 3)] = 255					# // Set Green Pixel To Full Bright
	tex_data[2 + ((dmx + (width * dmy)) * 3)] = 255					# // Set Blue Pixel To Full Bright
	return


def reset():
	""" // Reset The Maze, Colors, Start Point, Etc	"""
	global tex_data, mx, my

	# ZeroMemory(tex_data, width * height *3);							// Clear Out The Texture Memory With 0's
	# This creates or array of unsigned bytes for our texture data. All values initialized to 0
	# tex_data = numarray.zeros ((width * height * 3), type="u1")
	tex_data = np.zeros((width * height * 3), "b")

	# This Will seed the random num stream with current system time.
	random.seed()

	mx = random.randint (0, (width/2) - 1) * 2								# // Pick A New Random X Position
	my = random.randint (0, (height/2) - 1) * 2								# // Pick A New Random Y Position
	return


# // Any GL Init Code & User Initialiazation Goes Here
def init_gl(Height, Width):				# We call this right after our OpenGL window is created.
	global tex_data, width, height, quadric

	reset ()							# // Call Reset To Build Our Initial Texture, Etc.

	glEnable(GL_TEXTURE_2D)								# // Enable Texture Mapping
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, tex_data.tostring())

	glClearColor(0.0, 0.0, 0.0, 0.0)						# // Black Background
	glClearDepth(1.0)								# // Depth Buffer Setup
	glDepthFunc(GL_LEQUAL)								# // The Type Of Depth Testing
	glEnable(GL_DEPTH_TEST)							# // Enable Depth Testing

	glEnable(GL_COLOR_MATERIAL)							# // Enable Color Material (Allows Us To Tint Textures)

	quadric = gluNewQuadric()								# // Create A Pointer To The Quadric Object
	gluQuadricNormals(quadric, GLU_SMOOTH)					# // Create Smooth Normals
	gluQuadricTexture(quadric, GL_TRUE)					# // Create Texture Coords

	glEnable(GL_LIGHT0)									# // Enable Light0 (Default GL Light)

	return True											# // Return TRUE (Initialization Successful)


def update_scene():
	""" Solves/builds the maze. """
	global width, height, done, mx, my

	done = True														# // Set done To True
	for x in xrange (0, width, 2):										# // Loop Through All The Rooms
		for y in xrange (0, height, 2):									# // On X And Y Axis
			if tex_data[((x + (width * y)) * 3)] == 0:						# // If Current Texture Pixel (Room) Is Blank
				done = False											# // We Have To Set done To False (Not Finished Yet)

	if done:															# // If done Is True Then There Were No Unvisited Rooms
		# // Display A Message At The Top Of The Window, Pause For A Bit And Then Start Building A New Maze!
		glutSetWindowTitle("Capture")
		time.sleep(5)
		glutSetWindowTitle("Capture")
		reset()

	direction = random.randint(0,3)									# // Pick A Random Direction

	if (direction == 0) and (mx <= (width - 4)):									# // If The Direction Is 0 (Right) And We Are Not At The Far Right
		if tex_data[(((mx + 2) + (width * my)) * 3)] == 0:						# // And If The Room To The Right Has Not Already Been Visited
			update_tex(mx + 1, my)										# // Update The Texture To Show Path Cut Out Between Rooms
			mx += 2														# // Move To The Right (Room To The Right)

	if (direction == 1) and (my <= (height-4)):									# // If The Direction Is 1 (Down) And We Are Not At The Bottom
		if tex_data[((mx + (width * (my + 2))) * 3)] == 0:						# // And If The Room Below Has Not Already Been Visited
			update_tex(mx, my + 1)										# // Update The Texture To Show Path Cut Out Between Rooms
			my += 2													# // Move Down (Room Below)

	if (direction == 2) and (mx >= 2):											# // If The Direction Is 2 (Left) And We Are Not At The Far Left
		if tex_data[(((mx - 2) + (width * my)) * 3)] == 0:						# // And If The Room To The Left Has Not Already Been Visited
			update_tex(mx - 1, my)										# // Update The Texture To Show Path Cut Out Between Rooms
			mx -= 2														# // Move To The Left (Room To The Left)

	if (direction == 3) and (my >= 2):											# // If The Direction Is 3 (Up) And We Are Not At The Top
		if tex_data[((mx + (width * (my - 2))) * 3)] == 0:						# // And If The Room Above Has Not Already Been Visited
			update_tex(mx, my-1)										# // Update The Texture To Show Path Cut Out Between Rooms
			my -= 2													# // Move Up (Room Above)

	update_tex(mx, my)												# // Update Current Room

	glBegin(GL_TRIANGLES)
	glVertex2i(100, 100)
	glVertex2i(150, 100)
	glVertex2i(125, 50)
	glEnd( )

	return

def draw_gl_scene():
	""" // Our Drawing Routine """
	global xrot, yrot, zrot
	global width, height, tex_data
	global quadric

	update_scene()

	# // Get Window Dimensions
	window_width = glutGet(GLUT_WINDOW_WIDTH)
	window_height = glutGet(GLUT_WINDOW_HEIGHT)

	# // Update Our Texture... This Is The Key To The Programs Speed... Much Faster Than Rebuilding The Texture Each Time
	glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, tex_data.tostring())

	glClear(GL_COLOR_BUFFER_BIT)										# // Clear Screen

	glColor3ub(27, 157, 255)						# // Assign Color To Current View

	# // Set The Viewport To The Top Left.  It Will Take Up Half The Screen Width And Height
	glViewport(0, 0, window_width, window_height)
	glMatrixMode(GL_PROJECTION)								# // Select The Projection Matrix
	glLoadIdentity()														# // Reset The Projection Matrix
	# // Set Up Ortho Mode To Fit 1/4 The Screen (Size Of A Viewport)
	gluOrtho2D(0, window_width, window_height, 0)

	glMatrixMode(GL_MODELVIEW)								# // Select The Modelview Matrix
	glLoadIdentity()								# // Reset The Modelview Matrix

	glClear(GL_DEPTH_BUFFER_BIT)							# // Clear Depth Buffer

	glBegin(GL_QUADS)								# // Begin Drawing A Single Quad

	# // We Fill The Entire 1/4 Section With A Single Textured Quad.
	glTexCoord2f(1.0, 0.0)
	glVertex2i(window_width/2, 0)
	glTexCoord2f(0.0, 0.0)
	glVertex2i(0, 0)
	glTexCoord2f(0.0, 1.0)
	glVertex2i(0, window_height/2)
	glTexCoord2f(1.0, 1.0)
	glVertex2i(window_width/2, window_height/2)

	glEnd()												# // Done Drawing The Textured Quad

	glColor3ub(27, 157, 255)

	glBegin(GL_LINES)

	glVertex2i(window_width/2, window_height/2)
	glVertex2i(window_width/2 + 10, window_height/2 + 10)

	glEnd()

	glBegin(GL_TRIANGLES)
	glVertex2i(100, 100)
	glVertex2i(150, 100)
	glVertex2i(125, 50)
	glEnd( )

	glutSwapBuffers()													# // Flush The GL Rendering Pipeline
	return True


# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def resize_gl_scene(new_width, new_height):
	if new_height == 0:						# Prevent A Divide By Zero If The Window Is Too Small
		new_height = 1

	glViewport(0, 0, new_width, new_height)		# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	# // field of view, aspect ratio, near and far
	# This will squash and stretch our objects as the window is resized.
	gluPerspective(45.0, float(new_width)/float(new_height), 0.1, 100.0)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()


# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def key_pressed(*args):
	global window

	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit ()
	# // Check To See If Spacebar Is Pressed
	if args[0] == ' ':
		reset()													# // If So, Call Reset And Start A New Maze

	return


def main():
	global window
	# pass arguments to init
	glutInit(sys.argv)

	# Select type of Display mode:
	#  Double buffer
	#  RGBA color
	# Alpha components supported
	# Depth buffer
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)

	glutInitWindowSize(1024, 768)

	# the window starts at the upper left corner of the screen
	glutInitWindowPosition(0, 0)

	# Okay, like the C version we retain the window id to use when closing, but for those of you new
	# to Python, remember this assignment would make the variable local and not global
	# if it weren't for the global declaration at the start of main.
	window = glutCreateWindow("Capture");

	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invoke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.
	glutDisplayFunc(draw_gl_scene)

	# Uncomment this line to get full screen.
	#glutFullScreen()

	# When we are doing nothing, redraw the scene.
	glutIdleFunc(draw_gl_scene)

	# Register the function called when our window is resized.
	glutReshapeFunc(resize_gl_scene)

	# Register the function called when the keyboard is pressed.
	# The call setup glutSpecialFunc () is needed to receive
	# "keyboard function or directional keys."
	glutKeyboardFunc(key_pressed)
	glutSpecialFunc(key_pressed)

	# We've told Glut the type of window we want, and we've told glut about
	# various functions that we want invoked (idle, resizing, keyboard events).
	# Glut has done the hard work of building up thw windows DC context and
	# tying in a rendering context, so we are ready to start making immediate mode
	# GL calls.
	# Call to perform inital GL setup (the clear colors, enabling modes, and most releveant -
	# consturct the displays lists for the bitmap font.
	init_gl(640, 480)

	# Start Event Processing Engine
	glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
if __name__ == "__main__":
	print "Hit ESC key to quit."
	main()