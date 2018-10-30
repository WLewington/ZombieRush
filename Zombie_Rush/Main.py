# Zombie Rush
import random
import pygame as pg
from os import path
from settings import *
from sprites import *



class Game:

    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode((SX, SY))
        pg.mouse.set_visible(False)

        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.load_data()
        self.running = True
        self.dt = 0
        self.font_name = pg.font.match_font(FONT_NAME)

    def load_data(self):

        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, "Imgs")
        map_folder = path.join(game_folder, "map")
        sound_folder = path.join(game_folder, "sound")

        # --- SCREENS
        # When paused we dim the screen
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0,0,0,180))
        # Red screen (when Player is hit or dead)
        self.red_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.red_screen.fill((255,0,0,180))

        # --- SPRITES ---
        # Player
        self.player_still_img = pg.image.load(os.path.join(img_folder, "soldier_still.png")).convert()
        self.player_left_img = pg.image.load(os.path.join(img_folder, "soldier_left.png")).convert()
        self.player_right_img = pg.image.load(os.path.join(img_folder, "soldier_right.png")).convert()
        self.player_dead_img= pg.image.load(os.path.join(img_folder, "dead_soldier.png")).convert()
        # Bullets
        self.bullet_img = pg.image.load(os.path.join(img_folder, "bullet.png")).convert()
        # Zombies
        self.zombie_still_img = pg.image.load(os.path.join(img_folder, "zombie_still.png")).convert()
        self.zombie_dead_img = pg.image.load(os.path.join(img_folder, "dead_zombie.png")).convert()
        # Mouse
        self.mouse_pointer_img = pg.image.load(os.path.join(img_folder, "gun-point.png")).convert()
        # Pickups
        self.gun_img = pg.image.load(os.path.join(img_folder, "gun.png")).convert()
        self.ammo_img = pg.image.load(os.path.join(img_folder, "ammo.png")).convert()
        # Map
        self.background_img = pg.image.load(os.path.join(map_folder, "background.png")).convert()
        self.map_data = []

        # Load level
        with open(path.join(map_folder,"bit_map.txt"),'rt') as f:
            for line in f:
                self.map_data.append(line)

        # Start screen
        self.start_screen = pg.image.load(os.path.join(img_folder, "start_screen.png")).convert()

        # Game over screen
        self.game_over_screen = pg.image.load(os.path.join(img_folder, "game_over_screen.png")).convert()

        # Sounds
        self.shoot_sound = pg.mixer.Sound(os.path.join(sound_folder, "shoot.wav"))
        self.click_sound = pg.mixer.Sound(os.path.join(sound_folder, "click.wav"))
        self.boom_sound = pg.mixer.Sound(os.path.join(sound_folder, "boom.wav"))
        self.pickup_sound = pg.mixer.Sound(os.path.join(sound_folder, "pickup.wav"))
        self.pickup_spawn_sound = pg.mixer.Sound(os.path.join(sound_folder, "pickup_spawn.wav"))
        self.zombie_sound = pg.mixer.Sound(os.path.join(sound_folder, "zombie.wav"))

        # Background music
        pg.mixer.music.load(os.path.join(sound_folder, "music.ogg"))
        pg.mixer.music.play(-1)

    def zombie_spawning(self, zombie_count):
       for i in range(zombie_count):
           spawning_quarants = [[random.randrange(-SX//8, 0), random.randrange((-SY//8), SY)],
                               [random.randrange(0, (9*SX//8)), random.randrange((-SY//8), 0)],
                               [random.randrange(SX, 9*SX//8), random.randrange(0, 9*SY//8)],
                               [random.randrange(-SX//8, SX), random.randrange(SY, 9*SY//8)]]
           zones = choice(spawning_quarants)
           z = Zombie(self, zones[0], zones[1])
           self.all_sprites.add(z)
           self.zombies.add(z)

    def pickup_spawn(self):
        pickup = Pickup(self)
        self.all_sprites.add(pickup)
        self.pickups.add(pickup)

    # Setup a new game
    def new(self):
        self.wave = 1
        self.kill_count = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.backgroundwall = pg.sprite.Group()
        self.deadzombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.pickups = pg.sprite.Group()

        self.player = Player(self, 200+SX//2, SY//2)

        self.zombie_spawning(1)

        for Row, tiles in enumerate(self.map_data):
            for Col, tile in enumerate(tiles):
                if tile == '1':
                    backgroundwall(self,Col,Row)

        # Is game paused?
        self.paused = False

        # Is player dead? If so we show end screen and ask them to restart
        self.dead = False

        # Time the player died. Used to stop us from starting a new game
        # until a short time has passed
        self.dead_time = 0

        # If a player has been dead long enough (see self.dead_time) set
        # this to True
        self.can_restart = False

        # Is the player currently being hit
        self.hit = False

        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            # dt stand for delta time and by multiplying the value to the speed of movement
            # the velocity stays the same no matter the frame rate
            self.dt = self.clock.tick(FPS)/1000.0
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def update(self):

        if len(self.zombies) == 0:
            self.wave +=1
            self.zombie_spawning(self.wave)

        # Out of pickups?
        # Add a new pickup randomly, unless the player has low ammo then always show one
        if not self.dead and len(self.pickups) == 0 \
            and (random.randint(1, PICKUP_DELAY) == 1 or self.player.ammo < LOW_PLAYER_AMMO):
            self.pickup_spawn()

        # Killing a zombie
        hits = pg.sprite.groupcollide(self.zombies, self.bullets, False, True,pg.sprite.collide_circle)
        for hit in hits:
            self.kill_count += 1
            hit.dead -= 1

        # Killing the player
        self.hit = False
        hits = pg.sprite.spritecollide(self.player, self.zombies, False,pg.sprite.collide_circle)
        for hit in hits:
            self.player.life -= 1
            self.hit = True
            if self.player.life <= 0 and not self.dead:
                self.dead = True
                self.dead_time = pg.time.get_ticks()

        self.all_sprites.update()

    def events(self):

        if self.dead and pg.time.get_ticks() - self.dead_time > PLAYER_RESTART_DELAY :
            self.can_restart = True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if self.dead and self.can_restart and \
                (event.type == pg.KEYUP or pg.mouse.get_pressed()[0] == 1):
                    self.new()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_ESCAPE:
                    pg.quit()

    def draw(self):
        pg.display.set_caption(title+" (Fps {:.2f})".format(self.clock.get_fps()))
        self.screen.blit(pg.transform.scale(self.background_img, (960, 720)),(0,0))

        self.all_sprites.draw(self.screen)
        if not self.dead and self.paused:
            self.screen.blit(self.dim_screen,(0,0))
            self.draw_text("PAUSED", 30, RED, SX/2, SY/2)

        if self.hit or self.dead:
            self.screen.blit(self.red_screen,(0,0))

        if self.dead:
            self.game_over_screen.set_colorkey(BLACK)
            self.screen.blit(self.game_over_screen, (0, 0))

            if self.can_restart :
                self.draw_text("<< Press any key or click to try again >>", 20, WHITE, SX / 2, SY / 2)

        self.draw_text("WAVE NUMBER " + str(self.wave)+"     "+\
            str(self.kill_count) + " KILLS"+"     "+\
            str(self.player.ammo) + " BULLETS" \
            , 20, WHITE, SX/2, SY-60)

        self.Cursor_img()

        self.lifebar(40,SY-50,self.player.life)
        pg.display.flip()

    def lifebar(self,x,y,health):
        if health < 0:
            health =0
        fill = health
        outline_rect = pg.Rect(x,y,100,15)
        fill_rect = pg.Rect(x,y,fill,15)
        pg.draw.rect(self.screen,RED,fill_rect)
        pg.draw.rect(self.screen,WHITE,outline_rect,2)

    def Cursor_img(self):
        self.mouse_pointer_img.set_colorkey(BLACK)
        self.screen.blit(self.mouse_pointer_img,(self.player.mposX-15,self.player.mposY-15))

    def show_start_screen(self):
        self.screen.blit(self.start_screen, (0, 0))
        self.draw_text("A - move left | W - move up | D - move right | S - move down", 25, WHITE, SX / 2, SY *3/4)
        self.draw_text("Use mouse to aim and shoot. Don't run out of ammo!", 25, WHITE, SX / 2, SY *3/4+40)
        self.draw_text("<< Press any key or click to start >>", 20, WHITE, SX / 2, SY * 3/4+100)
        pg.display.flip()
        self.wait_for_start()

    def wait_for_start(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP or pg.mouse.get_pressed()[0] == 1:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

g = Game()
g.show_start_screen()
while g.running:

    g.new()

pg.quit()
