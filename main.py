# packages
import pygame
import sys
import math
import os

# center window on creation
os.environ['SDL_VIDEO_CENTERED'] = '1'

# global constants
SCREEN_HEIGHT = int(480 + (480 / 2))
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 30
TILE_SIZE = int((SCREEN_WIDTH / 2) / MAP_SIZE)
MAX_DEPTH = int(MAP_SIZE * TILE_SIZE)
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS
SCALE = (SCREEN_WIDTH / 2) / CASTED_RAYS
BLINDFOLD = pygame.image.load('/home/pi/Desktop/Raze/blndfld.png')
HANDS = pygame.image.load('/home/pi/Desktop/Raze/hands.png')
HANDS_Y = 0
HANDS_CHANGE = 2
HANDS_MOVEMENT = False
CAST_RAYS = False

# global variables
player_x = (SCREEN_WIDTH / 2) / 2
player_y = (SCREEN_WIDTH / 2) / 2
player_angle = math.pi
cheats = False
down = False

# map
MAP = (
    '##############################'
    '#     #    #                 #'
    '#     #    ############      #'
    '#   ###               #   ####'
    '#   #      #   ########      #'
    '#   #   ####                 #'
    '#       #    ##   ########   #'
    '#   #   ###              #   #'
    '#   #     #######  #######   #'
    '##########       ##         ##'
    '#             ###      #     #'
    '#######    ###    ######   ###'
    '#           #          #     #'
    '#  ########## #####    #######'
    '#  #        #     #      #   #'
    '#  #   ###  #     #      #   #'
    '#  #   # #  # #   #          #'
    '#  #   # #  # #   ############'
    '#  #   #      #              #'
    '#  #   #######################'
    '#  #                         #'
    '#  #  ########################'
    '#  #    # #         #  #  #  #'
    '#  #  ### #  ###  ###  #  #  #'
    '#  #         #            #  #'
    '#  #      ####    #########  #'
    '#  # ####             #      #'
    '#  #      #########   ####   #'
    '#  # ####                    #'
    '##############################'
)

# init pygame
pygame.init()

# create game window
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
icon = pygame.image.load('/home/pi/Desktop/Raze/icon.png')
pygame.display.set_icon(icon)

# set window title
pygame.display.set_caption('Raze')

# init timer
clock = pygame.time.Clock()

# draw map
def draw_map():
    # loop over map rows
    for row in range(MAP_SIZE):
        # loop over map columns
        for col in range(MAP_SIZE):
            # calculate square index
            square = row * MAP_SIZE + col
            
            # draw map in the game window
            pygame.draw.rect(
                win,
                (12, 72, 12) if MAP[square] == '#' else (100, 100, 100),
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            )

    # draw player on 2D board
    pygame.draw.circle(win, (135,89,50), (int(player_x), int(player_y)), 8)

# raycasting algorithm
def cast_rays():
    # define left most angle of FOV
    start_angle = player_angle - HALF_FOV
    
    # loop over casted rays
    for ray in range(CASTED_RAYS):
        # cast ray step by step
        for depth in range(MAX_DEPTH):
            # get ray target coordinates
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth
            
            # covert target X, Y coordinate to map col, row
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)
            
            # calculate map square index
            square = row * MAP_SIZE + col

            # ray hits the condition
            if MAP[square] == '#':
                if CAST_RAYS == True:
                    # highlight wall that has been hit by a casted ray
                    pygame.draw.rect(win, (6, 48, 23), (col * TILE_SIZE,
                                                    row * TILE_SIZE,
                                                    TILE_SIZE,
                                                    TILE_SIZE))
                elif CAST_RAYS == False:
                    pass     

                # draw casted ray
                if CAST_RAYS == True:
                    pygame.draw.line(win, (255, 255, 0), (player_x, player_y), (target_x, target_y))
                elif CAST_RAYS == False:
                    pass        

                # wall shading
                color = 255 / (1 + depth * depth * 0.0002)
                
                # fix fish eye effect
                depth *= math.cos(player_angle - start_angle)
                                
                # calculate wall height
                wall_height = 21000 / (depth + 0.0001)
                
                # fix stuck at the wall
                if wall_height > SCREEN_HEIGHT: wall_height = SCREEN_HEIGHT 
                
                # draw 3D projection (rectangle by rectangle...)
                pygame.draw.rect(win, (0, color, 0), (
                    SCREEN_HEIGHT + ray * SCALE,
                    (SCREEN_HEIGHT / 2) - wall_height / 2,
                     SCALE, wall_height))
                
                break

        # increment angle by a single step
        start_angle += STEP_ANGLE

