import pygame
import random
import math
from PIL import Image

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game: The End Update")
clock = pygame.time.Clock()

# --- HELPER: LOADING & GIF ---
def load_texture(path, size, fallback_color, alpha=True):
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        return pygame.transform.scale(img, size)
    except:
        img = pygame.Surface(size)
        img.fill(fallback_color)
        if alpha: img.set_colorkey((0,0,0))
        return img

def load_gif_frames(filename, size):
    try:
        pil_image = Image.open(filename)
        frames = []
        try:
            while True:
                frame = pil_image.convert('RGBA')
                pygame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                frames.append(pygame.transform.scale(pygame_surface, size))
                pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pass 
        return frames
    except:
        img = pygame.Surface(size); img.fill((50, 50, 50))
        return [img]

# --- CONSTANTS & ASSETS ---
player_img = load_texture("steve.png", (50, 50), (0, 255, 0))
grass_img1 = load_texture("grass.png", (64, 64), (34, 139, 34), False).convert()
grass_img2 = load_texture("grass2.jpg", (64, 64), (100, 30, 30), False).convert()
grass_img3 = load_texture("endstone.png", (64, 64), (240, 230, 140), False).convert()

obs_img1 = load_texture("cobblestone.png", (64, 64), (100, 100, 100), False)
obs_img2 = load_texture("cobblestone2.png", (64, 64), (50, 0, 0), False)
obs_img3 = load_texture("obsidian.png", (64, 64), (20, 0, 40), False)

arrow_img = load_texture("arrow.png", (20, 20), (255, 255, 0))
apple_img = load_texture("apple.png", (25, 25), (255, 0, 0))
book_img = load_texture("book.png", (35, 35), (139, 69, 19))
armor1_img = load_texture("armor1.png", (30, 30), (192, 192, 192))
armor2_img = load_texture("armor2.png", (30, 30), (50, 50, 255))
sword_img = load_texture("sword.png", (40, 40), (200, 200, 200))
sword2_img = load_texture("sword2.png", (40, 40), (255, 50, 50))

ghast_normal = load_texture("ghastpro.png", (70, 70), (255, 255, 255))
ghast_shooting = load_texture("ghastpro1.png", (70, 70), (255, 255, 255))

portal_nether_frames = load_gif_frames("portal.gif", (100, 100))
portal_end_frames = load_gif_frames("endp.gif", (100, 100))
fireball_frames = load_gif_frames("fireball.gif", (40, 40))
dead_frames = load_gif_frames("dead.gif", (450, 450)) 

portal_anim_speed = 100
fireball_anim_speed = 60
dead_anim_speed = 120

# --- MOBS ---
mobs_w1 = [
    {'type': 'shooter', 'speed': 1.5, 'hp': 3, 'img': load_texture("szkielet.png", (50, 50), (200,200,200)), 'shoot_cd': 2000},
    {'type': 'slow', 'speed': 1.1, 'hp': 5, 'img': load_texture("zombie.png", (50, 50), (0,150,0))},
    {'type': 'fast', 'speed': 3.2, 'hp': 2, 'img': load_texture("ende.png", (50, 50), (100,0,100))}
]

mobs_w2 = [
    {'type': 'ghast', 'speed': 1.0, 'hp': 12, 'img': ghast_normal, 'img_shoot': ghast_shooting, 'shoot_cd': 2500},
    {'type': 'blaze', 'speed': 2.2, 'hp': 6, 'img': load_texture("blaze.jpg", (50, 50), (255,200,0)), 'shoot_cd': 1000},
    {'type': 'pigman', 'speed': 1.8, 'hp': 8, 'img': load_texture("pig.jpg", (50, 50), (255,150,150))},
    {'type': 'skeleton_fast', 'speed': 4.5, 'hp': 4, 'img': load_texture("szkiel.jpg", (50, 50), (220,220,220))}
]

mobs_w3 = mobs_w2 + [{'type': 'fast', 'speed': 5.0, 'hp': 15, 'img': load_texture("ende.png", (60, 60), (50,0,50))}]

font = pygame.font.SysFont("Arial", 24, bold=True)

