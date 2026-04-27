import pygame
import random
import math
from PIL import Image

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game: Corrected RPG Update")
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

# --- ASSETS ---
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
blazerod_img = load_texture("blazerod.png", (40, 40), (255, 165, 0))
ghast_normal = load_texture("ghastpro.png", (70, 70), (255, 255, 255))
ghast_shooting = load_texture("ghastpro1.png", (70, 70), (255, 255, 255))
blazeking_img = load_texture("BlazeKing.png", (80, 80), (255, 100, 0)) 
portal_nether_frames = load_gif_frames("portal.gif", (100, 100))
portal_end_frames = load_gif_frames("endp.gif", (100, 100))
fireball_frames = load_gif_frames("fireball.gif", (40, 40))
dead_frames = load_gif_frames("dead.gif", (450, 450)) 

# ZMIANA: Tło statystyk powiększone o 50% (oryginalnie 260x320 -> teraz 390x480)
stats_bg = load_texture("staty.png", (390, 480), (40, 40, 40), True)

font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 16, bold=True)
big_font = pygame.font.SysFont("Arial", 40, bold=True)

# --- STATE ---
def reset_game():
    global player_world_x, player_world_y, player_hp, player_max_hp, player_exp, player_level, player_strength
    global exp_to_next_level, triple_shot, triple_shot_end, last_shot_time, sword
    global bullets, enemies, medkits, powerups, obstacles, generated_chunks
    global portals, world_count, portal_spawned, armors, player_armor, player_max_armor, armor_type
    global blaze_king_spawned, game_paused
    player_world_x, player_world_y = 0, 0
    player_hp, player_max_hp = 10.0, 10.0
    player_exp, player_level = 0, 1
    player_strength = 1
    exp_to_next_level = 10
    triple_shot, triple_shot_end, last_shot_time = False, 0, 0
    sword, player_armor, player_max_armor, armor_type = None, 0, 1, 1
    bullets, enemies, medkits, powerups, portals, obstacles, armors = [], [], [], [], [], [], []
    generated_chunks = set()
    world_count, portal_spawned, blaze_king_spawned = 1, False, False
    game_paused = False

def normalize_vector(dx, dy):
    dist = math.hypot(dx, dy)
    return (dx/dist, dy/dist) if dist != 0 else (0, 0)

