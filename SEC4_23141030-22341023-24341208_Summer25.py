from math import *
from random import *
from time import time as current_time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

car_position = [0.0, 0.0, 0.0]
road_left = -3.0
road_right = 3.0
lane_width = 2.0
lanes = [-lane_width, 0.0, lane_width]
speed = 5.0
boost_speed = 10.0
boost_time = 0.0
boost_duration = 2.0
boosts_left = 10
obstacles = []
obstacle_gen_time = current_time()
game_over = False
paused = False
game_started = False
score = 0
start_time = current_time()
camera_mode = 'third'
left_pressed = False
right_pressed = False
window_width = 800
window_height = 600
tree_positions = []
sky_state = 0
sky_colors = [
    (0.53, 0.81, 0.92),  # Day
    (1.0, 0.5, 0.0),     # Sunrise
    (0.8, 0.3, 0.5)      # Sunset
]
cheat_mode = False  # Cheat mode flag

last_frame_time = current_time()  # for delta time


def init():
    glEnable(GL_DEPTH_TEST)
    generate_trees()


def draw_text(text, x, y):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def draw_car():
    glColor3f(0.0, 0.0, 1.0)
    glPushMatrix()
    glTranslatef(0, 0.25, 0)
    glScalef(1.0, 0.5, 2.0)
    glutSolidCube(1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0.75, 0)
    glScalef(0.8, 0.5, 1.0)
    glutSolidCube(1)
    glPopMatrix()
    # Wheels
    glColor3f(0.0, 0.0, 0.0)
    wheel_radius = 0.25
    wheel_pos = [[0.5, 0.25, 0.75], [0.5, 0.25, -0.75],
                 [-0.5, 0.25, 0.75], [-0.5, 0.25, -0.75]]
    for pos in wheel_pos:
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        glutSolidSphere(wheel_radius, 10, 10)
        glPopMatrix()


def draw_barricade():
    glColor3f(1.0, 0.6, 0.0)
    glPushMatrix()
    glTranslatef(0.0, 0.25, 0.0)
    glScalef(1.0, 0.5, 0.5)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(0.0, 0.25, 0.0)
    glScalef(1.0, 0.1, 0.5)
    glutSolidCube(1)
    glPopMatrix()


def draw_street_lines():
    glColor3f(1.0, 1.0, 1.0)
    line_width = 0.05
    dash_length = 2.0
    gap_length = 2.0
    start_z = int(car_position[2] - 50)
    end_z = int(car_position[2] + 200)
    separators = [-lane_width / 2, lane_width / 2]
    for x in separators:
        z = start_z
        while z < end_z:
            glBegin(GL_QUADS)
            glVertex3f(x - line_width / 2, 0.01, z)
            glVertex3f(x + line_width / 2, 0.01, z)
            glVertex3f(x + line_width / 2, 0.01, z + dash_length)
            glVertex3f(x - line_width / 2, 0.01, z + dash_length)
            glEnd()
            z += dash_length + gap_length


def generate_trees():
    global tree_positions
    tree_positions.clear()
    start_z = -50
    end_z = 1000
    left_x = -6
    right_x = 6
    z = start_z
    while z < end_z:
        spacing = uniform(15, 25)
        height = uniform(1.0, 2.0)
        width = uniform(0.3, 0.5)
        tree_positions.append((left_x, z, width, height))
        tree_positions.append((right_x, z, width, height))
        z += spacing


def draw_tree(x, z, width=0.3, height=1.5):
    trunk_height = height * 0.4
    leaves_height = height * 0.6
    # Trunk
    glColor3f(0.55, 0.27, 0.07)
    glPushMatrix()
    glTranslatef(x, trunk_height / 2, z)
    glScalef(width, trunk_height, width)
    glutSolidCube(1)
    glPopMatrix()
    # Leaves
    glColor3f(0.0, 0.6, 0.0)
    glPushMatrix()
    glTranslatef(x, trunk_height + leaves_height / 2, z)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(width * 2, leaves_height, 10, 10)
    glPopMatrix()


