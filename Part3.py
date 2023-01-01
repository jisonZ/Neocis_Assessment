# Simple pygame program

# Import and initialize the pygame library
import pygame
import argparse
import numpy as np
from math import *
from numpy import linalg as LA

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
ROTATE_SPEED = 0.02
LIGHT_BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 37)

scale = 100
origin = [250, 250]
grid = [500, 500]
senstivity = 0.02
VertDic = {}
Frame = []
SurfList = []
projDic = {}
ProjMatrix = np.matrix([
    [1, 0 ,0],
    [0, 1, 0]
])

def getcolor(vertex):
    # cross product of two vectors
    vec1 = VertDic[vertex[1]] - VertDic[vertex[0]]
    vec2 = VertDic[vertex[2]] - VertDic[vertex[1]]
    perpVec = np.cross(vec1.reshape(1,3), vec2.reshape(1,3))
    cosVal = np.dot(perpVec, np.array([0,0,1]))/LA.norm(perpVec)
    cosVal = np.arccos(cosVal)
    # clamp angle to (0, pi/2)
    if cosVal > pi/2:
        cosVal = pi-cosVal

    return (0,0, LIGHT_BLUE[2]-(LIGHT_BLUE[2]-DARK_BLUE[2])*cosVal/(pi/2))

def visualizeShade():
    # Z-buffer
    # iterate through y values
    zBuf = [[-inf for x in range(grid[0])] for y in range(grid[1])]
    # screenBuf = [[WHITE for x in range(grid[0])] for y in range(grid[1])]
    # iterate each rpojected polygon
    for surf in SurfList:
        # find max and min y
        vertList = []
        for v in surf:
            vertList.append(projDic[v])
        vertList = sorted(vertList, key=lambda x: x[1], reverse=True)
        v_1 = vertList[0]
        v_2 = vertList[1]
        v_3 = vertList[2]

        if v_1[1] == v_2[1]:
            v_1, v_3 = v_3, v_1

        # print("new points")
        # print(v_1)
        # print(v_2)
        # print(v_3)
        # scan through (min y, max y) using scan line
        # print(f"ys range: {min(v_3[1], v_1[1])} to {max(v_3[1], v_1[1])}")
        for ys in range(min(v_3[1], v_1[1]), max(v_3[1], v_1[1])):
            z_a = v_1[2] - (v_1[2]-v_2[2])*((v_1[1]-ys)/(v_1[1]-v_2[1]))
            z_b = v_1[2] - (v_1[2]-v_3[2])*((v_1[1]-ys)/(v_1[1]-v_3[1]))
            # calcualte x_a and x_b
            if int(v_1[0]-v_2[0]) != 0:
                slop_a = (v_1[1]-v_2[1])/(v_1[0]-v_2[0])
                intcpt_a = v_1[1]-slop_a*v_1[0]
                x_a = int((ys-intcpt_a)/slop_a)
            else:
                x_a = int(v_1[0])
            
            if int(v_1[0]-v_3[0]) != 0:
                slop_b = (v_1[1]-v_3[1])/(v_1[0]-v_3[0])
                intcpt_b = v_1[1]-slop_b*v_1[0]
                x_b = int((ys-intcpt_b)/slop_b)
            else:
                x_b = int(v_1[0])

            # print(f"xp range: {x_a} to {x_b}")
            for xp in range(x_a, x_b):
                z_p = z_b-(z_b-z_a)*((x_b-xp)/(x_b-x_a))
                # print(f"draw ({xp}, {ys})")
                if (z_p > zBuf[xp][int(ys)]):
                    zBuf[xp][int(ys)] = z_p
                    pygame.draw.line(screen, getcolor(surf), (xp, ys), (xp, ys))
    
def genRotationMtx(zAngle, yAngle, xAngle):
    # define rotation matrix
    rotationZ = np.matrix([
        [cos(zAngle), -sin(zAngle), 0],
        [sin(zAngle), cos(zAngle), 0],
        [0, 0, 1],
    ])

    rotationY = np.matrix([
        [cos(yAngle), 0, sin(yAngle)],
        [0, 1, 0],
        [-sin(yAngle), 0, cos(yAngle)],
    ])

    rotationX = np.matrix([
        [1, 0, 0],
        [0, cos(xAngle), -sin(xAngle)],
        [0, sin(xAngle), cos(xAngle)],
    ])
    return rotationZ, rotationY, rotationX

