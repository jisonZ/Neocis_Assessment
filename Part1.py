# Import and initialize the pygame library
import pygame
import argparse
import numpy as np
from math import *

# color 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
ROTATE_SPEED = 0.02

# screen parameters
scale = 100
origin = [250, 250]
senstivity = 0.02

def runVisualizer(VertDic, SurfList):
    ProjMatrix = np.matrix([
        [1, 0 ,0],
        [0, 1, 0]
    ])

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

        # update vertex
        projDic = {}
        for key, val in VertDic.items():
            rotated2d = np.dot(rotationZ, val)
            rotated2d = np.dot(rotationY, rotated2d)
            rotated2d = np.dot(rotationX, rotated2d)
            VertDic[key] = rotated2d

            projected2d = np.dot(ProjMatrix, rotated2d)
            x = int(projected2d[0][0] * scale) + origin[0]
            y = int(-projected2d[1][0] * scale) + origin[1]
            pygame.draw.circle(screen, RED, (x, y), 5)            
            projDic[key] = [x, y]
        # break

        # update connected lines wo overlapping
        connected = set()
        for surf in SurfList:
            for v in range(len(surf)):
                if (surf[v], surf[(v+1)%len(surf)]) not in connected:
                    pygame.draw.line(screen, BLACK, projDic[surf[v]], projDic[surf[(v+1)%len(surf)]])
                    connected.add((surf[v], surf[(v+1)%len(surf)]))

        # Draw Origin
        pygame.draw.circle(screen, BLACK, (250, 250), 5)

        # Update screen
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
        VertDic = {}
        SurfList = []
        for i in range(numVert):
            line = f.readline().split(',')
            VertDic[int(line[0])] = np.matrix([[float(line[1])], [float(line[2])], [-float(line[3])]])
        
        for j in range(numSurf):
            line = f.readline().split(',')
            surf = []
            for i in line:
                surf.append(int(i))
            SurfList.append(surf)

    pygame.init()

    # Set up the drawing window
    pygame.display.set_caption("3D Visualizer")
    screen = pygame.display.set_mode([500, 500])

    # Run Visualization
    runVisualizer(VertDic, SurfList)

    # Done! Time to quit.
    pygame.quit()