def draw_trees():
    for x, z, width, height in tree_positions:
        if car_position[2] - 50 < z < car_position[2] + 200:
            draw_tree(x, z, width, height)


def draw_environment():
    road_width = 8.0
    extend_z = 1000.0
    # Grass left
    glColor3f(0.0, 0.5, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-50.0, 0.0, -extend_z)
    glVertex3f(-road_width / 2, 0.0, -extend_z)
    glVertex3f(-road_width / 2, 0.0, extend_z)
    glVertex3f(-50.0, 0.0, extend_z)
    glEnd()
    # Grass right
    glBegin(GL_QUADS)
    glVertex3f(road_width / 2, 0.0, -extend_z)
    glVertex3f(50.0, 0.0, -extend_z)
    glVertex3f(50.0, 0.0, extend_z)
    glVertex3f(road_width / 2, 0.0, extend_z)
    glEnd()
    # Rails
    glColor3f(0.6, 0.6, 0.6)
    rail_height = 0.2
    rail_width = 0.2
    glBegin(GL_QUADS)
    glVertex3f(-road_width / 2, 0.0, -extend_z)
    glVertex3f(-road_width / 2 + rail_width, 0.0, -extend_z)
    glVertex3f(-road_width / 2 + rail_width, rail_height, extend_z)
    glVertex3f(-road_width / 2, rail_height, extend_z)
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(road_width / 2 - rail_width, 0.0, -extend_z)
    glVertex3f(road_width / 2, 0.0, -extend_z)
    glVertex3f(road_width / 2, rail_height, extend_z)
    glVertex3f(road_width / 2 - rail_width, rail_height, extend_z)
    glEnd()
    # Sky
    glColor3f(*sky_colors[sky_state])
    glBegin(GL_QUADS)
    glVertex3f(-50.0, 0.0, -extend_z)
    glVertex3f(50.0, 0.0, -extend_z)
    glVertex3f(50.0, 50.0, -extend_z)
    glVertex3f(-50.0, 50.0, -extend_z)
    glEnd()


def display():
    glClearColor(*sky_colors[sky_state], 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Camera
    if camera_mode == 'third':
        gluLookAt(car_position[0], car_position[1] + 2.0, car_position[2] - 5.0,
                  car_position[0], car_position[1], car_position[2] + 10.0,
                  0.0, 1.0, 0.0)
    else:
        gluLookAt(car_position[0], car_position[1] + 1.0, car_position[2],
                  car_position[0], car_position[1] + 1.0, car_position[2] + 10.0,
                  0.0, 1.0, 0.0)

    draw_environment()
    draw_trees()

    # Road
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-4.0, 0.0, -1000.0)
    glVertex3f(4.0, 0.0, -1000.0)
    glVertex3f(4.0, 0.0, 1000.0)
    glVertex3f(-4.0, 0.0, 1000.0)
    glEnd()

    draw_street_lines()

    if game_started:
        if camera_mode == 'third':
            glPushMatrix()
            glTranslatef(car_position[0], car_position[1], car_position[2])
            draw_car()
            glPopMatrix()
        for obs in obstacles:
            glPushMatrix()
            glTranslatef(obs[0], obs[1], obs[2])
            draw_barricade()
            glPopMatrix()

    # 2D overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0)

    if not game_started:
        text = "PRESS S TO START"
        draw_text(text, (window_width - len(text) * 10) / 2, window_height / 2)
    else:
        draw_text(f"Score: {score}", 10, window_height - 20)
        draw_text(f"Boosts: {boosts_left}", 10, window_height - 40)
        draw_text(f"Cheat: {'ON' if cheat_mode else 'OFF'}", 10, window_height - 60)
        if game_over:
            text = "Game Over! Press R to restart"
            draw_text(text, (window_width - len(text) * 10) / 2, window_height / 2)
        elif paused:
            text = "PAUSED - Press P to resume"
            draw_text(text, (window_width - len(text) * 10) / 2, window_height / 2)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()


