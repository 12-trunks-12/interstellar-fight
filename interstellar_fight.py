#====================================
#     ---------IMPORTS---------
#====================================
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
import random
import time
#====================================
#    ---------CONSTANTS---------
#====================================
WIDTH_SCREEN = 1000
HEIGHT_SCREEN = 800
FPS = 60
DISPLAYSURF = pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))

#====================================
#  --------FUNCTIONS/CLASSES--------
#====================================

#==================FUNCTIONS
def update_stars(surface, layer, speed):
    for coordinate in layer:
        coordinate[1] += speed
        if coordinate[1] >= HEIGHT_SCREEN:
            coordinate[1] = 1
        pixel = pygame.PixelArray(surface)
        pixel[coordinate[0]][coordinate[1]] = pygame.Color(250, 250, 250)
        del pixel


def update_shoots(surface, group, objetive, shield, movement, damage):
    for shoot in group:
        shoot.rect.y += movement
        collision = pygame.sprite.spritecollide(objetive, group, True)
        if collision != [] and shield == False:
            group.remove(shoot)
            objetive.life -= damage
            objetive.image = pygame.image.load("Graphics/Ships/"+objetive.name+"_damage.png")
            if objetive.life < 0:
                objetive.life = 0
        elif shoot.rect.y <= 0 or shoot.rect.y >= HEIGHT_SCREEN:
            group.remove(shoot)
        else:
            surface.blit(shoot.image, (shoot.rect.x, shoot.rect.y))


def create_bar(surface, pos_x_bar, size_bar, pos_x_stuffed, size_stuffed, pos_y, size_y, color_stuffed, text, all_text, size_text, color_text):
    bar = pygame.gfxdraw.rectangle(surface, (pos_x_bar, pos_y, size_bar, size_y), (255, 255, 255, 255))
    stuffed = pygame.gfxdraw.box(surface, (pos_x_stuffed, pos_y, size_stuffed, size_y), color_stuffed)
    text = size_text.render(text+all_text, True, color_text)
    text.convert_alpha()
    return bar,stuffed,text