# --- LEVEL UP MENU ---
def show_level_up_menu():
    global player_max_hp, player_hp, player_strength
    
    rand_val = random.randint(1, 20)
    is_hp_boost = random.choice([True, False])
    rand_desc = f"+{rand_val} do Zyworności" if is_hp_boost else f"+{rand_val} do Sily"
    
    paused = True
    while paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        title = big_font.render("AWANS POZIOMU!", True, (255, 215, 0))
        instr = font.render("Wybierz ulepszenie (nacisnij 1, 2 lub 3):", True, (255, 255, 255))
        opt1 = font.render(f"1. +1 do Zyworności (Max HP)", True, (100, 255, 100))
        opt2 = font.render(f"2. +1 do Sily (Obrazenia)", True, (255, 100, 100))
        opt3 = font.render(f"3. Losowe: {rand_desc}", True, (100, 200, 255))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 220))
        screen.blit(opt1, (WIDTH//2 - 150, 300))
        screen.blit(opt2, (WIDTH//2 - 150, 350))
        screen.blit(opt3, (WIDTH//2 - 150, 400))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player_max_hp += 1; player_hp = min(player_hp + 1, player_max_hp); paused = False
                elif event.key == pygame.K_2:
                    player_strength += 1; paused = False
                elif event.key == pygame.K_3:
                    if is_hp_boost: 
                        player_max_hp += rand_val; player_hp = min(player_hp + rand_val, player_max_hp)
                    else: 
                        player_strength += rand_val
                    paused = False
            if event.type == pygame.QUIT:
                pygame.quit(); exit()

def spawn_enemy():
    global blaze_king_spawned
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
    blaze_king_template = {'type': 'blazeking', 'speed': 1.6, 'hp': 120, 'max_hp': 120, 'img': blazeking_img, 'shoot_cd': 1200}
    
    if world_count == 1: pool = mobs_w1
    elif world_count == 2: pool = mobs_w2
    else: pool = mobs_w2 + [{'type': 'fast', 'speed': 5.0, 'hp': 15, 'img': load_texture("ende.png", (60, 60), (50,0,50))}]
    
    if world_count == 2 and not blaze_king_spawned and random.random() < 0.08:
        enemy = blaze_king_template.copy()
        blaze_king_spawned = True
    else:
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

def draw_bar(x, y, w, h, percent, color, label=""):
    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * max(0, min(1, percent))), h))
    if label:
        txt = small_font.render(label, True, (255, 255, 255))
        screen.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

def generate_chunk(cx, cy):
    if (cx, cy) in generated_chunks: return
    if cx != 0 or cy != 0:
        c_obs_img = obs_img1 if world_count == 1 else obs_img2 if world_count == 2 else obs_img3
        for _ in range(random.randint(2, 5)):
            w, h = random.randint(45, 100), random.randint(45, 100)
            rx, ry = cx*600 + random.randint(0, 600-w), cy*600 + random.randint(0, 600-h)
            obstacles.append({'rect': pygame.Rect(rx, ry, w, h), 'img': pygame.transform.scale(c_obs_img, (w, h))})
    generated_chunks.add((cx, cy))

# ZMIANA: Zaktualizowana funkcja rysująca panel statystyk (dopasowana do większego tła)
def draw_stats_panel():
    # Panel szerszy, więc przesuwamy go bardziej w lewo
    panel_x, panel_y = WIDTH - 410, 60
    screen.blit(stats_bg, (panel_x, panel_y))
    
    world_names = {1: "Powierzchnia", 2: "Nether", 3: "The End"}
    current_world = world_names.get(world_count, "Nieznany")
    
    stats_txt = [
        ("STATYSTYKI", (255, 215, 0)),
        (f"Poziom: {player_level}", (255, 255, 255)),
        (f"Sila: {player_strength}", (255, 255, 255)),
        (f"Max HP: {int(player_max_hp)}", (255, 255, 255)),
        (f"Swiat: {current_world}", (150, 255, 150)),
        (f"EXP: {player_exp}/{exp_to_next_level}", (0, 190, 255))
    ]
    
    # Większe odstępy (50px) i marginesy (40px) dla lepszej czytelności
    for i, (text, color) in enumerate(stats_txt):
        surf = font.render(text, True, color)
        screen.blit(surf, (panel_x + 40, panel_y + 50 + (i * 50)))

# --- MAIN LOOP ---
reset_game()
running, game_over = True, False

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
        if not any(pygame.Rect(nx-25, ny-25, 50, 50).colliderect(o['rect']) for o in obstacles if math.hypot(o['rect'].centerx-player_world_x, o['rect'].centery-player_world_y)<200):
            player_world_x, player_world_y = nx, ny
        
        cam_x, cam_y = player_world_x - WIDTH//2, player_world_y - HEIGHT//2
        bg = grass_img1 if world_count == 1 else grass_img2 if world_count == 2 else grass_img3
        bg_w, bg_h = bg.get_size()
        for x in range(int(-cam_x % bg_w) - bg_w, WIDTH + bg_w, bg_w):
            for y in range(int(-cam_y % bg_h) - bg_h, HEIGHT + bg_h, bg_h): screen.blit(bg, (x, y))
        
        for o in obstacles:
            if screen.get_rect().colliderect(o['rect'].move(-cam_x, -cam_y)):
                screen.blit(o['img'], (o['rect'].x-cam_x, o['rect'].y-cam_y))

        # SHOOTING
        if current_time - last_shot_time > 400 and enemies:
            target = min(enemies, key=lambda e: math.hypot(e['x']-player_world_x, e['y']-player_world_y))
            bdx, bdy = normalize_vector(target['x']-player_world_x, target['y']-player_world_y)
            if triple_shot and current_time > triple_shot_end: triple_shot = False
            for a in ([-0.3, 0, 0.3] if triple_shot else [0]):
                fdx, fdy = bdx*math.cos(a)-bdy*math.sin(a), bdx*math.sin(a)+bdy*math.cos(a)
                bullets.append({'x':player_world_x, 'y':player_world_y, 'dx':fdx, 'dy':fdy, 'team':'player', 'type':'arrow'})
            last_shot_time = current_time

        # BULLETS
        for b in bullets[:]:
            b['x'] += b['dx'] * (12 if b['type'] == 'arrow' else 8)
            b['y'] += b['dy'] * (12 if b['type'] == 'arrow' else 8)
            img = fireball_frames[(current_time // 60) % len(fireball_frames)] if b['type'] == 'fireball' else pygame.transform.rotate(arrow_img, math.degrees(math.atan2(-b['dy'], b['dx'])))
            br = img.get_rect(center=(b['x']-cam_x, b['y']-cam_y))
            screen.blit(img, br)
            
            if b['team'] == 'player':
                for e in enemies[:]:
                    e_hit_size = 80 if e['type'] == 'blazeking' else 50
                    if br.colliderect(pygame.Rect(e['x']-cam_x-e_hit_size//2, e['y']-cam_y-e_hit_size//2, e_hit_size, e_hit_size)):
                        e['hp'] -= (1 + player_strength * 0.1)
                        if b in bullets: bullets.remove(b)
                        if e['hp'] <= 0:
                            is_boss = e['type'] == 'blazeking'
                            enemies.remove(e); player_exp += 15 if is_boss else 2
                            if world_count == 1 and not portal_spawned and random.random() < 0.05:
                                portals.append({'rect': pygame.Rect(e['x'], e['y'], 100, 100), 'target': 2}); portal_spawned = True
                            elif world_count == 2 and not portal_spawned and is_boss:
                                portals.append({'rect': pygame.Rect(e['x'], e['y'], 100, 100), 'target': 3}); portal_spawned = True
                            rnd = random.random()
                            apple_chance = 0.45 if world_count == 2 else 0.15
                            if rnd < apple_chance: medkits.append({'x':e['x'],'y':e['y']})
                            elif rnd < apple_chance + 0.05: powerups.append({'x':e['x'],'y':e['y']})
                            elif rnd < apple_chance + 0.70: armors.append({'x':e['x'],'y':e['y'], 'type': 1 if world_count == 1 else 2})
                        break
            elif br.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                take_damage(3 if b['type'] == 'fireball' else 1); bullets.remove(b)

        # SPAWN & ENEMIES
        spawn_rate = 180 if world_count == 2 else 90 
        if random.randint(1, spawn_rate) == 1: spawn_enemy()
            
        for e in enemies[:]:
            ex, ey = normalize_vector(player_world_x - e['x'], player_world_y - e['y'])
            e['x'] += ex * e['speed']; e['y'] += ey * e['speed']
            img = e['img_shoot'] if e['type'] == 'ghast' and current_time - e.get('last_shot', 0) < 500 else e['img']
            er = img.get_rect(center=(e['x']-cam_x, e['y']-cam_y))
            screen.blit(img, er)

            if e['type'] == 'blazeking':
                draw_bar(WIDTH//2 - 150, 20, 300, 15, e['hp']/120, (255, 165, 0))
                erx, ery = e['x'] + math.cos(current_time*0.008)*110, e['y'] + math.sin(current_time*0.008)*110
                rod_r = blazerod_img.get_rect(center=(erx-cam_x, ery-cam_y))
                screen.blit(blazerod_img, rod_r)
                if rod_r.move(cam_x, cam_y).colliderect(pygame.Rect(player_world_x-25, player_world_y-25, 50, 50)): take_damage(0.15)

            if 'shoot_cd' in e and current_time - e['last_shot'] > e['shoot_cd']:
                dx, dy = normalize_vector(player_world_x - e['x'], player_world_y - e['y'])
                bullets.append({'x':e['x'], 'y':e['y'], 'dx':dx, 'dy':dy, 'team':'enemy', 'type': 'fireball' if e['type'] in ['ghast', 'blaze', 'blazeking'] else 'arrow'})
                e['last_shot'] = current_time
            if er.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)): take_damage(0.05)

        # LEVEL UP LOGIC
        if player_exp >= exp_to_next_level:
            player_level += 1
            player_exp = 0
            exp_to_next_level = int(exp_to_next_level * 1.5)
            sword = {'ang': 0, 'time': current_time, 'dur': 10000} 
            show_level_up_menu() 

        if sword and current_time < sword['time'] + sword['dur']:
            sword['ang'] += 0.18
            sx, sy = player_world_x + math.cos(sword['ang'])*95, player_world_y + math.sin(sword['ang'])*95
            screen.blit(sword_img, sword_img.get_rect(center=(sx-cam_x, sy-cam_y)))
            sw_rect = pygame.Rect(sx-20, sy-20, 40, 40)
            for e in enemies[:]:
                e_sz = 80 if e['type'] == 'blazeking' else 50
                if sw_rect.colliderect(pygame.Rect(e['x']-e_sz//2, e['y']-e_sz//2, e_sz, e_sz)):
                    e['hp'] -= (0.3 + player_strength * 0.05)
                    if e['hp'] <= 0:
                        is_boss = e['type'] == 'blazeking'
                        enemies.remove(e); player_exp += 15 if is_boss else 2

        # UI - Pasek życia
        hp_label = f"HP: {int(player_hp)} / {int(player_max_hp)}"
        draw_bar(10, 10, 200, 22, player_hp/player_max_hp, (220, 20, 60), hp_label)
        
        if player_armor > 0: draw_bar(10, 10, 200, 5, player_armor/player_max_armor, (100, 100, 255))
        draw_bar(10, 38, 200, 10, player_exp/exp_to_next_level, (0, 150, 255))
        screen.blit(font.render(f"LVL: {player_level} | STR: {player_strength}", True, (255, 255, 255)), (10, 55))

        # ELEMENTY ŚWIATA
        for p in portals[:]:
            f = portal_nether_frames if p['target'] == 2 else portal_end_frames
            screen.blit(f[(current_time // 100) % len(f)], p['rect'].move(-cam_x, -cam_y))
            if p['rect'].move(-cam_x, -cam_y).colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                world_count = p['target']; enemies.clear(); bullets.clear(); portals.clear(); obstacles.clear(); generated_chunks.clear()
                portal_spawned = False; player_hp = player_max_hp

        for m in medkits[:]:
            mr = apple_img.get_rect(center=(m['x']-cam_x, m['y']-cam_y))
            screen.blit(apple_img, mr); 
            if mr.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)): player_hp = min(player_hp+10, player_max_hp); medkits.remove(m)
        
        for p in powerups[:]:
            pr = book_img.get_rect(center=(p['x']-cam_x, p['y']-cam_y))
            screen.blit(book_img, pr); 
            if pr.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)): triple_shot = True; triple_shot_end = current_time+8000; powerups.remove(p)

        for a in armors[:]:
            img = armor1_img if a['type'] == 1 else armor2_img
            ar = img.get_rect(center=(a['x']-cam_x, a['y']-cam_y))
            screen.blit(img, ar)
            if ar.colliderect(pygame.Rect(WIDTH//2-25, HEIGHT//2-25, 50, 50)):
                armor_type = a['type']; player_max_armor = 60 if armor_type == 1 else 120
                player_armor = player_max_armor; armors.remove(a)

        # GRACZ
        rot_p = pygame.transform.rotate(player_img, math.degrees(math.atan2(-vy, vx))) if vx or vy else player_img
        screen.blit(rot_p, rot_p.get_rect(center=(WIDTH//2, HEIGHT//2)))

        # OBSŁUGA KLAWISZA Q (Statystyki)
        if keys[pygame.K_q]:
            draw_stats_panel()

        if player_hp <= 0: game_over = True

    else:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0, 0, 0, 180)); screen.blit(s, (0, 0))
        screen.blit(dead_frames[(current_time // 120) % len(dead_frames)], dead_frames[0].get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
        screen.blit(font.render("Nacisnij 'R' aby zrestartować", True, (255, 255, 255)), (WIDTH//2 - 120, HEIGHT//2 + 210))

    pygame.display.flip()
pygame.quit()