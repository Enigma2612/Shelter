import pygame, sys, time, random, math, os
pygame.init()

W,H = (800,800)

clock = pygame.time.Clock()
FPS = 60
time_font = pygame.font.SysFont("comicsans", 50)

tile_size = 50
drop_vel = 3
level = 1

WIN = pygame.display.set_mode((W,H), 528)
pygame.display.set_caption("SHELTER")

dirt_img = pygame.transform.scale(pygame.image.load("data/dirt.png"), (tile_size, tile_size))
grass_img = pygame.transform.scale(pygame.image.load("data/grass.png"), (tile_size, tile_size))
glass_img = pygame.transform.scale(pygame.image.load('data/glass.png').convert_alpha(), (tile_size, tile_size))
glass_img.set_colorkey('white')
gun_img = pygame.transform.scale(pygame.image.load('data/gun.png').convert_alpha(), (tile_size//2, tile_size//2))
gun_img.set_colorkey('white')
ammo_img = pygame.transform.scale(pygame.image.load('data/ammo.png').convert_alpha(), (tile_size//2, tile_size//2))
ammo_img.set_colorkey('white')
crosshair_img = pygame.transform.scale(pygame.image.load('data/crosshair.png').convert_alpha(), (30,30))
leaf_img = pygame.transform.scale(pygame.image.load('data/leaf.png').convert_alpha(), (tile_size, tile_size))
oak_plank_full_img = pygame.transform.scale(pygame.image.load('data/oak_plank_full.png').convert_alpha(), (tile_size, tile_size))
oak_plank_cracked_img = pygame.transform.scale(pygame.image.load('data/oak_plank_cracked.png').convert_alpha(), (tile_size, tile_size))
oak_plank_chipped_img = pygame.transform.scale(pygame.image.load('data/oak_plank_chipped.png').convert_alpha(), (tile_size, tile_size))

legend = {1: 'dirt', 2: 'grass', 3: 'glass', 4: 'gun', 5: 'ammo', 6: 'leaf', 7: 'oak_plank_full', 8: 'oak_plank_chipped', 9: 'oak_plank_cracked'}


def game():
    global level

    
    def draw_grid():
        for i in range(H//tile_size+1):
            pygame.draw.line(WIN, 'white', (0, i*tile_size), (W, i*tile_size))

        for i in range(W//tile_size+1):
            pygame.draw.line(WIN, 'white', (i*tile_size, 0), (i*tile_size, H))




    class World:
        def __init__(self, data, legend):

            self.tile_list = []
            ammo = 0                        
            for row_count, row in enumerate(data):
                for col_count, tile in enumerate(row):
                    if tile in legend:
                        img = eval(f"{legend[tile]}_img")
                        img_rect = img.get_rect(x = col_count * tile_size, y = row_count * tile_size)
                        img_rect.center = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size).center
                        self.tile_list.append((img, img_rect))

                        if img == ammo_img:
                            ammo += 1

            self.max_ammo = ammo


        def draw(self):
            for tile in self.tile_list:
                WIN.blit(tile[0], tile[1])

#------------------------------------------------
    class Player:
        bullets = []
        gun = False
        ammo = 0
        
        def __init__(self, x, y, w, h, color = 'red', alt_color = 'purple', controls = ['a','d', 'SPACE']):
            player_image = pygame.Surface((w, h))

            self.image = player_image
            self.rect = self.image.get_rect(x=x, y=y)
            self.y_vel = 0
            self.x_vel = 7
            self.jumped = True
            self.color = color
            self.alt_color = alt_color

            self.og_color = color
            self.facing = 'right'
            self.controls = controls
            
        def prune_bullets(self):
            for bul in self.bullets:
                if bul.rect.right < 0 or bul.rect.left > W:
                    self.bullets.remove(bul)
                if bul.rect.bottom < 0 or bul.rect.top > H:
                    self.bullets.remove(bul)



        def update(self):
            dx, dy = 0, 0

            left = self.controls[0]
            right = self.controls[1]
            jump = self.controls[2]
            
            keys = pygame.key.get_pressed()
            if keys[eval(f"pygame.K_{left}")]:
                if self.rect.x - self.x_vel > 0:
                    dx -= self.x_vel
                else:
                    dx -= self.rect.x
                self.facing = 'left'
                    
            if keys[eval(f"pygame.K_{right}")]:
                if self.rect.right + self.x_vel < W:
                    dx += self.x_vel
                else:
                    dx += W - self.rect.right

                self.facing = 'right'

            if keys[eval(f"pygame.K_{jump}")] and not self.jumped:
                self.y_vel = -15
                self.jumped = True

            self.y_vel += 1
            dy += self.y_vel

            ammo_gained = False
            
            for tile in world.tile_list:
                #x collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):

                    if tile[0] == gun_img:
                        if tile in world.tile_list:
                            world.tile_list.remove(tile)
                        self.gun = True

                    if tile[0] == ammo_img:
                        if tile in world.tile_list:
                            world.tile_list.remove(tile)

                        if self.ammo + 1 <= world.max_ammo:
                            self.ammo += 1
                            ammo_gained = True

                    elif dx < 0:
                        self.rect.left = tile[1].right
                        dx = 0
                    elif dx > 0:
                        self.rect.right = tile[1].left
                        dx = 0

                    if tile[0] == oak_plank_cracked_img:
                        if tile in world.tile_list:
                            world.tile_list.remove(tile)


                    
                #y collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                    
                    if self.y_vel < 0 and tile[0] not in [gun_img, ammo_img]:
                        dy = tile[1].bottom - self.rect.top
                        self.y_vel = 0

                    elif self.y_vel >= 0 and tile[0] not in [gun_img, ammo_img]:
                        dy = 0
                        self.y_vel = 0
                        self.rect.bottom = tile[1].top                    
                        self.jumped = False

                    if tile[0] == oak_plank_cracked_img:
                        if tile in world.tile_list:
                            world.tile_list.remove(tile)

                    if tile[0] == gun_img:
                        if tile in world.tile_list:
                            world.tile_list.remove(tile)
                        self.gun = True

                    if tile[0] == ammo_img:
                        if tile in world.tile_list:
                            world.tile_list.remove(tile)
                        if self.ammo + 1 <= world.max_ammo and not ammo_gained:
                            self.ammo += 1

                #bullet hits blocks

                for bullet in self.bullets:
                    if not bullet.super:    
                        if tile[0] in [glass_img, oak_plank_cracked_img] and bullet.rect.colliderect(tile[1]):
                            self.bullets.remove(bullet)
                            if tile in world.tile_list:
                                world.tile_list.remove(tile)

                        elif tile[0] == oak_plank_full_img and bullet.rect.colliderect(tile[1]):
                            img = oak_plank_chipped_img
                            self.bullets.remove(bullet)
                            if tile in world.tile_list:
                                world.tile_list.remove(tile)
                            world.tile_list.append((img, tile[1]))

                        
                        elif tile[0] == oak_plank_chipped_img and bullet.rect.colliderect(tile[1]):
                            img = oak_plank_cracked_img
                            self.bullets.remove(bullet)
                            if tile in world.tile_list:
                                world.tile_list.remove(tile)
                            world.tile_list.append((img, tile[1]))


                        elif (tile[0] in [gun_img, ammo_img]) and bullet.rect.colliderect(tile[1]):
                            continue
                        
                        elif bullet.rect.colliderect(tile[1]):
                            self.bullets.remove(bullet)
                    else:
                        if bullet.rect.colliderect(tile[1]):
                            self.bullets.remove(bullet)
                            if tile in world.tile_list:
                                world.tile_list.remove(tile)
                

            if self.y_vel > 0:
                self.jumped = True
                
            self.rect.x += dx
            self.rect.y += dy

            self.image.fill(self.color)

            if self.ammo >0:
                self.color = self.alt_color
            else:
                self.color = self.og_color

            if self.gun:
                if self.facing == 'right':
                    self.image.blit(gun_img, (0, max(0, self.rect.height - gun_img.get_height())))
                if self.facing == 'left':
                    flipped_gun = pygame.transform.flip(gun_img, True, False).convert_alpha()
                    flipped_gun.set_colorkey('white')

                    self.image.blit(flipped_gun, (self.rect.width - flipped_gun.get_width(), max(0, self.rect.height - flipped_gun.get_height())))

            self.prune_bullets()
             #drawing player
            WIN.blit(self.image, self.rect)

#------------------------------------------------------
            
    class Bullet:
        target = []
        
        def __init__(self, x, y, speed, owner : Player | None = None, Super = False):

            temp_rect = pygame.Rect(x, y, 10, 10)
            temp_rect.center = x,y
            self.rect = temp_rect
            self.vel = speed
            self.owner = owner
            self.super = Super

            self.x = x
            self.y = y

        def shoot(self, target_x, target_y):

            angle = math.atan2(target_y - self.rect.y, target_x - self.rect.x)
            self.dx = math.cos(angle) * self.vel
            self.dy = math.sin(angle) * self.vel

            
        def update(self):
            self.x += self.dx
            self.y += self.dy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)


            pygame.draw.rect(WIN, 'purple', self.rect)


#-----------------------------------------------


    x = len(str(level))

    try:        
        with open(f'data/worlds/w{"0"*(4-x)}{level}.txt') as f:
            world_data = eval(f.read())
            
    except:
        print("YOU COMPLETED THE GAME!")
        pygame.quit()
        time.sleep(2)
        sys.exit()


    with open(f"data/worlds/w{'0'*(4-x)}{level}t.txt") as f:
        time_lim = eval(f.read())

    pygame.display.set_caption(f"SHELTER: LEVEL {level}")

        
    player = Player(0, 0, 40, 80)

    player2 = Player(0, 0, 40, 80, color = 'green', alt_color = 'magenta', controls = ['LEFT', "RIGHT", "UP"])

    lshift = False
    rshift = False
    a=0

    
    et = round(time.time()) + time_lim
    rain = 0
    rain_lis = []
    world = World(world_data, legend)
    
    max_level = max([int(i.split(".")[0][1:]) for i in os.listdir('data/worlds')
                     if (i.split(".")[0][-1] != 't' and i.split(".")[0][1].isdigit())])

    while True:
        clock.tick(FPS)
        mx,my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_n:
                    level += 1
                    return

                if event.key == pygame.K_p:
                    if level > 1:
                        level -= 1
                    else:
                        level = max_level
                    return

                if event.key == pygame.K_LSHIFT:
                    lshift = True
                if event.key == pygame.K_DOWN:
                    rshift = True
                
                if event.key == pygame.K_f:
                    player.gun = True
                    player.ammo += 100
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    lshift = False
                if event.key == pygame.K_DOWN:
                    rshift = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if player.gun and player.ammo > 0:
                        player.ammo -= 1
                        bullet = Bullet(*player.rect.center, 10, player)
                        bullet.target = [mx, my]
                        bullet.shoot(*bullet.target)
                        player.bullets.append(bullet)
                        
                    if player2.gun and player2.ammo > 0:
                        player2.ammo -= 1
                        bullet = Bullet(*player2.rect.center, 10, player2)
                        bullet.target = [mx, my]
                        bullet.shoot(*bullet.target)
                        player2.bullets.append(bullet)                    

        
        WIN.fill("skyblue")

        if lshift:
            if player.rect.height == 80:
                g,a = player.gun, player.ammo
                player = Player(player.rect.x, player.rect.y + 40, 40, 40)
                player.gun, player.ammo = g,a
        if not lshift:
            if player.rect.height == 40:
                g,a = player.gun, player.ammo
                player = Player(player.rect.x, player.rect.y - 40, 40, 80)
                player.gun, player.ammo = g,a
        
        if rshift and not a:
            if player2.rect.height == 80:
                g,a = player2.gun, player2.ammo
                player2 = Player(player2.rect.x, player2.rect.y + 40, 40, 40, color = 'green', alt_color = 'magenta', controls = ['LEFT', "RIGHT", "UP"])
                player2.gun, player2.ammo = g,a

        if not rshift and not a:
            if player2.rect.height == 40 and player2.rect.width == 40:
                g,a = player2.gun, player2.ammo
                player2 = Player(player2.rect.x, player2.rect.y - 40, 40, 80, color = 'green', alt_color = 'magenta', controls = ['LEFT', "RIGHT", "UP"])
                player2.gun, player2.ammo = g,a

        for bullet in player.bullets:
            bullet.update()

        time_left = et - round(time.time())

        if rain == 1:
            for _ in range(150):
                x = random.randint(0, W - 20)
                y = random.randint(-1600, -30)

                drop = pygame.Rect(x, y, 10, 30)
                rain_lis.append(drop)

        for drop in rain_lis[:]:
            pygame.draw.rect(WIN, 'blue', drop)

            if (x:=player.rect.colliderect(drop)) or (y:=player2.rect.colliderect(drop)):
                if x: player.rect.y = H+1
                if y: player2.rect.y = H+1


            if drop.y > H:
                if drop in rain_lis:
                    rain_lis.remove(drop)
            else:
                drop.y += drop_vel

            for tile in world.tile_list:
                if tile[1].colliderect(drop):
                    if tile[0] in [gun_img, ammo_img, leaf_img, oak_plank_cracked_img]:
                        pass
                    elif drop in rain_lis:
                        rain_lis.remove(drop)

        else:
            if rain_lis == [] and rain>0:
                print("LEVEL CLEAR")
                level += 1
                return

        if player.rect.y > H and player2.rect.y > H:
            print("GAME OVER")
            return
        
        for bullet in player.bullets:
            if (a:=(bullet.rect.colliderect(player2.rect) and bullet.owner != player2)) or (b:=(bullet.rect.colliderect(player.rect) and bullet.owner != player)):
                if a: 
                    try: player2 = Player(player2.rect.x, player2.rect.y + player2.rect.height//2, player2.rect.width//2, player2.rect.height//2, color = 'coral', alt_color = 'magenta', controls = ['LEFT', "RIGHT", "UP"]); player.bullets.remove(bullet)
                    except:...


        world.draw()
        player.update()
        player2.update()
        
        if time_left >= 0:
            time_txt = f"Time: {time_left}"
            time_img = time_font.render(time_txt, 1, 'black')
            time_rect = time_img.get_rect(x = 10,y = 10)
            WIN.blit(time_img, time_rect)
        else:
            rain += 1

        if player.ammo > 0 or player2.ammo > 0:
            pygame.mouse.set_visible(False)

            crosshair_rect = crosshair_img.get_rect(center = (mx,my))
            WIN.blit(crosshair_img, crosshair_rect)

        else:
            pygame.mouse.set_visible(True)
##        draw_grid()
        pygame.display.update()


if __name__ == '__main__':
    while True:
        game()

    
 