# def visualizeFrame(zAngle, yAngle, xAngle):
#     rotationZ, rotationY, rotationX = genRotationMtx(zAngle, yAngle, xAngle)
#     color = [RED, GREEN, BLUE]
#     for i in range(3):
#         rotated2d = np.dot(rotationZ, Frame[i])
#         rotated2d = np.dot(rotationY, rotated2d)
#         rotated2d = np.dot(rotationX, rotated2d)
#         projected2d = np.dot(ProjMatrix, rotated2d)

def visualizeEdges():
    global projDic
    projDic = {}
    for key, val in VertDic.items():
        rotated2d = val
        projected2d = np.dot(ProjMatrix, rotated2d)
        x = int(projected2d[0][0] * scale) + origin[0]
        y = int(-projected2d[1][0] * scale) + origin[1]
        pygame.draw.circle(screen, RED, (x, y), 5)

        projDic[key] = [x, y, rotated2d[2][0]]
    # update connected lines wo overlapping
    connected = set()
    for surf in SurfList:
        for v in range(len(surf)):
            if (surf[v], surf[(v+1)%len(surf)]) not in connected:
                pygame.draw.line(screen, BLACK, projDic[surf[v]][0:2], projDic[surf[(v+1)%len(surf)]][0:2])
                connected.add((surf[v], surf[(v+1)%len(surf)]))

def PreprocessLocation(zAngle, yAngle, xAngle):
    rotationZ, rotationY, rotationX = genRotationMtx(zAngle, yAngle, xAngle)

    # update vertex
    for key, val in VertDic.items():
        rotated2d = np.dot(rotationZ, val)
        rotated2d = np.dot(rotationY, rotated2d)
        rotated2d = np.dot(rotationX, rotated2d)
        VertDic[key] = rotated2d

def runVisualizer():
    # Run until the user asks to quit
    running = True
    rotating = False
    initRotating = False
    while running:
        xAngle = 0
        yAngle = 0
        zAngle = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:            
                    rotating = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    rotating = False
                    initRotating = False

            elif event.type == pygame.MOUSEMOTION:
                if rotating:
                    rel = pygame.mouse.get_rel()
                    if not initRotating:
                        initRotating = True
                    else:
                        yAngle = -rel[0]*senstivity
                        xAngle = -rel[1]*senstivity
                    
            # if event.type == pygame.KEYDOWN:
            # if a key is pressed for rotation
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                xAngle = yAngle = zAngle = 0
            if keys[pygame.K_a]:
                yAngle = ROTATE_SPEED
            if keys[pygame.K_d]:
                yAngle = -ROTATE_SPEED      
            if keys[pygame.K_w]:
                xAngle = ROTATE_SPEED
            if keys[pygame.K_s]:
                xAngle = -ROTATE_SPEED
            if keys[pygame.K_q]:
                zAngle = -ROTATE_SPEED
            if keys[pygame.K_e]:
                zAngle = ROTATE_SPEED
            
        # Fill the background with white
        screen.fill(WHITE)
        PreprocessLocation(zAngle, yAngle, xAngle)
        # visualizeFrame(zAngle, yAngle, xAngle)
        visualizeEdges()
        visualizeShade()

        pygame.display.update()

if __name__ == '__main__':
    # parse coordinate file
    parser = argparse.ArgumentParser(description='Process Coordinates')
    parser.add_argument('fname', type=str, help='A filename that include the coordinate information')
    args = parser.parse_args()

    with open(args.fname, encoding='utf-8') as f:
        firstline = f.readline().split(',')
        numVert = int(firstline[0])
        numSurf = int(firstline[1])

        for i in range(numVert):
            line = f.readline().split(',')
            VertDic[int(line[0])] = np.matrix([[float(line[1])], [float(line[2])], [-float(line[3])]])
        
        for j in range(numSurf):
            line = f.readline().split(',')
            surf = []
            for i in line:
                surf.append(int(i))
            SurfList.append(surf)

    Frame.append(np.matrix([[1], [0], [0]]))
    Frame.append(np.matrix([[0], [1], [0]]))
    Frame.append(np.matrix([[0], [0], [1]]))

    pygame.init()

    # Set up the drawing window
    pygame.display.set_caption("3D Visualizer")
    screen = pygame.display.set_mode(grid)

    # Run Visualization
    runVisualizer()

    # Done! Time to quit.
    pygame.quit()