# moving direction
forward = True

# game loop
while True:
    # escape condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d or pygame.K_w or event.key == pygame.K_s:
                HANDS_MOVEMENT = False
    
    # covert target X, Y coordinate to map col, row
    col = int(player_x / TILE_SIZE)
    row = int(player_y / TILE_SIZE)
           
    # calculate map square index
    square = row * MAP_SIZE + col

    # player hits the wall (collision detection)
    if MAP[square] == '#':
        if forward:
            player_x -= -math.sin(player_angle) * 5
            player_y -= math.cos(player_angle) * 5
        else:
            player_x += -math.sin(player_angle) * 5
            player_y += math.cos(player_angle) * 5
    
    # update 2D background
    pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
    
    # update 3D background
    pygame.draw.rect(win, (100, 100, 100), (SCREEN_HEIGHT, SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))
    pygame.draw.rect(win, (100, 100, 255), (SCREEN_HEIGHT, -SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))
    
    # draw 2D map
    # apply raycasting
    cast_rays()

    # get user input
    keys = pygame.key.get_pressed()
    
    # handle user input
    if keys[pygame.K_a]:
        player_angle -= 0.1
    if keys[pygame.K_d]:
        player_angle += 0.1
    if keys[pygame.K_w]:
        HANDS_MOVEMENT = True
        forward = True
        player_x += -math.sin(player_angle) * 5
        player_y += math.cos(player_angle) * 5
    if keys[pygame.K_s]:
        HANDS_MOVEMENT = True
        forward = False
        player_x -= -math.sin(player_angle) * 5
        player_y -= math.cos(player_angle) * 5
    if keys[pygame.K_F1]:
        cheats = True
    if keys[pygame.K_F2]:
        cheats = False
    if keys[pygame.K_F3]:
        CAST_RAYS = True
    if keys[pygame.K_F4]:
        CAST_RAYS = False

    # set FPS
    clock.tick(24)

    # display FPS
    fps = str(int(clock.get_fps()))
    
    # pick up the font
    font = pygame.font.SysFont('Monospace Regular', 30)
    
    # create font surface
    fps_surface = font.render(fps, False, (255, 255, 255))
    
    # print FPS to screen
    win.blit(fps_surface, (480, 0))


    # set map blindfold
    if cheats == False:
        win.blit(BLINDFOLD, (0, 0))
        text = 'This is a maze'
        textUnder = 'activate map to help guid you (This map can get confusing)'
        textUnderThat = 'F1 to activate F2 to diactivate'
        textUnderTT = 'NOTE: It wont tell you where the goal is cheeky'
        message = font.render(text, False, (255, 255, 255))
        messageUnder = font.render(textUnder, False, (255, 255, 255))
        messageUnderThat = font.render(textUnderThat, False, (255, 255, 255))
        messageUnderTT = font.render(textUnderTT, False, (255, 255, 255))
        win.blit(message, (290, 282))
        win.blit(messageUnder, (100, 300))
        win.blit(messageUnderThat, (230, 300 + (250 - 232)))
        win.blit(messageUnderTT, (160, 300 + (280 - 232)))
    elif cheats == True:
        draw_map()

    # hands movement
    if HANDS_MOVEMENT == True:
        if down == False:
            HANDS_Y += HANDS_CHANGE
        if HANDS_Y == 10:
            down = True
        if down == True:
            HANDS_Y -= HANDS_CHANGE
        if HANDS_Y == -10:
            down = False
    elif HANDS_MOVEMENT == False:
        pass
    win.blit(HANDS, (720, HANDS_Y + 12))

    # update display
    pygame.display.flip()