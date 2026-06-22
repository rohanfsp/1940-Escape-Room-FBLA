import pygame
import json
import os
import sys
import linecache

# Dynamically grabs the exact name of your Python file
CURRENT_FILE = os.path.basename(__file__)

# Initialize Pygame and the Audio Mixer
pygame.init()
pygame.mixer.init()

music_playing = True
try:
    pygame.mixer.music.load("noir_jazz.mp3")
    pygame.mixer.music.set_volume(0.4) 
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Audio warning: Could not load 'noir_jazz.mp3'. {e}")

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================
GAME_WIDTH = 800
TECH_WIDTH = 450  # Extra width for the Tech/Debug Mode panels
SCREEN_HEIGHT = 600

# Panel mode can be None, "PYTHON_BASICS", "BASIC_DETAILS", "SIMULATED_TRACE", "LIVE_KEY_TRACE", "LIVE_FULL_TRACE"
panel_mode = None 
panel_scroll_y = 0  

screen = pygame.display.set_mode((GAME_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("1940 Escape Room - Timeline Mystery")

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (70, 130, 180)
DARK_BLUE = (25, 60, 100)
GREEN = (60, 179, 113)
DARK_GREEN = (34, 139, 34)
RED = (220, 20, 60)
BEIGE = (245, 222, 179)
BROWN = (139, 69, 19)

# Tech/Terminal Colors
TECH_BG = (15, 15, 20)
TECH_GREEN = (50, 205, 50)
TECH_BLUE = (100, 150, 255)
TECH_YELLOW = (255, 215, 0)
TECH_PURPLE = (200, 100, 200)
TECH_RED = (255, 100, 100)

# Fonts
title_font = pygame.font.Font(None, 72)
heading_font = pygame.font.Font(None, 48)
text_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

tech_font_bold = pygame.font.SysFont("courier", 16, bold=True)
tech_font_normal = pygame.font.SysFont("courier", 13)
tech_font_tiny = pygame.font.SysFont("courier", 11)

clock = pygame.time.Clock()
FPS = 60

# ============================================================================
# IMAGE ASSET LOADING
# ============================================================================
BG_FILES = {
    "TITLE": "bg_title.png",
    "INSTRUCTIONS": "bg_instructions.png",
    "STRANGE_ROOM": "bg_strange_room.png",
    "FDR_BROADCAST": "bg_fdr_broadcast.png",
    "CHALLENGE1": "bg_challenge1.png",
    "SYSTEM_GLITCH": "bg_system_glitch.png",
    "FACTORY_WORKER": "bg_factory_worker.png",
    "CHALLENGE2": "bg_challenge2.png",
    "COMMAND_POST": "bg_command_post.png",
    "ROBERT_OPPENHEIMER": "bg_robert_oppenheimer.png",
    "CHALLENGE3": "bg_challenge3.png",
    "SIMULATION_BREACH": "bg_simulation_breach.png",
    "GOVERNMENT_CODE_ANALYST": "bg_government_code_analyst.png",
    "CHALLENGE4": "bg_challenge4.png",
    "FINAL_DOOR": "bg_final_door.png",
    "TIME_TRAVELER": "bg_time_traveler.png",
    "END": "bg_end.png",
    "FAIL": "bg_fail.png" ,
    "NOT_ENOUGH_POINTS": "bg_not_enough_points.png"
}

loaded_bgs = {}
for scene_state, filename in BG_FILES.items():
    try:
        img = pygame.image.load(filename).convert()
        loaded_bgs[scene_state] = pygame.transform.scale(img, (GAME_WIDTH, SCREEN_HEIGHT))
    except:
        loaded_bgs[scene_state] = None

def draw_bg(current_state, fallback_color):
    """Draws the background image if it exists, otherwise uses the fallback color."""
    img = loaded_bgs.get(current_state)
    if img:
        screen.blit(img, (0, 0))
    else:
        screen.fill(fallback_color)

# ============================================================================
# CONTENT DICTIONARY 
# ============================================================================
CONTENT = {
    "challenge1_options": ["Lend-lease act", "Freedom of Speech act", "Space Act", "Digital Act"],
    "challenge1_correct": 0,
    "challenge2_events": ["WWII Begins", "Pearl Harbor", "D-Day", "WWII Ends"],
    "challenge3_options": ["Operation Overlord", "Operation Barbarossa", "Operation Desert Storm", "Operation Torch"],
    "challenge3_correct": 0,
    "challenge4_options": ["1945", "1918", "1914", "1942"],
    "challenge4_correct": 0,
    "end_success": "YOU ESCAPED THE TIMELINE!",
    "end_failure": "TRAPPED IN 1940 FOREVER..."
}

# ============================================================================
# PANEL MODE TEXT DATA
# ============================================================================
PYTHON_BASICS_TEXT = [
    "PYTHON:",
    "Python is a high-level, interpreted language.",
    "It emphasizes code readability with indentation.",
    "",
    "ADVANTAGES:",
    "- Easy to learn and read.",
    "- Huge community and extensive libraries.",
    "- Versatile (Web, AI, Data Science, Games).",
    "",
    "MODULES:",
    "Files containing Python code that can be imported.",
    "They prevent rewriting code (e.g., 'import os').",
    "",
    "PYGAME:",
    "Modules designed for writing video games.",
    "Handles graphics, audio, and user inputs perfectly.",
    "",
    "FURTHER REFERENCE AND READING:",
    "python official: https://www.python.org",
    "pygame official: https://www.pygame.org",
    "python github: https://github.com/python/cpython",
    "pygame github: https://github.com/pygame/pygame"
]

PB_HEADERS = [
    "PYTHON:", 
    "ADVANTAGES:", 
    "MODULES:", 
    "PYGAME:", 
    "FURTHER REFERENCE AND READING:"
]

LOGIC_PATH_TRACE = {
    "TITLE": [
        "-> main() evaluates: if state == 'TITLE':",
        "-> draw_bg('TITLE') executes image rendering",
        "-> draw_button('START GAME') evaluates mouse collision",
        "-> if collision == True: state = 'INSTRUCTIONS'"
    ],
    "INSTRUCTIONS": [
        "-> main() evaluates: if state == 'INSTRUCTIONS':",
        "-> draw_bg('INSTRUCTIONS') executes image rendering",
        "-> if draw_button('Play') == True: state = 'STRANGE_ROOM'"
    ],
    "CHALLENGE1": [
        "-> main() routes execution to draw_challenge1()",
        "-> for i, option in enumerate(CONTENT['challenge1_options']):",
        "->    if draw_button(option) is True: # Collision detected",
        "->       if i == CONTENT['challenge1_correct']:",
        "->          score += 75; challenge1_answered = True",
        "->       else: score -= 50"
    ],
    "CHALLENGE2": [
        "-> main() routes execution to draw_challenge2()",
        "-> if draw_button(event) is True: selected_order.append(i)",
        "-> if len(selected_order) == 4: # Array is full",
        "->    if selected_order == [0, 1, 2, 3]: score += 75",
        "->    else: score -= 50; selected_order.clear()"
    ],
    "CHALLENGE3": [
        "-> main() routes execution to draw_challenge3()",
        "-> for i, option in enumerate(CONTENT['challenge3_options']):",
        "->    if draw_button(option) is True:",
        "->       if i == CONTENT['challenge3_correct']: score += 75",
        "->       else: score -= 50"
    ],
    "CHALLENGE4": [
        "-> main() routes execution to draw_challenge4()",
        "-> for i, option in enumerate(CONTENT['challenge4_options']):",
        "->    if draw_button(option) is True:",
        "->       if i == CONTENT['challenge4_correct']: score += 75",
        "->       else: score -= 50"
    ],
    "FINAL_DOOR": [
        "-> main() routes execution to draw_final_door()",
        "-> if score >= ESCAPE_SCORE_REQUIRED: # evaluates score >= 200",
        "->    if draw_button('Enter the Door') is True: state = 'TIME_TRAVELER'",
        "-> else:",
        "->    if draw_button('Try Again') is True: reset_game()"
    ],
    "END": [
        "-> main() routes execution to draw_end()",
        "-> save_high_score() & save_best_time() trigger OS file writing",
        "-> if draw_button('Play Again') is True: reset_game(); state = 'TITLE'"
    ]
}

DEFAULT_LOGIC_PATH = [
    "-> main() evaluates current state routing",
    "-> draw_bg() loads visual assets into memory",
    "-> draw_button() function awaits True collision state to trigger transition"
]

CODE_LAYOUT_TEXT = [
    "DISPLAY SETTINGS",
    " - Panel modes: PYTHON_BASICS, BASIC_DETAILS,",
    "   SIMULATED_TRACE, LIVE_KEY_TRACE, LIVE_FULL_TRACE",
    " - Colors & Terminal Colors",
    " - Fonts",
    "IMAGE ASSET LOADING",
    "CONTENT DICTIONARY",
    "PANEL MODE TEXT DATA",
    "REAL-TIME TRACING LOGIC (Mode 4 and 5)",
    "GAME STATE VARIABLES",
    "FILE I/O",
    "HELPER FUNCTIONS - UI DRAWING",
    "STATE DRAWING FUNCTIONS",
    "TECH & SUPER DEBUG MODES RENDERING",
    "MAIN GAME LOOP"
]

# ============================================================================
# REAL-TIME TRACING LOGIC (Mode 4 and 5)
# ============================================================================
key_trace_log = []
full_trace_log = []
previous_state = "TITLE"

def live_system_trace(frame, event, arg):
    """
    Hooks directly into the Python interpreter line-by-line!
    """
    if event == 'line':
        co = frame.f_code
        func_name = co.co_name
        filename = co.co_filename
        line_no = frame.f_lineno
        
        if CURRENT_FILE in filename:
            ignored_funcs = [
                'render_wrapped_text', 'draw_side_panel', 'draw_score', 'draw_hints',
                'draw_text_centered', 'draw_text_lines', 'get_state_function_and_key',
                'generate_key_pdb_trace', 'draw_button', 'draw_bg', 'draw_music_icon'
            ]
            if func_name in ignored_funcs:
                return live_system_trace
                
            line_text = linecache.getline(filename, line_no).strip()
            if not line_text: return live_system_trace

            log_entry = f"L{line_no}: [{func_name}] {line_text}"
            
            if panel_mode == "LIVE_KEY_TRACE":
                ignore_noise = [
                    'pygame.', 'clock.tick', 'timer += 1', 'sys.settrace',
                    'draw_bg', 'draw_score', 'draw_hints', 'draw_music_icon',
                    'draw_side_panel', 'screen.fill', 'screen.blit', 'draw_text_centered'
                ]
                if any(n in line_text for n in ignore_noise): 
                    return live_system_trace
                
                if log_entry not in key_trace_log[-40:]:
                    key_trace_log.append(log_entry)
                    if len(key_trace_log) > 1000: key_trace_log.pop(0)

            elif panel_mode == "LIVE_FULL_TRACE":
                if "sys.settrace" in line_text: 
                    return live_system_trace 
                
                if not full_trace_log or full_trace_log[-1] != log_entry:
                    full_trace_log.append(log_entry)
                    if len(full_trace_log) > 1000: full_trace_log.pop(0)

    return live_system_trace

# ============================================================================
# GAME STATE VARIABLES
# ============================================================================
state = "TITLE"
score = 0
POINTS_PER_CHALLENGE = 75
PENALTY_POINTS = 50
ESCAPE_SCORE_REQUIRED = 200
high_score = 0
best_time = 0
challenge1_answered = False
challenge2_answered = False
challenge3_answered = False
challenge4_answered = False
selected_order = []
timer = 0
final_time = 0

# ============================================================================
# FILE I/O
# ============================================================================
def load_high_score():
    global high_score
    try:
        if os.path.exists("highscore.json"):
            with open("highscore.json", "r") as file:
                data = json.load(file)
                high_score = data.get("high_score", 0)
        else:
            high_score = 0
    except Exception:
        high_score = 0

def save_high_score():
    global high_score
    try:
        if score > high_score:
            high_score = score
            with open("highscore.json", "w") as file:
                json.dump({"high_score": high_score}, file)
    except Exception:
        pass

def load_best_time():
    global best_time
    try:
        if os.path.exists("best_time.json"):
            with open("best_time.json", "r") as file:
                data = json.load(file)
                best_time = data.get("best_time", 0)
        else:
            best_time = 0
            with open("best_time.json", "w") as file:
                json.dump({"best_time": best_time}, file)
    except Exception:
        best_time = 0

def save_best_time():
    global best_time, final_time, score
    try:
        if score >= ESCAPE_SCORE_REQUIRED:
            if final_time > 0 and (best_time == 0 or final_time < best_time):
                best_time = final_time
                with open("best_time.json", "w") as file:
                    json.dump({"best_time": best_time}, file)
    except Exception:
        pass

# ============================================================================
# HELPER FUNCTIONS - UI DRAWING
# ============================================================================
def draw_button(text, x, y, width, height, color, hover_color, text_color=WHITE, font=text_font):
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]

    button_rect = pygame.Rect(x, y, width, height)
    is_hovering = button_rect.collidepoint(mouse_pos)
    current_color = hover_color if is_hovering else color

    pygame.draw.rect(screen, current_color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 3)

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

    if is_hovering and mouse_clicked:
        pygame.time.wait(200)
        return True
    return False

def draw_music_icon():
    global music_playing
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    
    icon_x = GAME_WIDTH - 45
    icon_y = 15
    icon_rect = pygame.Rect(icon_x - 5, icon_y - 5, 40, 30)
    is_hovering = icon_rect.collidepoint(mouse_pos)
    
    color = WHITE if is_hovering else GRAY
    
    pygame.draw.rect(screen, color, (icon_x, icon_y + 6, 6, 8))
    pygame.draw.polygon(screen, color, [(icon_x + 6, icon_y + 6), (icon_x + 14, icon_y), (icon_x + 14, icon_y + 20), (icon_x + 6, icon_y + 14)])
    
    if music_playing:
        pygame.draw.line(screen, color, (icon_x + 18, icon_y + 6), (icon_x + 18, icon_y + 14), 2)
        pygame.draw.line(screen, color, (icon_x + 22, icon_y + 3), (icon_x + 22, icon_y + 17), 2)
    else:
        pygame.draw.line(screen, RED, (icon_x + 18, icon_y + 5), (icon_x + 26, icon_y + 15), 3)
        pygame.draw.line(screen, RED, (icon_x + 26, icon_y + 5), (icon_x + 18, icon_y + 15), 3)
        
    if is_hovering and mouse_clicked:
        pygame.time.wait(200)
        music_playing = not music_playing
        if music_playing:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

def draw_text_centered(text, y, font, color=WHITE):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(GAME_WIDTH // 2, y))
    screen.blit(text_surface, text_rect)

def draw_hints():
    hint_text = small_font.render("[1] Python Basics  [2] Basic Details  [3] Simulated Trace  [4] Live Key Trace  [5] Full Trace", True, GRAY)
    text_rect = hint_text.get_rect(center=(GAME_WIDTH // 2, 25))
    screen.blit(hint_text, text_rect)

def draw_score():
    score_text = f"Current score: {score}"
    text_surface = small_font.render(score_text, True, WHITE)
    screen.blit(text_surface, (GAME_WIDTH - 200, SCREEN_HEIGHT - 40))

# ============================================================================
# STATE DRAWING FUNCTIONS 
# ============================================================================
def draw_title():
    global state, high_score, score, best_time
    draw_bg("TITLE", DARK_BLUE)
    
    draw_text_centered(f"High Score: {high_score}", 270, text_font, WHITE)
    if best_time > 0:
        draw_text_centered(f"Best Time: {(best_time / FPS):.2f} seconds", 310, text_font, BEIGE)
    else:
        draw_text_centered("Best Time: N/A", 310, text_font, BEIGE)

    if draw_button("START GAME", 250, 410, 300, 60, BLUE, GREEN):
        state = "INSTRUCTIONS"
    if draw_button("QUIT", 250, 490, 300, 60, RED, DARK_GRAY):
        return "QUIT"
    
    return None

def draw_instructions():
    global state
    draw_bg("INSTRUCTIONS", DARK_GRAY)

    if draw_button("BACK", 50, 520, 150, 60, RED, DARK_GRAY):
        state = "TITLE"
    if draw_button("Play", 600, 520, 150, 60, GREEN, DARK_GREEN):
        state = "STRANGE_ROOM"

def draw_strange_room():
    global state
    draw_bg("STRANGE_ROOM", BROWN)

    if draw_button("Examine the Radio", 250, 480, 300, 60, BLUE, GREEN):
        state = "FDR_BROADCAST"

def draw_fdr_broadcast():
    global state
    draw_bg("FDR_BROADCAST", DARK_BLUE)
    
    if not loaded_bgs["FDR_BROADCAST"]:
        pygame.draw.rect(screen, BROWN, (300, 60, 200, 150))
        pygame.draw.rect(screen, BEIGE, (300, 60, 200, 150), 5)

    if draw_button("Investigate Further", 250, 500, 300, 60, GREEN, DARK_GREEN):
        state = "CHALLENGE1"

def draw_challenge1():
    global state, score, challenge1_answered
    draw_bg("CHALLENGE1", DARK_GRAY)

    if challenge1_answered:
        draw_text_centered(f"CORRECT! +{POINTS_PER_CHALLENGE} Key fragments", 500, text_font, GREEN)
        if draw_button("Continue", 300, 530, 200, 60, BLUE, GREEN):
            state = "SYSTEM_GLITCH"
        return

    button_y = 200
    for i, option in enumerate(CONTENT["challenge1_options"]):
        if draw_button(option, 200, button_y + i * 90, 400, 70, BLUE, GREEN):
            if i == CONTENT["challenge1_correct"]:
                score += POINTS_PER_CHALLENGE
                challenge1_answered = True
            else:
                draw_text_centered(f"Wrong! -{PENALTY_POINTS} Key fragments.", 500, text_font, RED)
                pygame.display.flip()
                pygame.time.wait(1000)
                score -= PENALTY_POINTS
                if score < 0:
                    score = 0 
                    state = "END"
                return

def draw_system_glitch():
    global state
    draw_bg("SYSTEM_GLITCH", BLACK)
    
    if not loaded_bgs["SYSTEM_GLITCH"]:
        for i in range(5):
            x = (i * 160) % GAME_WIDTH
            pygame.draw.rect(screen, (100, 0, 150), (x, 0, 80, SCREEN_HEIGHT), 2)
    draw_text_centered("SYSTEM GLITCH DETECTED", 50, heading_font, RED)

    if draw_button("Look Around", 250, 500, 300, 60, BLUE, GREEN):
        state = "FACTORY_WORKER"

def draw_factory_worker():
    global state
    draw_bg("FACTORY_WORKER", DARK_GRAY)
    
    if not loaded_bgs["FACTORY_WORKER"]:
        pygame.draw.rect(screen, BEIGE, (350, 50, 100, 50))
        pygame.draw.rect(screen, BLUE, (325, 100, 150, 120))

    if draw_button("Continue On", 250, 500, 300, 60, GREEN, DARK_GREEN):
        state = "CHALLENGE2"

def draw_challenge2():
    global state, score, challenge2_answered, selected_order
    draw_bg("CHALLENGE2", DARK_BLUE)

    if challenge2_answered:
        draw_text_centered(f"PERFECT ORDER! +{POINTS_PER_CHALLENGE} Key fragments", 500, text_font, GREEN)
        if draw_button("Continue", 300, 530, 200, 60, BLUE, GREEN):
            state = "COMMAND_POST"
        return

    if selected_order:
        order_text = "Your order: " + " → ".join([str(i+1) for i in selected_order])
        draw_text_centered(order_text, 130, small_font, BEIGE)

    for i, event in enumerate(CONTENT["challenge2_events"]):
        color = DARK_GRAY if i in selected_order else BLUE
        hover = DARK_GRAY if i in selected_order else GREEN

        if draw_button(event, 150, 200 + i * 85, 500, 70, color, hover):
            if i not in selected_order:
                selected_order.append(i)
                if len(selected_order) == 4:
                    if selected_order == [0, 1, 2, 3]:
                        score += POINTS_PER_CHALLENGE
                        challenge2_answered = True
                    else:
                        draw_text_centered(f"WRONG ORDER! -{PENALTY_POINTS} Key fragments.", 550, text_font, RED)
                        pygame.display.flip()
                        pygame.time.wait(1500)
                        score -= PENALTY_POINTS
                        if score < 0: 
                            score = 0 
                            state = "END"
                        selected_order = []

    if selected_order and not challenge2_answered:
        if draw_button("Reset", 300, 530, 200, 60, RED, DARK_GRAY):
            selected_order = []

def draw_command_post():
    global state
    draw_bg("COMMAND_POST", DARK_GRAY)

    if draw_button("Approach the Commander", 250, 500, 300, 60, BLUE, GREEN):
        state = "ROBERT_OPPENHEIMER"

def draw_robert_oppenheimer():
    global state
    draw_bg("ROBERT_OPPENHEIMER", DARK_BLUE)
    
    if not loaded_bgs["ROBERT_OPPENHEIMER"]:
        pygame.draw.rect(screen, BEIGE, (350, 80, 100, 50))
        pygame.draw.rect(screen, BROWN, (325, 130, 150, 120))

    if draw_button("Answer the Question", 250, 500, 300, 60, GREEN, DARK_GREEN):
        state = "CHALLENGE3"

def draw_challenge3():
    global state, score, challenge3_answered
    draw_bg("CHALLENGE3", DARK_GRAY)

    if challenge3_answered:
        draw_text_centered(f"CORRECT! +{POINTS_PER_CHALLENGE} Key fragments", 500, text_font, GREEN)
        if draw_button("Continue", 300, 530, 200, 60, BLUE, GREEN):
            state = "SIMULATION_BREACH"
        return

    for i, option in enumerate(CONTENT["challenge3_options"]):
        if draw_button(option, 200, 200 + i * 90, 400, 70, BLUE, GREEN):
            if i == CONTENT["challenge3_correct"]:
                score += POINTS_PER_CHALLENGE
                challenge3_answered = True
            else:
                draw_text_centered(f"Wrong! -{PENALTY_POINTS} Key fragments.", 500, text_font, RED)
                pygame.display.flip()
                pygame.time.wait(1000)
                score -= PENALTY_POINTS
                if score < 0: 
                    score = 0 
                    state = "END"
                return

def draw_simulation_breach():
    global state
    draw_bg("SIMULATION_BREACH", BLACK)
    
    if not loaded_bgs["SIMULATION_BREACH"]:
        for i in range(0, GAME_WIDTH, 40):
            pygame.draw.line(screen, GREEN, (i, 0), (i, SCREEN_HEIGHT), 2)
    draw_text_centered("SIMULATION BREACH", 130, heading_font, RED)

    if draw_button("Find the Analyst", 250, 500, 300, 60, GREEN, DARK_GREEN):
        state = "GOVERNMENT_CODE_ANALYST"

def draw_government_code_analyst():
    global state
    draw_bg("GOVERNMENT_CODE_ANALYST", DARK_GRAY)
    
    if not loaded_bgs["GOVERNMENT_CODE_ANALYST"]:
        pygame.draw.rect(screen, BEIGE, (350, 80, 100, 50))
        pygame.draw.rect(screen, DARK_GREEN, (325, 130, 150, 120))
    draw_text_centered("A code lock appears on the wall.", 245, small_font, WHITE)

    if draw_button("Approach the Lock", 250, 500, 300, 60, GREEN, DARK_GREEN):
        state = "CHALLENGE4"

def draw_challenge4():
    global state, score, challenge4_answered
    draw_bg("CHALLENGE4", DARK_BLUE)

    if challenge4_answered:
        draw_text_centered(f"CODE ACCEPTED! +{POINTS_PER_CHALLENGE} Key fragments", 500, text_font, GREEN)
        if draw_button("Continue", 300, 530, 200, 60, BLUE, GREEN):
            state = "FINAL_DOOR"
        return

    positions = [(180, 230, 200, 80), (420, 230, 200, 80), 
                 (180, 340, 200, 80), (420, 340, 200, 80)]

    for i, option in enumerate(CONTENT["challenge4_options"]):
        x, y, w, h = positions[i]
        if draw_button(str(option), x, y, w, h, BLUE, GREEN):
            if i == CONTENT["challenge4_correct"]:
                score += POINTS_PER_CHALLENGE
                challenge4_answered = True
            else:
                draw_text_centered(f"INCORRECT CODE! -{PENALTY_POINTS} Key fragments.", 520, text_font, RED)
                pygame.display.flip()
                pygame.time.wait(1000)
                score -= PENALTY_POINTS
                if score < 0: 
                    score = 0 
                    state = "END"

def draw_final_door():
    global state
    
    if not loaded_bgs["FINAL_DOOR"]:
        pygame.draw.rect(screen, BROWN, (300, 150, 200, 300))
        pygame.draw.rect(screen, BEIGE, (300, 150, 200, 300), 5)
        pygame.draw.circle(screen, WHITE, (470, 300), 10)

    if score >= ESCAPE_SCORE_REQUIRED:
        draw_bg("FINAL_DOOR", BLACK)
        if draw_button("Enter the Door", 250, 500, 300, 60, GREEN, DARK_GREEN):
            state = "TIME_TRAVELER"
    else:
        draw_bg("NOT_ENOUGH_POINTS", BLACK)
        if draw_button("Try Again", 250, 500, 300, 60, RED, DARK_GRAY):
            reset_game()
            state = "TITLE"

def draw_time_traveler():
    global state
    draw_bg("TIME_TRAVELER", BLUE)

    if draw_button("Accept the Gift", 250, 530, 300, 60, GREEN, DARK_GREEN):
        state = "END"

def draw_end():
    global state

    if score >= ESCAPE_SCORE_REQUIRED:
        draw_bg("END", DARK_GREEN if score >= ESCAPE_SCORE_REQUIRED else DARK_GRAY)
        draw_text_centered(CONTENT.get("end_success", "YOU ESCAPED THE TIMELINE!"), 100, title_font, BEIGE)
        draw_text_centered("CONGRATULATIONS!", 180, heading_font, WHITE)
    else:
        draw_bg("FAIL", DARK_GREEN if score >= ESCAPE_SCORE_REQUIRED else DARK_GRAY)
        draw_text_centered(CONTENT.get("end_failure", "TRAPPED IN 1940 FOREVER..."), 100, title_font, RED)
        draw_text_centered("Better luck next time!", 180, heading_font, WHITE)

    draw_text_centered(f"Final Score: {score} / 300", 260, heading_font, WHITE)
    draw_text_centered(f"High Score: {high_score}", 320, text_font, BEIGE)

    time_seconds = final_time / FPS if final_time > 0 else 0.0
    draw_text_centered(f"Time: {time_seconds:.2f} seconds", 365, text_font, WHITE)

    if best_time > 0:
        draw_text_centered(f"Best Time: {(best_time / FPS):.2f} seconds", 400, text_font, BEIGE)
    else:
        draw_text_centered("Best Time: N/A", 400, text_font, BEIGE)

    save_high_score()
    save_best_time()

    if draw_button("Play Again", 200, 440, 400, 60, BLUE, GREEN):
        reset_game()
        state = "TITLE"
    if draw_button("Quit", 200, 520, 400, 60, RED, DARK_GRAY):
        return "QUIT"
    return None

def reset_game():
    global score, challenge1_answered, challenge2_answered, challenge3_answered
    global challenge4_answered, selected_order, timer, final_time
    score = 0
    challenge1_answered = False
    challenge2_answered = False
    challenge3_answered = False
    challenge4_answered = False
    selected_order = []
    timer = 0
    final_time = 0

# ============================================================================
# TECH & SUPER DEBUG MODES RENDERING
# ============================================================================

def render_wrapped_text(surface, text, font, color, x, y, max_width):
    words = text.split(' ')
    space_width = font.size(' ')[0]
    current_x = x
    
    for word in words:
        word_width = font.size(word)[0]
        if current_x + word_width >= x + max_width:
            current_x = x
            y += 18 
        surface.blit(font.render(word, True, color), (current_x, y))
        current_x += word_width + space_width
        
    return y + 18

def get_state_function_and_key(current_state):
    state_data = {
        "TITLE": ("draw_title", "title"),
        "INSTRUCTIONS": ("draw_instructions", "instructions"),
        "STRANGE_ROOM": ("draw_strange_room", "strange_room_text"),
        "FDR_BROADCAST": ("draw_fdr_broadcast", "fdr_broadcast_text"),
        "CHALLENGE1": ("draw_challenge1", "challenge1_options"),
        "SYSTEM_GLITCH": ("draw_system_glitch", "system_glitch_text"),
        "FACTORY_WORKER": ("draw_factory_worker", "factory_worker_text"),
        "CHALLENGE2": ("draw_challenge2", "challenge2_events"),
        "COMMAND_POST": ("draw_command_post", "command_post_text"),
        "ROBERT_OPPENHEIMER": ("draw_robert_oppenheimer", "robert_oppenheimer_text"),
        "CHALLENGE3": ("draw_challenge3", "challenge3_options"),
        "SIMULATION_BREACH": ("draw_simulation_breach", "simulation_breach_text"),
        "GOVERNMENT_CODE_ANALYST": ("draw_government_code_analyst", "government_code_analyst_text"),
        "CHALLENGE4": ("draw_challenge4", "challenge4_options"),
        "FINAL_DOOR": ("draw_final_door", "final_door_success"), 
        "TIME_TRAVELER": ("draw_time_traveler", "time_traveler_text"),
        "END": ("draw_end", "end_success")
    }
    return state_data.get(current_state, ("draw_scene", "scene_text"))

def generate_key_pdb_trace(current_state):
    func_name, content_key = get_state_function_and_key(current_state)

    primary_buttons = {
        "TITLE": "START GAME",
        "INSTRUCTIONS": "Play",
        "STRANGE_ROOM": "Examine the Radio",
        "FDR_BROADCAST": "Investigate Further",
        "SYSTEM_GLITCH": "Look Around",
        "FACTORY_WORKER": "Continue On",
        "COMMAND_POST": "Approach the Commander",
        "ROBERT_OPPENHEIMER": "Answer the Question",
        "SIMULATION_BREACH": "Find the Analyst",
        "GOVERNMENT_CODE_ANALYST": "Approach the Lock",
        "TIME_TRAVELER": "Accept the Gift",
        "END": "Play Again"
    }

    lines = [
        f"> {CURRENT_FILE}(main)",
        f"-> elif state == '{current_state}':",
        "(Pdb) n",
        f"> {CURRENT_FILE}(main)",
        f"-> {func_name}()",
        "(Pdb) s",
        f"--Call--",
        f"> {CURRENT_FILE}({func_name})",
        f"-> draw_bg('{current_state}', fallback_color)",
        "(Pdb) n"
    ]

    if current_state == "INSTRUCTIONS":
        lines.extend([
            f"> {CURRENT_FILE}({func_name})",
            f"-> if draw_button('BACK'):",
            "(Pdb) n",
            f"> {CURRENT_FILE}({func_name})",
            f"-> if draw_button('Play'):",
            "(Pdb) p state",
            f"'{current_state}'",
            "(Pdb) _"
        ])
    elif current_state == "FINAL_DOOR":
        lines.extend([
            f"> {CURRENT_FILE}({func_name})",
            f"-> if score >= ESCAPE_SCORE_REQUIRED:",
            "(Pdb) p score",
            f"{score}",
            "(Pdb) n",
            f"> {CURRENT_FILE}({func_name})",
            f"-> if draw_button('Enter the Door'):" if score >= ESCAPE_SCORE_REQUIRED else f"-> if draw_button('Try Again'):",
            "(Pdb) _"
        ])
    elif "CHALLENGE" in current_state:
        content_key = f"{current_state.lower()}_options" if current_state != "CHALLENGE2" else "challenge2_events"
        lines.extend([
            f"> {CURRENT_FILE}({func_name})",
            f"-> for i, option in enumerate(CONTENT['{content_key}']):",
            "(Pdb) p CONTENT['{content_key}']",
            f"{CONTENT.get(content_key, [])}", 
            "(Pdb) n",
            f"> {CURRENT_FILE}({func_name})",
            f"-> if draw_button(option):",
            "(Pdb) p score",
            f"{score}",
            "(Pdb) n"
        ])
    else:
        btn_name = primary_buttons.get(current_state, "Continue")
        lines.extend([
            f"> {CURRENT_FILE}({func_name})",
            f"-> if draw_button('{btn_name}'):",
            "(Pdb) p state",
            f"'{current_state}'",
            "(Pdb) _"
        ])
    return lines

def draw_side_panel():
    global panel_scroll_y
    if panel_mode is None:
        return

    panel_rect = pygame.Rect(GAME_WIDTH, 0, TECH_WIDTH, SCREEN_HEIGHT)
    x_offset = GAME_WIDTH + 15
    fixed_y = 20

    # ================== MODE 1: PYTHON BASICS ==================
    if panel_mode == "PYTHON_BASICS":
        pygame.draw.rect(screen, TECH_BG, panel_rect)
        pygame.draw.line(screen, TECH_GREEN, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)

        screen.blit(tech_font_bold.render("[ 1 ] Python Basics", True, TECH_RED), (x_offset, fixed_y))
        fixed_y += 40
        
        clip_rect = pygame.Rect(GAME_WIDTH, fixed_y, TECH_WIDTH, SCREEN_HEIGHT - fixed_y)
        screen.set_clip(clip_rect)
        y_offset = fixed_y + panel_scroll_y

        for line in PYTHON_BASICS_TEXT:
            if line in PB_HEADERS: 
                y_offset += 10
                y_offset = render_wrapped_text(screen, line, tech_font_bold, TECH_GREEN, x_offset + 5, y_offset, TECH_WIDTH - 30)
            else:
                y_offset = render_wrapped_text(screen, line, tech_font_normal, GRAY, x_offset + 10, y_offset, TECH_WIDTH - 30)

    # ================== MODE 2: BASIC DETAILS ==================
    elif panel_mode == "BASIC_DETAILS":
        pygame.draw.rect(screen, TECH_BG, panel_rect)
        pygame.draw.line(screen, TECH_GREEN, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)

        screen.blit(tech_font_bold.render("[ 2 ] Basic Details", True, TECH_RED), (x_offset, fixed_y))
        fixed_y += 40

        clip_rect = pygame.Rect(GAME_WIDTH, fixed_y, TECH_WIDTH, SCREEN_HEIGHT - fixed_y)
        screen.set_clip(clip_rect)
        y_offset = fixed_y + panel_scroll_y
        
        if state == "TITLE":
            screen.blit(tech_font_bold.render("[ SYSTEM IMPORTS ]", True, TECH_GREEN), (x_offset, y_offset))
            y_offset += 20
            y_offset = render_wrapped_text(screen, "-> import pygame, sys, json, os, linecache", tech_font_normal, GRAY, x_offset + 10, y_offset, TECH_WIDTH - 30)
            y_offset += 15

        screen.blit(tech_font_bold.render("[ GAME TIMING ALGORITHM ]", True, TECH_GREEN), (x_offset, y_offset))
        y_offset += 25
        y_offset = render_wrapped_text(screen, "-> Loop runs 60 times/sec (FPS). Timer adds +1 per frame.", tech_font_normal, GRAY, x_offset + 10, y_offset, TECH_WIDTH - 30)
        y_offset = render_wrapped_text(screen, "-> Elapsed Seconds = Timer / 60.", tech_font_normal, GRAY, x_offset + 10, y_offset, TECH_WIDTH - 30)
        y_offset += 15

        screen.blit(tech_font_bold.render(f"[ PAGE LOGIC FLOW: {state} ]", True, TECH_GREEN), (x_offset, y_offset))
        y_offset += 25
        for line in LOGIC_PATH_TRACE.get(state, DEFAULT_LOGIC_PATH):
            y_offset = render_wrapped_text(screen, line, tech_font_normal, (200, 255, 200), x_offset + 10, y_offset, TECH_WIDTH - 30)
        y_offset += 15

        screen.blit(tech_font_bold.render("[ LIVE MEMORY MAP ]", True, TECH_GREEN), (x_offset, y_offset))
        y_offset += 25
        variables = [("score", score), ("state", state)]
        if state == "CHALLENGE2": variables.append(("selected_order", str(selected_order)))
        for name, val in variables:
            screen.blit(tech_font_bold.render(f"VAR '{name}': {val}", True, WHITE), (x_offset + 10, y_offset))
            y_offset += 18
            y_offset = render_wrapped_text(screen, f"ADDR: {hex(id(val))}", tech_font_normal, GRAY, x_offset + 10, y_offset, TECH_WIDTH - 30)
            y_offset += 7 

        y_offset += 15
        screen.blit(tech_font_bold.render("[ SOURCE CODE LAYOUT ]", True, TECH_GREEN), (x_offset, y_offset))
        y_offset += 25
        for line in CODE_LAYOUT_TEXT:
            color = TECH_YELLOW if not line.startswith(" -") else GRAY
            y_offset = render_wrapped_text(screen, line, tech_font_normal, color, x_offset + 10, y_offset, TECH_WIDTH - 30)

    # ================== MODE 3: SIMULATED TRACE ==================
    elif panel_mode == "SIMULATED_TRACE":
        pygame.draw.rect(screen, BLACK, panel_rect)
        pygame.draw.line(screen, DARK_GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)
        
        screen.blit(tech_font_bold.render("[ 3 ] Simulated Trace", True, TECH_RED), (x_offset, fixed_y))
        fixed_y += 40

        clip_rect = pygame.Rect(GAME_WIDTH, fixed_y, TECH_WIDTH, SCREEN_HEIGHT - fixed_y)
        screen.set_clip(clip_rect)
        y_offset = fixed_y + panel_scroll_y

        screen.blit(tech_font_bold.render("[ SIMULATED PDB CONTEXT ]", True, TECH_GREEN), (x_offset, y_offset))
        y_offset += 25
        y_offset = render_wrapped_text(screen, "Note: Real 'pdb' physically halts the Python thread to await terminal input. In a UI/Game environment, halting the thread freezes the 60 FPS event loop, causing a crash. This educational view safely simulates a trace.", tech_font_normal, GRAY, x_offset + 10, y_offset, TECH_WIDTH - 30)
        y_offset += 18
        
        screen.blit(tech_font_bold.render("[ TERMINAL TRACE ]", True, TECH_GREEN), (x_offset, y_offset))
        y_offset += 25
        y_offset = render_wrapped_text(screen, f"mac1 ~ % python3 -m pdb {CURRENT_FILE}", tech_font_bold, WHITE, x_offset + 10, y_offset, TECH_WIDTH - 30)
        y_offset += 12

        for line in generate_key_pdb_trace(state):
            color = TECH_GREEN 
            if line.startswith(">"): color = TECH_BLUE
            elif line.startswith("(Pdb)"): color = TECH_YELLOW
            elif line.startswith("--"): color = TECH_PURPLE
            elif line.startswith("'") or line.startswith("["): color = WHITE
            y_offset = render_wrapped_text(screen, line, tech_font_normal, color, x_offset + 10, y_offset, TECH_WIDTH - 30)

    # ================== MODE 4: LIVE 'KEY' TRACES ==================
    elif panel_mode == "LIVE_KEY_TRACE":
        pygame.draw.rect(screen, BLACK, panel_rect)
        pygame.draw.line(screen, TECH_RED, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)
        
        screen.blit(tech_font_bold.render("[ 4 ] Live 'Key' Traces", True, TECH_RED), (x_offset, fixed_y))
        fixed_y += 25
        fixed_y = render_wrapped_text(screen, "Note: Scene changes track globally. Code execution only traces while this panel is open to save CPU.", tech_font_tiny, GRAY, x_offset, fixed_y, TECH_WIDTH - 15)
        fixed_y += 10

        clip_rect = pygame.Rect(GAME_WIDTH, fixed_y, TECH_WIDTH, SCREEN_HEIGHT - fixed_y)
        screen.set_clip(clip_rect)
        
        max_lines = 18 
        total_lines = len(key_trace_log)
        max_scroll = max(0, total_lines - max_lines)
        
        line_offset = abs(panel_scroll_y) // 25
        line_offset = min(line_offset, max_scroll)
        
        if abs(panel_scroll_y) > max_scroll * 25:
            panel_scroll_y = -(max_scroll * 25)
            
        start_idx = max(0, total_lines - max_lines - line_offset)
        end_idx = start_idx + max_lines
        display_log = key_trace_log[start_idx:end_idx]

        y_offset = fixed_y
        for line in display_log:
            color = TECH_GREEN
            if "ENTERED SCENE" in line: color = TECH_YELLOW
            y_offset = render_wrapped_text(screen, line, tech_font_normal, color, x_offset + 10, y_offset, TECH_WIDTH - 30)

        if max_scroll > 0:
            track_rect = pygame.Rect(GAME_WIDTH + TECH_WIDTH - 12, fixed_y, 4, SCREEN_HEIGHT - fixed_y - 10)
            pygame.draw.rect(screen, DARK_GRAY, track_rect)
            scroll_percent = line_offset / max_scroll
            handle_height = max(30, track_rect.height * (max_lines / total_lines))
            handle_y = fixed_y + (1.0 - scroll_percent) * (track_rect.height - handle_height)
            pygame.draw.rect(screen, GRAY, (GAME_WIDTH + TECH_WIDTH - 14, handle_y, 8, handle_height), border_radius=4)


    # ================== MODE 5: LIVE FULL TRACE ==================
    elif panel_mode == "LIVE_FULL_TRACE":
        pygame.draw.rect(screen, BLACK, panel_rect)
        pygame.draw.line(screen, TECH_RED, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)
        
        screen.blit(tech_font_bold.render("[ 5 ] Live Full Trace", True, TECH_RED), (x_offset, fixed_y))
        fixed_y += 25
        fixed_y = render_wrapped_text(screen, "Note: Code execution only traces while this panel is open. UI drawing is filtered to prevent crashes.", tech_font_tiny, GRAY, x_offset, fixed_y, TECH_WIDTH - 15)
        fixed_y += 10

        clip_rect = pygame.Rect(GAME_WIDTH, fixed_y, TECH_WIDTH, SCREEN_HEIGHT - fixed_y)
        screen.set_clip(clip_rect)
        
        max_lines = 18
        total_lines = len(full_trace_log)
        max_scroll = max(0, total_lines - max_lines)
        
        line_offset = abs(panel_scroll_y) // 25
        line_offset = min(line_offset, max_scroll)
        
        if abs(panel_scroll_y) > max_scroll * 25:
            panel_scroll_y = -(max_scroll * 25)
            
        start_idx = max(0, total_lines - max_lines - line_offset)
        end_idx = start_idx + max_lines
        display_log = full_trace_log[start_idx:end_idx]

        y_offset = fixed_y
        for line in display_log:
            color = TECH_GREEN
            if "ENTERED SCENE" in line: color = TECH_YELLOW
            y_offset = render_wrapped_text(screen, line, tech_font_normal, color, x_offset + 10, y_offset, TECH_WIDTH - 30)

        if max_scroll > 0:
            track_rect = pygame.Rect(GAME_WIDTH + TECH_WIDTH - 12, fixed_y, 4, SCREEN_HEIGHT - fixed_y - 10)
            pygame.draw.rect(screen, DARK_GRAY, track_rect)
            scroll_percent = line_offset / max_scroll
            handle_height = max(30, track_rect.height * (max_lines / total_lines))
            handle_y = fixed_y + (1.0 - scroll_percent) * (track_rect.height - handle_height)
            pygame.draw.rect(screen, GRAY, (GAME_WIDTH + TECH_WIDTH - 14, handle_y, 8, handle_height), border_radius=4)

    screen.set_clip(None)

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

def main():
    global state, previous_state, score, timer, final_time, best_time, panel_mode, panel_scroll_y, screen

    load_high_score()
    load_best_time()

    running = True
    while running:
        if state != previous_state:
            sep = f"\n--- ENTERED SCENE: {state} ---"
            if not key_trace_log or key_trace_log[-1] != sep: 
                key_trace_log.append(sep)
                if len(key_trace_log) > 1000: key_trace_log.pop(0)
            if not full_trace_log or full_trace_log[-1] != sep: 
                full_trace_log.append(sep)
                if len(full_trace_log) > 1000: full_trace_log.pop(0)
            previous_state = state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEWHEEL:
                if panel_mode in ["LIVE_KEY_TRACE", "LIVE_FULL_TRACE", "PYTHON_BASICS", "BASIC_DETAILS", "SIMULATED_TRACE"]:
                    panel_scroll_y += event.y * 30 
                    if panel_scroll_y > 0:
                        panel_scroll_y = 0

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    panel_mode = None if panel_mode == "PYTHON_BASICS" else "PYTHON_BASICS"
                    sys.settrace(None); panel_scroll_y = 0 
                elif event.key == pygame.K_2:
                    panel_mode = None if panel_mode == "BASIC_DETAILS" else "BASIC_DETAILS"
                    sys.settrace(None); panel_scroll_y = 0 
                elif event.key == pygame.K_3:
                    panel_mode = None if panel_mode == "SIMULATED_TRACE" else "SIMULATED_TRACE"
                    sys.settrace(None); panel_scroll_y = 0 
                elif event.key == pygame.K_4:
                    panel_mode = None if panel_mode == "LIVE_KEY_TRACE" else "LIVE_KEY_TRACE"
                    panel_scroll_y = 0 
                    sys.settrace(live_system_trace if panel_mode == "LIVE_KEY_TRACE" else None)
                elif event.key == pygame.K_5:
                    panel_mode = None if panel_mode == "LIVE_FULL_TRACE" else "LIVE_FULL_TRACE"
                    panel_scroll_y = 0 
                    sys.settrace(live_system_trace if panel_mode == "LIVE_FULL_TRACE" else None)
                
                screen = pygame.display.set_mode((GAME_WIDTH + TECH_WIDTH if panel_mode else GAME_WIDTH, SCREEN_HEIGHT))

        screen.fill(BLACK)

        if state == "TITLE":
            if draw_title() == "QUIT": running = False
        elif state == "INSTRUCTIONS": draw_instructions()
        elif state == "STRANGE_ROOM": draw_strange_room()
        elif state == "FDR_BROADCAST": draw_fdr_broadcast()
        elif state == "CHALLENGE1": draw_challenge1()
        elif state == "SYSTEM_GLITCH": draw_system_glitch()
        elif state == "FACTORY_WORKER": draw_factory_worker()
        elif state == "CHALLENGE2": draw_challenge2()
        elif state == "COMMAND_POST": draw_command_post()
        elif state == "ROBERT_OPPENHEIMER": draw_robert_oppenheimer()
        elif state == "CHALLENGE3": draw_challenge3()
        elif state == "SIMULATION_BREACH": draw_simulation_breach()
        elif state == "GOVERNMENT_CODE_ANALYST": draw_government_code_analyst()
        elif state == "CHALLENGE4": draw_challenge4()
        elif state == "FINAL_DOOR": draw_final_door()   
        elif state == "TIME_TRAVELER": draw_time_traveler()
        elif state == "END":
            if final_time == 0:
                final_time = timer
                save_best_time()
                save_high_score()
            if draw_end() == "QUIT": running = False

        draw_hints()
        draw_music_icon()
        if state not in ["TITLE", "INSTRUCTIONS", "END"]:
            draw_score()

        draw_side_panel()

        if state != "END":
            timer += 1

        pygame.display.flip()
        clock.tick(FPS)

    sys.settrace(None)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

