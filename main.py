"""
    FLAPPY BIRD
    Remake of the classic game, optimized as a
    port for Miyoo Mini & Miyoo Mini Plus (OnionOS)

    Forked from:
    https://github.com/bbhitec/flappy_pygame

    Changes made by:
    https://github.com/rbrower28

    Changes:
    - reformat for MM aspect ratio
    - conversion to python2 compatibility

    Up Next:
    - Alternate day and night background
    - Alternate bird color
    - Alternate pipe color
"""

import pygame
from sys import exit
import random

############ CONST
DISPLAY_WIDTH  = 640
DISPLAY_HEIGHT = 480
FPS = 60
SCORE_X = DISPLAY_WIDTH - 80
SCORE_Y = 60

FLOOR_HEIGHT = 420
FLOOR_SPEED = 1
GRAVITY_COEFF = 0.35    # acceleration from gravity
BIRD_START_X = 100
BIRD_START_Y = DISPLAY_HEIGHT/2
BIRD_START_SPEED = -10
BIRD_ROTATION_COEFF = 3 # bird surface rotation sensitivity
BIRD_FLAP_POWER = 7     # bird flap strength. decrease to make game easier
BIRD_FLAP_FREQ = 300    # flap animation speed
BIRD_DISPLAY_TOLERANCE = 100
PIPE_START_X = DISPLAY_WIDTH + 200
PIPE_HEIGHTS = [240, 280, 320, 360]
PIPE_MARGIN = 180   # space between the pipes
PIPE_SPEED = 4
PIPE_FREQ = 1100    # pipes spawning frequency (in ms)

SPAWNPIPE_EVT = pygame.USEREVENT
BIRD_FLAP_EVT = pygame.USEREVENT + 1

############ global vars
gravity = GRAVITY_COEFF
bird_speed = BIRD_START_SPEED
game_active = False # indicate a un-halted game
game_score = 0
high_score = 0

# to make a continuous floor, we make two floor surfaces move together
def draw_floor():
    screen.blit(floor_surface, (floor_x,FLOOR_HEIGHT))
    screen.blit(floor_surface, (floor_x+DISPLAY_WIDTH,FLOOR_HEIGHT))

# different bird frames are kept as a list
# and changed via a timed event
def bird_animation():
    global bird_flap_index
    bird_flap_index = (bird_flap_index + 1) % 3 # repeat frames
    new_bird_surface = bird_flaps[bird_flap_index]
    new_bird_rect = new_bird_surface.get_rect(center = (BIRD_START_X, bird_rect.centery))
    return new_bird_surface, new_bird_rect

def rotate_bird(bird_surface):
    global bird_speed
    rotation_angle = -bird_speed * BIRD_ROTATION_COEFF
    new_surface = pygame.transform.rotozoom(bird_surface,rotation_angle,1)
    return new_surface

def draw_bird(bird_rotated):
    screen.blit(bird_rotated, bird_rect)

def move_pipes(pipe_rect_list_a):
    for pipe_rect in pipe_rect_list_a:
        pipe_rect.centerx -= PIPE_SPEED
    return pipe_rect_list_a

def draw_pipes(pipe_rect_list_a):
    global pipe_surface
    for pipe_rect in pipe_rect_list_a:
        if pipe_rect.top < 0:
            pipe_surface_l = pygame.transform.flip(pipe_surface, False, True)
        else:
            pipe_surface_l = pipe_surface
        screen.blit(pipe_surface_l, pipe_rect)

def create_pipe():
    global pipe_surface
    pipe_height = random.choice(PIPE_HEIGHTS)
    pipe_surface = random.choice(pipe_surfaces)
    bottom_pipe = pipe_surface.get_rect(midtop = (PIPE_START_X, pipe_height))
    upper_pipe = pipe_surface.get_rect(midbottom = (PIPE_START_X, pipe_height - PIPE_MARGIN))
    return bottom_pipe, upper_pipe

# check bird-pipe collision
def check_collisions(pipe_rect_list_a):
    if bird_rect.top <= -BIRD_DISPLAY_TOLERANCE or bird_rect.bottom >= FLOOR_HEIGHT:
        die_sound.play()
        return False
    for pipe in pipe_rect_list_a:
        if bird_rect.colliderect(pipe):
            collision_sound.play()
            return False
    return True

