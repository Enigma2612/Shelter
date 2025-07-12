import pygame, sys, random, time, math, os
pygame.init()

W,H = 800, 800
WIN = pygame.Surface((W,H), pygame.SRCALPHA)
screen = pygame.display.set_mode((W, H+100))
clock, FPS = pygame.time.Clock(), 60
tile_size = 50

pygame.display.set_caption("Level Editor")

dirt_img = pygame.transform.scale(pygame.image.load("data/dirt.png"), (tile_size, tile_size))
grass_img = pygame.tranWsform.scale(pygame.image.load("data/grass.png"), (tile_size, tile_size))
glass_img = pygame.transform.scale(pygame.image.load('data/glass.png').convert_alpha(), (tile_size, tile_size))
glass_img.set_colorkey('white')
gun_img = pygame.transform.scale(pygame.image.load('data/gun.png').convert_alpha(), (tile_size//2, tile_size//2))
gun_img.set_colorkey('white')
ammo_img = pygame.transform.scale(pygame.image.load('data/ammo.png').convert_alpha(), (tile_size//2, tile_size//2))

save_button_img = pygame.transform.scale(pygame.image.load('data/save_button.png').convert(), (100, 50))
load_button_img = pygame.transform.scale(pygame.image.load('data/load_button.png').convert(), (100, 50))

leaf_img = pygame.transform.scale(pygame.image.load('data/leaf.png').convert_alpha(), (tile_size, tile_size))
oak_plank_full_img = pygame.transform.scale(pygame.image.load('data/oak_plank_full.png').convert_alpha(), (tile_size, tile_size))
oak_plank_cracked_img = pygame.transform.scale(pygame.image.load('data/oak_plank_cracked.png').convert_alpha(), (tile_size, tile_size))
oak_plank_chipped_img = pygame.transform.scale(pygame.image.load('data/oak_plank_chipped.png').convert_alpha(), (tile_size, tile_size))

legend = {1: 'dirt', 2: 'grass', 3: 'glass', 4: 'gun', 5: 'ammo', 6: 'leaf', 7: 'oak_plank_full', 8: 'oak_plank_chipped', 9: 'oak_plank_cracked'}

user_time = ''
user_time_col = 'cyan'
entering_time = False


level_font = pygame.font.SysFont("comicsans", 42)
time_font = pygame.font.SysFont(None, 48)


def draw_grid():
    for i in range(H//tile_size+1):
        pygame.draw.line(WIN, 'white', (0, i*tile_size), (W, i*tile_size))

    for i in range(W//tile_size+1):
        pygame.draw.line(WIN, 'white', (i*tile_size, 0), (i*tile_size, H))


class World:
    def __init__(self, data, legend):
        self.data = data
        self.legend = legend
        self.tile_list = []

    def edit(self):
        for row_count, row in enumerate(self.data):
            for col_count, tile in enumerate(row):
                
                if tile in self.legend:
                    img = eval(f"{self.legend[tile]}_img")
                    img_rect = img.get_rect(x = col_count * tile_size, y = row_count * tile_size)
                    img_rect.center = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size).center
                    self.tile_list.append((img, img_rect))
                    
                
    def update(self):

        self.edit()
        
        for tile in self.tile_list:
            WIN.blit(tile[0], tile[1])



with open("data/worlds/world default mode.txt") as f:
    world_data = eval(f.read())

left_down, middle_down, right_down = False, False, False
mouse_tile = 1
run = True

level_num = 1 + max([int(i.split(".")[0][1:]) for i in os.listdir('data/worlds')
                     if (i.split(".")[0][-1] != 't' and i.split(".")[0][1].isdigit())])

while run:
    screen.fill('black')
    screen.blit(WIN, (0,0))
    world = World(world_data, legend)
    
    mx,my = pygame.mouse.get_pos()
    tile_rects = [pygame.Rect(col_count*tile_size, row_count*tile_size, tile_size, tile_size)
                  for row_count, row in enumerate(world.data) for col_count, tile in enumerate(row)]
##    tile_coords = [(i.x//tile_size, i.y//tile_size) for i in tile_rects]
    
    WIN.fill("skyblue")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                left_down = True
            if event.button == 2:
                middle_down = True
            if event.button == 3:
                right_down = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_down = False
            if event.button == 2:
                middle_down = False
            if event.button == 3:
                right_down = False

        if event.type == pygame.MOUSEWHEEL:
            mouse_tile += event.y
            mouse_tile %= max(legend) + 1


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level_num += 1
            if event.key == pygame.K_DOWN:
                if level_num > 1: level_num -= 1
                else: pass


            if entering_time:
                if event.key == pygame.K_BACKSPACE:
                    user_time = user_time[:-1]
                else:
                    user_time += event.unicode
                    


    level_txt = f"Level: {level_num}"
    level_img = level_font.render(level_txt, 1, 'white')
    level_rect = level_img.get_rect(midleft = (20, (H + screen.get_height())//2))

    time_txt = f"Time:"
    time_img = level_font.render(time_txt, 1, 'white')
    time_rect = time_img.get_rect(midleft = (5*W//8, (H + screen.get_height())//2))

    screen.blit(level_img, level_rect)
    screen.blit(time_img, time_rect)

    user_time_space = pygame.Rect(0,0, int((W - time_rect.right)*9/10), int(7/10*(screen.get_height() - H)))
    user_time_space.midleft = time_rect.midright
    user_time_space.left += 5

    if entering_time:
        user_time_col = 'cyan'
    else:
        user_time_col = 'orange'
        
    save_button = save_button_img.get_rect(center = (3*W//8 - 20, H + save_button_img.get_height()))
    load_button = load_button_img.get_rect(center = (11*W//20 - 20, H + load_button_img.get_height()))

    if left_down:
        if save_button.collidepoint((mx,my)):
##            time = int(input(f"Enter time limit for level {level_num} (in seconds): "))

            if user_time.isnumeric():
            
                x = len(str(level_num))
                with open(f"data/worlds/w{'0'*(4-x)}{level_num}.txt", 'w') as f:
                    f.write(str(world_data))

                with open(f"data/worlds/w{'0'*(4-x)}{level_num}t.txt", 'w') as f:
                    f.write(str(user_time))

                user_time_col = 'green'                


            else:
                user_time_col = 'red'

        if load_button.collidepoint((mx,my)):
##            print("LOAD")
            x = len(str(level_num))

            if os.path.exists(f"data/worlds/w{'0'*(4-x)}{level_num}.txt"):
                with open(f"data/worlds/w{'0'*(4-x)}{level_num}.txt") as f:
                    world_data = eval(f.read())
            else:
                with open(f"data/worlds/world default mode.txt") as f:
                    world_data = eval(f.read())

    pygame.draw.rect(screen, user_time_col, user_time_space, 5)
    screen.blit(save_button_img, save_button)
    screen.blit(load_button_img, load_button)


    user_time_img = time_font.render(user_time, 1, 'white')
    user_time_rect = user_time_img.get_rect(center = user_time_space.center)

    screen.blit(user_time_img, user_time_rect)
    

    if left_down:
        for rect in tile_rects:
            if rect.collidepoint((mx,my)):
                col = rect.x//tile_size
                row = rect.y//tile_size

                world_data[row][col] = mouse_tile


        if user_time_space.collidepoint((mx,my)):
            entering_time = True
        else:
            entering_time = False


    if right_down:
        for rect in tile_rects:
            if rect.collidepoint((mx,my)):
                col = rect.x//tile_size
                row = rect.y//tile_size

                world_data[row][col] = 0

        if user_time_space.collidepoint((mx,my)):
            entering_time = True
        else:
            entering_time = False


    if middle_down:
        for rect in tile_rects:
            if rect.collidepoint((mx,my)):
                col = rect.x//tile_size
                row = rect.y//tile_size

                mouse_tile = world_data[row][col]

        if user_time_space.collidepoint((mx,my)):
            entering_time = True
        else:
            entering_time = False

               
    world.update()    
    draw_grid()


    if mouse_tile > 0 and my < H:
        pygame.mouse.set_visible(False)
        mouse_img = eval(f"{legend[mouse_tile]}_img").copy()
        mouse_img.set_alpha(190)
        mouse_img = pygame.transform.scale(mouse_img, (30, 30))

        mouse_rect = mouse_img.get_rect(center = (mx, my))

        WIN.blit(mouse_img, mouse_rect)
        
    else:
        pygame.mouse.set_visible(True)

 
    clock.tick(60)
    pygame.display.update()


else:
    pygame.quit(); sys.exit()


#PENDING STUFF:
#BUTTON FOR SAVING THE NEWLY MADE LEVEL --- TAKE INPUT FOR TIME AFTER THE LEVEL IS SAVED
#BUTTON FOR LOADING PREVIOUS LEVELS