#==================CLASSES
class Ship(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name  # For change the name more easily
        self.image = pygame.image.load("Graphics/Ships/" + name + ".png")
        self.rect = self.image.get_rect()

        self.movement = None
        self.speed = 10
        self.life = 200

        self.counter_attack_laser = 0  # Control the frecuency of the shoots
        self.counter_attack_missiles = 0  # Control the frecuency of the missiles

    def update_movement(self):
        if self.movement == 'right' and self.rect.x < WIDTH_SCREEN-self.image.get_rect()[2]:
            self.rect.x += self.speed
        elif self.movement == 'left' and self.rect.x > 0:
            self.rect.x -= self.speed

    def control_frecuency_shoots(self):  # If counter_attack = 0 you can shoot, else it go diminishing till be 0 (when you can shoot)
        #Lasers
        if self.counter_attack_laser > 0:
            self.counter_attack_laser -= 1

        #Missiles
        if self.counter_attack_missiles > 0:
            self.counter_attack_missiles -= 1

    def shoot(self, type_laser, group_shoots):
        if type_laser != "missiles.png":
            group_shoots.add(Laser(type_laser, self.rect.x))

        elif type_laser == "missile.png":
            group_shoots.add(Laser(type_laser, self.rect.x))




class Laser(pygame.sprite.Sprite):
    def __init__(self, type, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Graphics/Lasers/" + type)
        self.rect = self.image.get_rect()

        if type not in ("missile.png", "boss_laser.png"):
            self.rect.x, self.rect.y = (x+22, HEIGHT_SCREEN-104)
        elif type == "missile.png":
            self.rect.x, self.rect.y = (x, HEIGHT_SCREEN-154)
        elif type == "boss_laser.png":
            self.rect.x, self.rect.y = (x+100, 154)


#====================================
#      ----------BODY----------
#====================================
#------------------Initialize
pygame.mixer.pre_init(22050, -16, 10, 4096)
pygame.init()
pygame.display.set_caption("Interstellar Fight")
pygame.mouse.set_visible(False)
fpsClock = pygame.time.Clock()

#------------------Background
#___Space image
space = pygame.image.load("Graphics/Background/space_scroll.png")

#___Stars
stars_layer3 = []
for i in range(200):
    stars_layer3.append([random.randrange(1, WIDTH_SCREEN-1), random.randrange(1, HEIGHT_SCREEN-1)])

stars_layer2 = []
for i in range(300):
    stars_layer2.append([random.randrange(1, WIDTH_SCREEN-1), random.randrange(1, HEIGHT_SCREEN-1)])

stars_layer1 = []
for i in range(100):
    stars_layer1.append([random.randrange(1, WIDTH_SCREEN-1), random.randrange(1, HEIGHT_SCREEN-1)])

#------------------Ships
#___Boss
boss = Ship("boss_sprite")
boss.rect.x= (WIDTH_SCREEN-boss.image.get_rect()[2])//2
boss.movement = "left"
boss.speed = 5
boss.life = 1000

boss_laser = "boss_laser.png"
list_shoots_boss = pygame.sprite.Group()

#___Player
player = Ship("ship_sprite")
player.rect.x = (WIDTH_SCREEN-player.image.get_rect()[2])/2
player.rect.y = HEIGHT_SCREEN-player.image.get_rect()[3]-10

normal_laser = "normal_laser.png"
special_laser = "elite_laser.png"
missile = "missile.png"

list_normal_shoots_player = pygame.sprite.Group()
list_special_shoots_player = pygame.sprite.Group()
list_missiles_player = pygame.sprite.Group()

#------------------Music
music = pygame.mixer.music
music.load("Music/music_war.mp3")
music.set_volume(0.5)
music.play(-1)

sound_laser = pygame.mixer.Sound("Music/shoot_laser.wav")
sound_laser.set_volume(1)
sound_laser_boss = pygame.mixer.Sound("Music/shoot_laser_boss.wav")
sound_laser.set_volume(0.05)

sound_missile = pygame.mixer.Sound("Music/shoot_missile.wav")
sound_missile.set_volume(1)

#------------------Font
font_big = pygame.font.Font("04b_30.TTF", int(HEIGHT_SCREEN/30))
font_small = pygame.font.Font("04b_30.TTF", int(HEIGHT_SCREEN/50))
font_time = pygame.font.Font("TravelingTypewriter.TTF", 15)

#------------------Counters/Conditions
#___Menu
counter_menu = False

#___Scroll background (+2, +4...)
counter_scroll = 0

#___Movement of the boss (change direction if counter > 15)
counter_boss_movement = 0

#___Shoots of the player ship
counter_damage = 0  # If the boss hit you

counter_normal_laser_ammunition = 250   # Maximum of lasers ammunition

counter_super_mode = 400  # Maximum of special lasers ammunition
super_mode = False   # If True lasers are more strong

counter_missile_ammunition = 5    # Maximum of missiles ammunition
attack_missile = False  # If true you attack with ONE missile

attack_laser = False  # True if K_SPACE is activated (to shoot)
recharge_normal_laser = False   # False if player is attacking, True if player isn't attacking an counter laser < 100
recharge_super_mode = False

#___End of the game
counter_end = False  # If you win is True, if you died is False
counter_time_start = time.time()  # Control the time of the game
counter_time_pause = 0

#====================================
#     -----------LOOP-----------
#====================================
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        #__Player action (movement, attack)
        key_pressed = pygame.key.get_pressed()  # Because if K_LEFT or K_RIGHT is actived K_SPACE not work

        if event.type == KEYDOWN:
            #-Menu
            if event.key == K_q:
                if counter_menu == False:
                    counter_menu = True
                else:
                    counter_menu = False
                    pygame.mixer.music.unpause()
                break

            #--Movement
            if event.key == K_RIGHT:
                player.movement = "right"
            elif event.key == K_LEFT:
                player.movement = "left"

            #--Attack
            if event.key == K_a and counter_super_mode == 400:  # Special laser
                super_mode = True
                player.life += 50
                if player.life > 200:
                    player.life = 200
                player.speed = 13

            elif event.key == K_s and counter_missile_ammunition >= 1 and player.counter_attack_missiles == 0:  # Missiles
                attack_missile = True

        elif event.type == KEYUP:
            #--Stop movement
            if event.key == K_RIGHT and key_pressed[K_LEFT]:
                player.movement = "left"
            elif event.key == K_LEFT and key_pressed[K_RIGHT]:
                player.movement = "right"
            elif not key_pressed[K_LEFT] and not key_pressed[K_RIGHT]:
                player.movement = None

            #--Stop attack
            if event.key == K_SPACE:
                attack_laser = False
                if counter_normal_laser_ammunition < 250:
                    recharge_normal_laser = True


    if counter_menu == True:  # Active the menu
        pygame.mixer.music.pause()
        menu_image = pygame.image.load("Graphics/menu.png")
        DISPLAYSURF.blit(menu_image, (0, 0))

    elif counter_menu == False and player.life > 0 and boss.life > 0:
        #___Images of the ships
        #Player
        if super_mode == True:
            counter_super_mode -= 1
            player.image = pygame.image.load("Graphics/Ships/ship_sprite_SM.png")
            if counter_super_mode <= 0:
                super_mode = False
                recharge_super_mode = True
        else:
            player.image = pygame.image.load("Graphics/Ships/ship_sprite.png")
            player.speed = 10

        #Boss
        boss.image = pygame.image.load("Graphics/Ships/boss_sprite.png")

        #___Player actions (movement, recharge, frecueny...)
        key_pressed = pygame.key.get_pressed()

        #-Movement
        player.update_movement()

        #Frecuency
        player.control_frecuency_shoots()

        #-Attack, recharge and control of the attack frecuency
        if key_pressed[K_SPACE] == True:
            attack_laser = True

        #Attack missiles
        if attack_missile == True and player.counter_attack_missiles == 0:  # Shoot missiles
            player.counter_attack_missiles = 30 # Time to can shoot other time
            counter_missile_ammunition -= 1
            player.shoot(missile, list_missiles_player)
            sound_laser.stop()  # For the sound missile sound
            sound_missile.play()
            attack_missile = False

        #Attack laser
        if attack_laser == True and (recharge_normal_laser == False or recharge_super_mode == False) and player.counter_attack_laser == 0: # Shoot special lasers
            if super_mode == True:
                if counter_normal_laser_ammunition < 250:
                    recharge_normal_laser = True
                else:
                    recharge_normal_laser = False
                player.counter_attack_laser = 5  # Time to can shoot other time
                player.shoot(special_laser, list_special_shoots_player)
                sound_laser.play()

            elif counter_normal_laser_ammunition >= 0 and recharge_normal_laser == False:  # Shoot normal lasers
                counter_normal_laser_ammunition -= 1.5
                player.counter_attack_laser = 5 # Time to can shoot other time
                player.shoot(normal_laser, list_normal_shoots_player)
                sound_laser.play()
                if counter_normal_laser_ammunition <= 0:
                    attack_laser = False
                    recharge_normal_laser = True

        #Recharge normal laser
        if recharge_normal_laser == True and counter_normal_laser_ammunition < 250:
            counter_normal_laser_ammunition += 1
            if key_pressed[K_SPACE] and counter_normal_laser_ammunition > 60 and super_mode == False:  # As K_SPACE won't active if you don't moving, if you have pressed the K_SPACE all the time: <-----
                attack_laser = True
                recharge_normal_laser = False
            if counter_normal_laser_ammunition >= 250:
                recharge_normal_laser = False

        #Recharge super mode
        if recharge_super_mode == True and counter_super_mode < 400:
            counter_super_mode += 0.125
            if counter_super_mode >= 400:
                recharge_super_mode = False

        #Recharge missile
        if counter_missile_ammunition < 5:
            counter_missile_ammunition += 0.0078125


        #___Boss actions
        #-Movement
        counter_boss_movement += 1
        if counter_boss_movement > 15 or boss.rect.x in (0, WIDTH_SCREEN):
            boss.movement = random.choice(("right", "left"))
            counter_boss_movement = 0
        boss.update_movement()

        #-Attack
        boss_attack = random.choice(("attack", "a", "e", "i", "o", "u", "pass"))  # a,e,i,o for - probability of attack
        if boss_attack == "attack" and boss.counter_attack_laser == 0:
            boss.counter_attack_laser = 10
            boss.shoot(boss_laser, list_shoots_boss)
            sound_laser_boss.play()
        boss.control_frecuency_shoots()

        #================================UPDATE============================
        #--------------------Background
        #___Scroll
        counter_scroll += 2
        if counter_scroll >= space.get_rect()[3]:
            counter_scroll = 0
        DISPLAYSURF.blit(space, (0, space.get_rect()[3]*-1+counter_scroll))
        DISPLAYSURF.blit(space, (0, counter_scroll))

        #___White pixels(stars)
        update_stars(DISPLAYSURF, stars_layer3, 1)
        update_stars(DISPLAYSURF, stars_layer2, 6)
        update_stars(DISPLAYSURF, stars_layer3, 3)

        #--------------------Lasers/Missiles
        #___Boss shoots
        if super_mode == False:
            update_shoots(DISPLAYSURF, list_shoots_boss, player, False, 15, 5)
        else:
            update_shoots(DISPLAYSURF, list_shoots_boss, player, True, 15, 5)

        #___Player shoots
        #-Normal shoots
        update_shoots(DISPLAYSURF, list_normal_shoots_player, boss, False, -15, 2)

        #-Special shoots
        update_shoots(DISPLAYSURF, list_special_shoots_player, boss, False, -15, 10)

        #-Missiles
        update_shoots(DISPLAYSURF, list_missiles_player, boss, False, -15, 15)

        #--------------------Ships
        DISPLAYSURF.blit(boss.image, (boss.rect.x, 0))
        DISPLAYSURF.blit(player.image, (player.rect.x, player.rect.y))

        #--------------------Bars
        #___Boss bars
        bar_boss_life = create_bar(DISPLAYSURF, WIDTH_SCREEN//2-250, 500, WIDTH_SCREEN//2-boss.life/4, boss.life/2, 5, 30, (150, 0, 0, 175), str(boss.life), "/1000", font_big, (255, 0, 100, 200)  )
        DISPLAYSURF.blit(bar_boss_life[2], (WIDTH_SCREEN//2-bar_boss_life[2].get_width()//2, 8))

        #__Players bars
        #(surface, pos_x_bar, size_bar, pos_x_stuffed, size_stuffed,  pos_y, size_y, color_stuffed, text, all_text, size_text, color_text)
        #--Life
        bar_life = create_bar(DISPLAYSURF, WIDTH_SCREEN//130, 200, WIDTH_SCREEN//130, player.life, 760, 30, (0, 255, 0, 175), str(player.life), "/200", font_big, (0, 255, 100, 200))
        DISPLAYSURF.blit(bar_life[2], (25, 762.5))

        #--Normal lasers
        bar_lasers_ammunition = create_bar(DISPLAYSURF, WIDTH_SCREEN-260, 250, WIDTH_SCREEN-counter_normal_laser_ammunition-10, counter_normal_laser_ammunition+1, 760, 30, (0, 0, 255, 200), str(int(counter_normal_laser_ammunition)), "/250", font_big, (0, 100, 255, 175))
        DISPLAYSURF.blit(bar_lasers_ammunition[2], (WIDTH_SCREEN-260+bar_lasers_ammunition[2].get_width()//4, 762.5))

        #--Super mode
        bar_super_mode = create_bar(DISPLAYSURF, WIDTH_SCREEN-210, 200, WIDTH_SCREEN-counter_super_mode*0.5-10, counter_super_mode*0.5+1, 735, 15, (255, 255, 0, 200), "SUPER MODE", "", font_small, (255, 255, 100, 175))
        DISPLAYSURF.blit(bar_super_mode[2], (WIDTH_SCREEN-185, 734.5))

        #--Missiles
        bar_missiles_ammunition = create_bar(DISPLAYSURF, WIDTH_SCREEN-110, 100, WIDTH_SCREEN-counter_missile_ammunition*20-10, counter_missile_ammunition*20+1, 700, 25, (255, 100, 0, 200), str(int(counter_missile_ammunition)), "/5", font_big, (255, 100, 0, 175))
        DISPLAYSURF.blit(bar_missiles_ammunition[2], (WIDTH_SCREEN-113+bar_missiles_ammunition[2].get_width()//4, 700))

    #--------------------End of game
    elif player.life <= 0 or boss.life <= 0:
        counter_end += 1
        if player.life <= 0:
            image_you = pygame.image.load("Graphics/Letters end/you.png")
            DISPLAYSURF.blit(image_you, (0, 0))
            if counter_end > 20 and counter_end < 50:
                image_you_are = pygame.image.load("Graphics/Letters end/you_are.png")
                DISPLAYSURF.blit(image_you_are, (0, 0))
            if counter_end > 50:
                image_you_are_dead = pygame.image.load("Graphics/Letters end/you_are_dead.png")
                DISPLAYSURF.blit(image_you_are_dead, (0, 0))

        elif boss.life <= 0:
            image_win = pygame.image.load("Graphics/Letters end/win.png")
            DISPLAYSURF.blit(image_win, (0, 0))

    #--------------------Update, FPS
    pygame.display.update()
    fpsClock.tick(FPS)


#--Que hay que hacer?
# 1. Moverse y disparar a la vez  ***  HECHO
# 2. Control de vida y los láseres del jugador y la vida del enemigo ***  HECHO
# 3. Mostrar vida enemigo y munición actual  ***  HECHO
# 4. Que el enemigo dispare y mostrar vida actual  ***  HECHO
# 5. Opción de utilizar munición especial y misiles y mostrarlo  ***  HECHO
# 6. Añadir sonidos  HECHO
# 7. Añadir pausa con manual de instrucciones (como utilizar el teclado) ***  HECHO
# 8. Texto fin del juego ***  HECHO
# 9. Optimizar código utilizando funciones  ***  HECHO

#--Problemas:
# 1. Los disparos del enemigo traspasaban al jugador  ***  SOLUCIONADO (al utilizar la función, debía de haber algún fallo escrito)
# 2. Bug al usar el 'super mode' que al terminarlo SIN DISPARAR no deja disparar normal  ***  SOLUCIONADO (al soltar el espacio en el bucle de eventos se activaba automáticamente)
# 3. Bug al utilizar el menú cuando termina la partida, pues la imagen de fondo que queda es la del menú  ***  ERROR
# 4. Los misiles se podían disparar demasiado rápido  ***  SOLUCIONADO (controlar su frecuencia en el bucle)

#--Extras:
# 1. Menú
# 2. Oleada de enemigos
# 3. Guardar puntuación, ganar dinero y opción de comprar otras naves (utilizando como base de datos un fichero)