def update():
    global car_position, boost_time, game_over, score, obstacle_gen_time, boosts_left, obstacles
    global last_frame_time

    now = current_time()
    dt = now - last_frame_time
    last_frame_time = now

    if game_started and not game_over and not paused:
        current_speed = boost_speed if boost_time > 0 else speed
        car_position[2] += current_speed * dt

        # Player movement
        if left_pressed:
            car_position[0] -= 5.0 * dt
        if right_pressed:
            car_position[0] += 5.0 * dt
        if boost_time > 0:
            boost_time -= dt

        if cheat_mode:
            target_lane = car_position[0]
            for obs in obstacles:
                if 0 < obs[2] - car_position[2] < 10.0:
                    if abs(obs[0] - car_position[0]) < 1.0:
                        for lane in lanes:
                            if lane != car_position[0]:
                                lane_safe = True
                                for o in obstacles:
                                    if 0 < o[2] - car_position[2] < 10.0 and o[0] == lane:
                                        lane_safe = False
                                        break
                                if lane_safe:
                                    target_lane = lane
                                    break
                        break
            lane_diff = target_lane - car_position[0]
            move_amount = 5.0 * dt
            if abs(lane_diff) < move_amount:
                car_position[0] = target_lane
            else:
                car_position[0] += move_amount if lane_diff > 0 else -move_amount

        # Obstacles generation
        if current_time() - obstacle_gen_time > uniform(1.0, 3.0):
            num_obs = randint(1, 2)
            chosen_lanes = sample(lanes, num_obs)
            obs_z = car_position[2] + 50.0
            for lane in chosen_lanes:
                obstacles.append([lane, 0.25, obs_z])
            obstacle_gen_time = current_time()

        # Check collisions and remove passed obstacles
        new_obs = []
        for obs in obstacles:
            if not cheat_mode:  # collision check only if cheat off
                if abs(obs[0] - car_position[0]) < 1.0 and abs(obs[2] - car_position[2]) < 1.0:
                    game_over = True
            if obs[2] > car_position[2] - 20.0:
                new_obs.append(obs)
        obstacles = new_obs

        # Road boundaries
        if car_position[0] < road_left or car_position[0] > road_right:
            game_over = True

        # Score
        score = int(current_time() - start_time)

    glutPostRedisplay()


def idle():
    update()


def keyboard_down(key, x, y):
    global left_pressed, right_pressed, camera_mode, boost_time, boosts_left
    global game_over, start_time, score, obstacles, paused, sky_state, game_started, cheat_mode
    if key in [b'd', b'D']:
        left_pressed = True
    elif key in [b'a', b'A']:
        right_pressed = True
    elif key == b'v':
        camera_mode = 'first' if camera_mode == 'third' else 'third'
    elif key == b'w':
        if boosts_left > 0 and boost_time <= 0:
            boost_time = boost_duration
            boosts_left -= 1
    elif key in [b's', b'S']:
        if not game_started:
            game_started = True
            start_time = current_time()
    elif key == b'r' and game_over:
        game_over = False
        start_time = current_time()
        score = 0
        car_position[:] = [0.0, 0.0, 0.0]
        obstacles.clear()
        boosts_left = 10
    elif key == b'p':
        paused = not paused
    elif key in [b'c', b'C']:
        sky_state = (sky_state + 1) % len(sky_colors)
    elif key in [b'm', b'M']:
        cheat_mode = not cheat_mode


def keyboard_up(key, x, y):
    global left_pressed, right_pressed
    if key in [b'd', b'D']:
        left_pressed = False
    elif key in [b'a', b'A']:
        right_pressed = False


def reshape(w, h):
    global window_width, window_height
    window_width = w
    window_height = h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w/h if h != 0 else 1, 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)


if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Car Game")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutIdleFunc(idle)
    glutMainLoop()