# --- STATE ---
def reset_game():
    global player_world_x, player_world_y, player_hp, player_max_hp, player_exp, player_level
    global exp_to_next_level, triple_shot, triple_shot_end, last_shot_time, sword
    global bullets, enemies, medkits, powerups, obstacles, generated_chunks
    global portals, world_count, portal_spawned, armors, player_armor, player_max_armor, armor_type
    player_world_x, player_world_y = 0, 0
    player_hp, player_max_hp = 10, 10
    player_exp, player_level = 0, 1
    exp_to_next_level = 10
    triple_shot = False
    triple_shot_end = 0
    last_shot_time = 0
    sword = None
    player_armor = 0
    player_max_armor = 1
    armor_type = 1
    bullets, enemies, medkits, powerups, portals, obstacles, armors = [], [], [], [], [], [], []
    generated_chunks = set()
    world_count, portal_spawned = 1, False

def normalize_vector(dx, dy):
    dist = math.hypot(dx, dy)
    return (dx/dist, dy/dist) if dist != 0 else (0, 0)

def spawn_enemy():
    if world_count == 1: pool = mobs_w1
    elif world_count == 2: pool = mobs_w2
    else: pool = mobs_w3
    
    enemy = random.choice(pool).copy()
    angle = random.uniform(0, 2*math.pi)
    r = random.uniform(550, 750)
    enemy['x'], enemy['y'] = player_world_x + math.cos(angle)*r, player_world_y + math.sin(angle)*r
    if 'shoot_cd' in enemy: enemy['last_shot'] = pygame.time.get_ticks()
    enemies.append(enemy)

def take_damage(amount):
    global player_hp, player_armor
    if player_armor > 0:
        reduction = 0.3 if armor_type == 1 else 0.6
        player_hp -= amount * (1 - reduction)
        player_armor -= 1 
    else:
        player_hp -= amount

def draw_bar(x, y, w, h, percent, color):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * max(0, min(1, percent))), h))

def generate_chunk(cx, cy):
    if (cx, cy) in generated_chunks: return
    if cx != 0 or cy != 0:
        if world_count == 1: c_obs_img = obs_img1
        elif world_count == 2: c_obs_img = obs_img2
        else: c_obs_img = obs_img3
        
        for _ in range(random.randint(2, 5)):
            w, h = random.randint(45, 100), random.randint(45, 100)
            rx, ry = cx*600 + random.randint(0, 600-w), cy*600 + random.randint(0, 600-h)
            obstacles.append({'rect': pygame.Rect(rx, ry, w, h), 'img': pygame.transform.scale(c_obs_img, (w, h))})
    generated_chunks.add((cx, cy))

# --- MAIN LOOP ---
reset_game()
running = True
game_over = False

