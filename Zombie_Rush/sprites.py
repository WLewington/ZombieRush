import os, math, random
from random import uniform, choice
import pygame as pg
from settings import *
vec = pg.math.Vector2



def Collide(SP,GP,direc):

    def collide_hit_rect(x,y):
        return x.hit_rect.colliderect(y.rect)


    if direc == 'x':
        hit = pg.sprite.spritecollide(SP,GP, False,collide_hit_rect)
        if hit:
            if SP.vel.x > 0:
                SP.pos.x = hit[0].rect.left - SP.hit_rect.width/2
            if SP.vel.x < 0:
                SP.pos.x = hit[0].rect.right + SP.hit_rect.width/2


            SP.vel.x = 0
            SP.hit_rect.centerx = SP.pos.x
    if direc == 'y':
        hit = pg.sprite.spritecollide(SP,GP, False,collide_hit_rect)
        if hit:
            if SP.vel.y > 0:
                SP.pos.y = hit[0].rect.top - SP.hit_rect.height/2
            if SP.vel.y < 0:
                SP.pos.y = hit[0].rect.bottom + SP.hit_rect.height/2
            SP.vel.y = 0
            SP.hit_rect.centery = SP.pos.y

class Player(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = 3
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.player_still = pg.transform.scale\
            (game.player_still_img, (PLAYER_SIZE, PLAYER_SIZE))
        self.player_left = pg.transform.scale\
            (game.player_left_img, (PLAYER_SIZE, PLAYER_SIZE))
        self.player_right = pg.transform.scale\
            (game.player_right_img, (PLAYER_SIZE, PLAYER_SIZE))
        self.image = self.player_still
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.radius = 15
        #pg.draw.circle(self.image,RED,self.rect.center,self.radius,2)

        self.rect.center = (x, y)
        self.hit_rect = pg.Rect(0,0,40,40)
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.last_shot = 0
        self.degr = 0
        self.walk_frame = 0
        self.life=100
        self.bullet_lifetime = BULLET_LIFETIME
        self.ammo = 10

    def keysWASD_collision(self):
        self.vel = vec(0, 0)
        key = pg.key.get_pressed()
        if key[pg.K_a] and self.pos.x > self.radius:
            self.vel.x = -PLAYER_SPEED
        if key[pg.K_d] and self.pos.x+self.radius < SX:
            self.vel.x = PLAYER_SPEED
        if key[pg.K_w] and self.pos.y > self.radius:
            self.vel.y = -PLAYER_SPEED
        if key[pg.K_s] and self.pos.y+self.radius < SY:
            self.vel.y = PLAYER_SPEED
        # This is for maitaining the speed constant whe noving in a diagonal
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def bullet_spawning(self, degr):
        if pg.mouse.get_pressed()[0] == 1:
            # Shoot if we have ammo left
            if self.ammo > 0 :
                now = pg.time.get_ticks()
                if now - self.last_shot > BULLET_RATE:
                    self.last_shot = now
                    self.ammo -= 1
                    dir = vec(1, 0).rotate(-degr)
                    barrel = self.pos + vec(30, 0).rotate(-degr)
                    bullet(self.game, barrel, dir, self.bullet_lifetime)
                    self.game.shoot_sound.play()
            else :
                # No ammo, make a clicking sound
                self.game.click_sound.play()

    def P_Animation(self):
        # Are we standing still?
        if self.vel.x == 0 and self.vel.y == 0:
            self.walk_frame = 0
        else:
            # Do walking animation
            self.walk_frame += 1
            if self.walk_frame >= PLAYER_ANIMATIONSPEED:
                self.walk_frame = 0

        if self.walk_frame >= 1 and self.walk_frame <PLAYER_ANIMATIONSPEED/2:
            return self.player_left
        elif self.walk_frame > PLAYER_ANIMATIONSPEED/2:
            return self.player_right
        else:
            return self.player_still

    def rotate_p(self):
        self.mposX, self.mposY = pg.mouse.get_pos()
        self.mouse = vec(self.mposX, self.mposY)
        self.direct = vec(self.mouse - self.pos)
        self.degs = pg.math.Vector2.angle_to(self.direct, vec(0, 0))

    def update(self):

        if self.game.dead :
            self.image = self.game.player_dead_img
        else :
            self.rotate_p()
            self.keysWASD_collision()
            self.bullet_spawning(self.degs)
            self.pos.x += round(self.vel.x * self.game.dt)
            self.pos.y += round(self.vel.y * self.game.dt)
            self.hit_rect.centerx = self.pos.x
            Collide(self,self.game.backgroundwall,'x')
            self.hit_rect.centery = self.pos.y
            Collide(self,self.game.backgroundwall,'y')
            self.image_sate = self.P_Animation()
            self.image = pg.transform.rotate(self.image_sate, self.degs-90)

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.hit_rect.center

class Zombie(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = 3
        self.groups = game.all_sprites, game.zombies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.zombie_still = pg.transform.scale\
            (game.zombie_still_img, (ZOMBIE_SIZE, ZOMBIE_SIZE))


        self.image = self.zombie_still
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.radius = 15
        #pg.draw.circle(self.image,RED,self.rect.center,self.radius,2)

        self.hit_rect = pg.Rect(0,0,10,10).copy()
        self.hit_rect.center = self.rect.center

        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0

        self.speeds = zombie_slow_speed

        # True if we have seen player and are chasing them
        self.chasing = False
        # Where we are walking to, if we haven't see the player yet
        self.target = self.random_target()
        # Return a new position to head to

        self.dead = 1

    def random_target(self):
        return vec(random.randint(0, SX), random.randint(0, SY))

    def avoid_zombies(self):
        for zombie in self.game.zombies:
            if zombie != self:
                dist = self.pos - zombie.pos
                if 0 < dist.length() < avoid_radius:
                    self.acc += dist.normalize()

    def update(self):
        # Can we see the player? Start chasing them and make a noise
        dist_from_player = self.pos.distance_to(self.game.player.pos)
        if not self.chasing and dist_from_player < zombie_sight_range:
            self.chasing = True
            self.game.zombie_sound.play()

        # Chasing the player?
        if self.chasing:
            target = self.game.player.pos
            self.speed = choice(zombie_fast_speed) #zombie_speeds[random.randrange(0,4)][1]

        else:
            # Have we reached target? If so pick a new one
            dist_from_target = self.pos.distance_to(self.target)
            if dist_from_target < 30:
                self.target = self.random_target()
            target = self.target
            self.speed = zombie_slow_speed #zombie_speeds[random.randrange(0,4)][0]

        self.rot = (target - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.zombie_still, (self.rot - 90))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_zombies()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt**2

        self.hit_rect.centerx = self.pos.x
        Collide(self,self.game.backgroundwall,'x')
        self.hit_rect.centery = self.pos.y
        Collide(self,self.game.backgroundwall,'y')
        self.rect.center = self.hit_rect.center

        if self.dead == 0:
            self.kill()
            self.game.boom_sound.play()
            Dead_zombie(self.game,self.pos)

class Dead_zombie(pg.sprite.Sprite):
    def __init__(self,game,pos):
        self._layer = 2
        self.groups = game.all_sprites, game.deadzombies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.zombie_dead_img
        self.image = pg.transform.scale(self.game.zombie_dead_img,(42,52))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.rect.center = self.pos
        if pg.time.get_ticks() - self.spawn_time > 5000:
            self.kill()

class bullet(pg.sprite.Sprite):

    def __init__(self, game, pos, dir, lifetime):
        self._layer = 3
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()
        self.lifetime = lifetime

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
        if pg.sprite.spritecollideany(self,self.game.backgroundwall):
            self.kill()

class backgroundwall(pg.sprite.Sprite):

    def __init__(self,game,x,y):
        self._layer = 1
        self.groups = game.all_sprites, game.backgroundwall
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image  = pg.Surface((20,20))
        self.image.fill(GREEN)
        self.image.set_colorkey(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * 20
        self.rect.y = y * 20

class Pickup(pg.sprite.Sprite):

    def __init__(self, game):
        self.groups = game.all_sprites, game.pickups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # One in five chance we make a better gun, otherwise ammo
        if random.randint(1, 5) == 1 :
            self.type = "gun"
            self.image = game.gun_img
        else :
            self.type = "ammo"
            self.image = game.ammo_img

        self.rect = self.image.get_rect()

        self.pos = self.random_pos()
        self.rect.center = self.pos

        # Check that we're not on top of player or a wall, if we are, pick a new place
        while self.hit_player() or pg.sprite.spritecollideany(self,self.game.backgroundwall):
            self.pos = self.random_pos()
            self.rect.center = self.pos

        self.game.pickup_spawn_sound.play()
        self.spawn_time = pg.time.get_ticks()

    def hit_player(self):
        return self.rect.colliderect(self.game.player.hit_rect)

    def random_pos(self):
        return vec(random.randint(0, SX), random.randint(0, SY))

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > PICKUP_LIFETIME:
            self.kill()

        if self.rect.colliderect(self.game.player.hit_rect) :
            self.game.pickup_sound.play()
            if self.type == "ammo" :
                self.game.player.ammo += 10
            else :
                self.game.player.bullet_lifetime += 100

            self.kill()
