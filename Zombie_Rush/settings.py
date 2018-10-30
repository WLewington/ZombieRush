#game variables
SX = 960
SY = 720
FPS = 60
FONT_NAME = 'arial'
title = "Zombie Rush"

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# ---Player Stats
PLAYER_SPEED = 200
PLAYER_SIZE = 53
PLAYER_ANIMATIONSPEED = 12

# ---Bullets Stats
BULLET_SPEED = 700
BULLET_LIFETIME = 250
BULLET_RATE = 300

# ---Zombie Stats
avoid_radius = 35

zombie_slow_speed = 70
zombie_fast_speed = [250,200,300,150,250,350,250]
zombie_sight_range = 300  # How far away a zombie can see the player

ZOMBIE_SIZE = 30

# How long a pickup should be shown for
PICKUP_LIFETIME = 5000

# How many frames to wait before new pickup
PICKUP_DELAY = 500

# If player has this much ammo or less then immediately show a pickup
# to give them some chance
LOW_PLAYER_AMMO = 3

# Time to wait before player can restart after dying
PLAYER_RESTART_DELAY = 2000
