import pygame
from pygame.math import Vector2


pygame.init()
screen = pygame.display.set_mode((1150, 800))
clock = pygame.time.Clock()
# Images.
BG_IMG = pygame.Surface((1150, 800))
BG_IMG.fill((30, 120, 30))
BLUECAR_ORIGINAL = pygame.Surface((50, 30), pygame.SRCALPHA)
pygame.draw.polygon(
    BLUECAR_ORIGINAL, (0, 0, 255), [(0, 30), (50, 20), (50, 10), (0, 0)])
bluecar = BLUECAR_ORIGINAL
REDCAR_ORIGINAL = pygame.Surface((50, 30), pygame.SRCALPHA)
pygame.draw.polygon(
    REDCAR_ORIGINAL, (255, 0, 0), [(0, 0), (50, 10), (50, 20), (0, 30)])
redcar = REDCAR_ORIGINAL

BALL = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(BALL, [250,250,250], [15, 15], 15)
# Ball variables.
ball_pos = Vector2(575, 400)
ballrect = BALL.get_rect(center=ball_pos)
ball_vel = Vector2(0, 0)
# Car variables.
pos_red = Vector2(470, 370)
vel_red = Vector2(3, 0)
redrect = redcar.get_rect(center=pos_red)
redangle = 0
pos_blue = Vector2(70,70)
vel_blue = Vector2(3,0)
bluerect = bluecar.get_rect(center=pos_red)
blueangle = 0
# Masks.
mask_blue = pygame.mask.from_surface(bluecar)
mask_red = pygame.mask.from_surface(redcar)
mask_ball = pygame.mask.from_surface(BALL)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        redangle += 5
        vel_red.rotate_ip(-5)
        redcar = pygame.transform.rotate(REDCAR_ORIGINAL, redangle)
        redrect = redcar.get_rect(center=redrect.center)
        # We need a new mask after the rotation.
        mask_red = pygame.mask.from_surface(redcar)
    elif keys[pygame.K_RIGHT]:
        redangle -= 5
        vel_red.rotate_ip(5)
        redcar = pygame.transform.rotate(REDCAR_ORIGINAL, redangle)
        redrect = redcar.get_rect(center=redrect.center)
        mask_red = pygame.mask.from_surface(redcar)

    if keys[pygame.K_a]:
        blueangle += 5
        vel_blue.rotate_ip(-5)
        bluecar = pygame.transform.rotate(BLUECAR_ORIGINAL, blueangle)
        bluerect = bluecar.get_rect(center=bluerect.center)
        mask_blue = pygame.mask.from_surface(bluecar)
    elif keys[pygame.K_d]:
        blueangle -= 5
        vel_blue.rotate_ip(5)
        bluecar = pygame.transform.rotate(BLUECAR_ORIGINAL, blueangle)
        bluerect = bluecar.get_rect(center=bluerect.center)
        mask_blue = pygame.mask.from_surface(bluecar)

    # Move the cars.
    pos_red += vel_red
    redrect.center = pos_red
    pos_blue += vel_blue
    bluerect.center = pos_blue
    # Move the ball.
    ball_vel *= .99  # Friction.
    ball_pos += ball_vel
    ballrect.center = ball_pos

    # Red car collision.
    # We need the offset between the redrect and the ballrect.
    offset_red = redrect[0] - ballrect[0], redrect[1] - ballrect[1]
    # Pass the offset to the `overlap` method. If the masks collide,
    # overlap will return a single point, otherwise `None`.
    overlap_red = mask_ball.overlap(mask_red, offset_red)
    # Blue car collision.
    offset_blue = bluerect[0] - ballrect[0], bluerect[1] - ballrect[1]
    overlap_blue = mask_ball.overlap(mask_blue, offset_blue)

    if overlap_red and overlap_blue:  # Both collide with the ball.
        # Not sure what should happen here.
        ball_vel = vel_red + vel_blue * 1.4
    elif overlap_red:  # Red collides with the ball.
        ball_vel = Vector2(vel_red) * 1.4
    elif overlap_blue:  # Blue collides with the ball.
        ball_vel = Vector2(vel_blue) * 1.4

    # Drawing.
    screen.blit(BG_IMG, (0, 0))
    screen.blit(BALL, ballrect)
    screen.blit(redcar, redrect)
    screen.blit(bluecar, bluerect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()