# render score as text and draw as a surface
def draw_score():
    global game_font
    global game_score
    score_surface = game_font.render(str(game_score), False, [255, 255, 255]) # white
    score_rect = score_surface.get_rect(center = (SCORE_X, SCORE_Y))
    screen.blit(score_surface, score_rect)

def draw_highscore():
    global game_font
    global high_score
    highscore_surface = game_font.render(str(high_score), False, [241, 241, 129]) # gold
    highscore_rect = highscore_surface.get_rect(center = (80, SCORE_Y))
    screen.blit(highscore_surface, highscore_rect)

# renewing the game
def reset_game():
    global bird_speed
    bird_speed = BIRD_START_SPEED

    global game_score
    game_score = 0

    global pipe_rect_list
    bird_rect.center = (BIRD_START_X, BIRD_START_Y)
    pipe_rect_list = []

    global game_active
    game_active = True

def update_highscore():
    global game_score
    global high_score
    if (game_score > high_score):
        high_score = game_score

def exit_app():
    pygame.quit()
    exit()

############ PYGAME
pygame.mixer.pre_init(44100, -16, 2, 512) # audio presets
pygame.init()
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Flappy Bird")
pygame.font.init()
game_font = pygame.font.Font('assets/04B_19.TTF', 50) # src & size
clock = pygame.time.Clock()

############ ASSETS
bg_surface = pygame.transform.scale(pygame.image.load('assets/background-day.png').convert(), (DISPLAY_WIDTH, DISPLAY_HEIGHT*2))
floor_surface = pygame.transform.scale(pygame.image.load('assets/base.png').convert(), (672, 140))
floor_x = 0

# bird animation
bird_flaps = [pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap.png').convert_alpha()),
              pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha()),
              pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap.png').convert_alpha())]
bird_flap_index = 0
bird_surface =  bird_flaps[bird_flap_index]
bird_rect = bird_surface.get_rect(center = (BIRD_START_X, BIRD_START_Y))
pygame.time.set_timer(BIRD_FLAP_EVT, BIRD_FLAP_FREQ)

# the pipe textures
pipe_surfaces = [pygame.transform.scale(pygame.image.load('assets/pipe-red.png').convert(), (70, 340)),
                pygame.transform.scale(pygame.image.load('assets/pipe-green.png').convert(), (70, 340,))]
pipe_rect_list = []
pygame.time.set_timer(SPAWNPIPE_EVT, PIPE_FREQ)

# greeting/game over surface
greeting_surface = pygame.transform.scale(pygame.image.load('assets/message.png').convert_alpha(), (260, 380))
greeting_rect = greeting_surface.get_rect(center = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT*0.45))

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
game_score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
die_sound = pygame.mixer.Sound('sound/sfx_die.wav')
collision_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
swooshing_sound = pygame.mixer.Sound('sound/sfx_swooshing.wav')

def action():
    global bird_speed
    global game_active
    if game_active:
        bird_speed = 0
        bird_speed -= BIRD_FLAP_POWER
        flap_sound.play()
    else:
        reset_game()

def main():
    global game_active
    global pipe_rect_list
    global floor_x
    global bird_speed
    global game_score
    global gravity
    global bird_rect

    ############ main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:   # A btn (Miyoo Mini)
                    action()
                if event.key == pygame.K_ESCAPE:    # Menu btn (Miyoo Mini)
                    exit_app()
            if event.type == SPAWNPIPE_EVT:
                pipe_rect_list.extend(create_pipe())
            if event.type == BIRD_FLAP_EVT:
                bird_surface, bird_rect = bird_animation()

        screen.blit(bg_surface, (0,-(DISPLAY_HEIGHT*2/3)))

        if (game_active):
            # update bird
            bird_speed += gravity
            bird_rect.centery += bird_speed
            bird_rotated = rotate_bird(bird_surface)
            draw_bird(bird_rotated)

            game_active = check_collisions(pipe_rect_list)

            # update pipes
            pipe_rect_list = move_pipes(pipe_rect_list)
            draw_pipes(pipe_rect_list)

            game_score +=1
        else:
            update_highscore()
            draw_highscore()
            screen.blit(greeting_surface, greeting_rect)

        draw_score()

        # floor movements
        floor_x -= FLOOR_SPEED
        if (floor_x <= -DISPLAY_WIDTH):
            floor_x = 0
        draw_floor()

        # end frame
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()