while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r: reset_game(); game_over = False

    if not game_over:
        p_cx, p_cy = int(player_world_x // 600), int(player_world_y // 600)
        for r in range(-1, 2):
            for c in range(-1, 2): generate_chunk(p_cx + r, p_cy + c)

        keys = pygame.key.get_pressed()
        vx, vy = normalize_vector(keys[pygame.K_d]-keys[pygame.K_a], keys[pygame.K_s]-keys[pygame.K_w])
        nx, ny = player_world_x + vx*5, player_world_y + vy*5
        pf = pygame.Rect(nx-25, ny-25, 50, 50)
        
        if not any(pf.colliderect(o['rect']) for o in obstacles if math.hypot(o['rect'].centerx-player_world_x, o['rect'].centery-player_world_y)<200):
            player_world_x, player_world_y = nx, ny
        
        cam_x, cam_y = player_world_x - WIDTH//2, player_world_y - HEIGHT//2

        if world_count == 1: bg = grass_img1
        elif world_count == 2: bg = grass_img2
        else: bg = grass_img3

        bg_w, bg_h = bg.get_size()
        start_x = int(-cam_x % bg_w) - bg_w
        start_y = int(-cam_y % bg_h) - bg_h
        for x in range(start_x, WIDTH + bg_w, bg_w):
            for y in range(start_y, HEIGHT + bg_h, bg_h): screen.blit(bg, (x, y))
        
        for o in obstacles:
            if screen.get_rect().colliderect(o['rect'].move(-cam_x, -cam_y)):
                screen.blit(o['img'], (o['rect'].x-cam_x, o['rect'].y-cam_y))

        # --- PLAYER SHOOTING ---
        if current_time - last_shot_time > 400 and enemies:
            target = min(enemies, key=lambda e: math.hypot(e['x']-player_world_x, e['y']-player_world_y))
            bdx, bdy = normalize_vector(target['x']-player_world_x, target['y']-player_world_y)
            if triple_shot and current_time > triple_shot_end: triple_shot = False
            angs = [-0.3, 0, 0.3] if triple_shot else [0]
            for a in angs:
                fdx, fdy = bdx*math.cos(a)-bdy*math.sin(a), bdx*math.sin(a)+bdy*math.cos(a)
                bullets.append({'x':player_world_x, 'y':player_world_y, 'dx':fdx, 'dy':fdy, 'team':'player', 'type':'arrow'})
            last_shot_time = current_time

        # --- BULLET LOGIC ---
        for b in bullets[:]:
            speed = 12 if b['type'] == 'arrow' else 8
            b['x'] += b['dx'] * speed; b['y'] += b['dy'] * speed
            if b['type'] == 'fireball':
                f_idx = (current_time // fireball_anim_speed) % len(fireball_frames)
                img = fireball_frames[f_idx]
            else:
                img = pygame.transform.rotate(arrow_img, math.degrees(math.atan2(-b['dy'], b['dx'])))
            br = img.get_rect(center=(b['x']-cam_x, b['y']-cam_y))
            screen.blit(img, br)
            
            if b['team'] == 'player':
                for e in enemies[:]:
                    if br.colliderect(pygame.Rect(e['x']-cam_x, e['y']-cam_y, 50, 50)):
                        e['hp'] -= 1
                        if b in bullets: bullets.remove(b)
                        if e['hp'] <= 0:
                            if e in enemies: enemies.remove(e); player_exp += 2
                            rnd = random.random()
                            
                            # --- SZANSE NA PORTALE ---
                            # 5% do Netheru z Overworld
                            if world_count == 1 and not portal_spawned and rnd < 0.05:
                                portals.append({'rect': pygame.Rect(e['x'], e['y'], 100, 100), 'target': 2})
                                portal_spawned = True
                            # 10% do Endu z Netheru (ZMIANA TUTAJ)
                            elif world_count == 2 and not portal_spawned and rnd < 0.10:
                                portals.append({'rect': pygame.Rect(e['x'], e['y'], 100, 100), 'target': 3})
                                portal_spawned = True
                            # --- RESZTA DROPU ---
                            elif rnd < 0.15: medkits.append({'x':e['x'],'y':e['y']})
                            elif rnd < 0.20: powerups.append({'x':e['x'],'y':e['y']})
                            elif rnd < 0.90: armors.append({'x':e['x'],'y':e['y'], 'type': 1 if world_count == 1 else 2})
                        break
            else:
                if br.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                    take_damage(2 if b['type'] == 'fireball' else 1)
                    if b in bullets: bullets.remove(b)

        # --- ENEMY LOGIC ---
        if random.randint(1, 45) == 1: spawn_enemy()
        for e in enemies[:]:
            ex, ey = normalize_vector(player_world_x - e['x'], player_world_y - e['y'])
            e['x'] += ex * e['speed']; e['y'] += ey * e['speed']
            
            current_mob_img = e['img']
            if e['type'] == 'ghast' and current_time - e.get('last_shot', 0) < 500:
                current_mob_img = e['img_shoot']
            
            er = pygame.Rect(e['x']-cam_x, e['y']-cam_y, 50, 50)
            screen.blit(current_mob_img, er)

            if e['type'] == 'skeleton_fast':
                e_ang = current_time * 0.01 
                esx, esy = e['x'] + math.cos(e_ang) * 70, e['y'] + math.sin(e_ang) * 70
                es_rect = sword2_img.get_rect(center=(esx-cam_x, esy-cam_y))
                screen.blit(sword2_img, es_rect)
                if es_rect.move(cam_x, cam_y).colliderect(pygame.Rect(player_world_x-25, player_world_y-25, 50, 50)):
                    take_damage(0.05)

            if 'shoot_cd' in e and current_time - e['last_shot'] > e['shoot_cd']:
                dx, dy = normalize_vector(player_world_x - e['x'], player_world_y - e['y'])
                b_type = 'fireball' if e['type'] in ['ghast', 'blaze'] else 'arrow'
                bullets.append({'x':e['x'], 'y':e['y'], 'dx':dx, 'dy':dy, 'team':'enemy', 'type': b_type})
                e['last_shot'] = current_time
            
            if er.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)): take_damage(0.05)

        # --- PLAYER SWORD & LEVEL UP ---
        if player_exp >= exp_to_next_level:
            player_level += 1; player_exp = 0; exp_to_next_level = int(exp_to_next_level*1.4)
            player_max_hp += 2; player_hp = player_max_hp
            sword = {'ang': 0, 'time': current_time, 'dur': 10000}

        if sword and current_time < sword['time'] + sword['dur']:
            sword['ang'] += 0.18
            sx, sy = player_world_x + math.cos(sword['ang'])*95, player_world_y + math.sin(sword['ang'])*95
            sr_screen = sword_img.get_rect(center=(sx-cam_x, sy-cam_y))
            screen.blit(sword_img, sr_screen)
            sword_world_rect = pygame.Rect(sx-20, sy-20, 40, 40)
            for e in enemies[:]:
                if sword_world_rect.colliderect(pygame.Rect(e['x']-25, e['y']-25, 50, 50)):
                    e['hp'] -= 0.3
                    if e['hp'] <= 0 and e in enemies: enemies.remove(e); player_exp += 2

        # UI
        draw_bar(10, 10, 200, 20, player_hp/player_max_hp, (255, 0, 0))
        if player_armor > 0: draw_bar(10, 10, 200, 5, player_armor/player_max_armor, (100, 100, 255))
        draw_bar(10, 35, 200, 10, player_exp/exp_to_next_level, (0, 150, 255))
        
        world_names = {1: "OVERWORLD", 2: "NETHER", 3: "THE END"}
        world_txt = font.render(f"WORLD: {world_names[world_count]} | LVL: {player_level}", True, (255, 255, 255))
        screen.blit(world_txt, (10, 55))

        # --- Portals & Pickups ---
        for p in portals[:]:
            f_list = portal_nether_frames if p['target'] == 2 else portal_end_frames
            f_idx = (current_time // portal_anim_speed) % len(f_list)
            screen.blit(f_list[f_idx], p['rect'].move(-cam_x, -cam_y))
            if p['rect'].move(-cam_x, -cam_y).colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                world_count = p['target']
                enemies.clear(); bullets.clear(); portals.clear(); obstacles.clear(); generated_chunks.clear()
                portal_spawned = False; player_hp = player_max_hp

        for m in medkits[:]:
            mr = apple_img.get_rect(center=(m['x']-cam_x, m['y']-cam_y))
            screen.blit(apple_img, mr)
            if mr.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                player_hp = min(player_hp+4, player_max_hp); medkits.remove(m)
        
        for p in powerups[:]:
            pr = book_img.get_rect(center=(p['x']-cam_x, p['y']-cam_y))
            screen.blit(book_img, pr)
            if pr.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                triple_shot = True; triple_shot_end = current_time+8000; powerups.remove(p)

        for a in armors[:]:
            img = armor1_img if a['type'] == 1 else armor2_img
            ar = img.get_rect(center=(a['x']-cam_x, a['y']-cam_y))
            screen.blit(img, ar)
            if ar.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                armor_type = a['type']
                player_max_armor = 60 if armor_type == 1 else 120
                player_armor = player_max_armor
                armors.remove(a)

        rot_p = pygame.transform.rotate(player_img, math.degrees(math.atan2(-vy, vx))) if vx or vy else player_img
        screen.blit(rot_p, rot_p.get_rect(center=(WIDTH//2, HEIGHT//2)))

        if player_hp <= 0: game_over = True

    else: # GAME OVER
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0, 0, 0, 180)); screen.blit(s, (0, 0))
        d_idx = (current_time // dead_anim_speed) % len(dead_frames)
        screen.blit(dead_frames[d_idx], dead_frames[d_idx].get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        restart_txt = font.render("Press 'R' to Restart", True, (255, 255, 255))
        screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, HEIGHT//2 + 210))

    pygame.display.flip()
pygame.quit()