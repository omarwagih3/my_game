from OpenGL.GL import *
from OpenGL.GLUT import *
import pygame
import pygame.mixer
import sys
import time
import math

# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Texture names for background, left tank, right tank, midwall, poster, and guns
texture_names = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Variable to track whether to display the poster or the game layout
show_poster = True
game_over_1 = False
game_over_2 = False
about_poster_active = False

# Flag to indicate which tank's movement is active
left_tank_active = True

# Flag to indicate the direction of grey rectangle movement
moving_right = True

# Tank positions
left_tank_x = 5
right_tank_x = WINDOW_WIDTH - 215
tank_y = 106
gun_length = 2

# Initialize pygame mixer
pygame.mixer.init()

# Load the sound files
fire_sound = pygame.mixer.Sound("./sounds/boo.wav")
finish_sound = pygame.mixer.Sound("./sounds/click.wav")

# Sound effects
hit_sound = None

# Define the speed of grey rectangle movement
movement_speed = 2.6

# declaring grey rectangle attributes
gray_rect_width = 200  # Width of the gray rectangle
gray_rect_height = 40   # Height of the gray rectangle
gray_rect_x = (WINDOW_WIDTH - gray_rect_width) / 2  # Centering the rectangle horizontally
gray_rect_y = WINDOW_HEIGHT*0.45 + 120  # Positioning the rectangle above the midwall 

# Circle attributes
circle_radius = 5
circle_speed = 0.05
circle_active = False  # Flag to indicate if the circle is active or not

# Initialize bullet position and velocity components
bullet_x = 0
bullet_y = 0
bullet_vx = 0
bullet_vy = 0
GRAVITY = 9.81

# Declaring health bars attributes
left_tank_health_percentage = 1.0  #  health percentage for the left tank
right_tank_health_percentage = 1.0  #  health percentage for the right tank
health_bar_width = 300
health_bar_height = 25
health_bar_offset = 35  # Offset from the top of the window
left_health_bar_x = 20
right_health_bar_x = WINDOW_WIDTH - health_bar_width - 20

# Function to initialize textures
def Texture_init():
    loadTextures()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Function to set up texture parameters
def texture_setup(texture_image_binary, texture_name, width, height):
    glBindTexture(GL_TEXTURE_2D, texture_name)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_image_binary)
    glBindTexture(GL_TEXTURE_2D, -1)

# Function to load textures
def loadTextures():
    glEnable(GL_TEXTURE_2D)
    images = []

    # Load texture images
    images.append(pygame.image.load("./imgs/background.png"))  # Background
    images.append(pygame.image.load("./imgs/left-tank-body.png"))   # Left tank
    images.append(pygame.image.load("./imgs/left-tank-gun.png"))   # Left tank gun
    images.append(pygame.image.load("./imgs/right-tank-body.png"))  # Right tank
    images.append(pygame.image.load("./imgs/right-tank-gun.png"))  # Right tank gun
    images.append(pygame.image.load("./imgs/midwall.png"))     # Midwall
    images.append(pygame.image.load("./imgs/poster.png"))      # Poster_0
    images.append(pygame.image.load("./imgs/game_over_1.png"))      # Poster_1
    images.append(pygame.image.load("./imgs/game_over_2.png"))      # Poster_2
    images.append(pygame.image.load("./imgs/about_poster.png"))      # Poster_2

    # Convert images to raw pixel data
    textures = [pygame.image.tostring(image, "RGBA", True) for image in images]

    # Generate texture names
    glGenTextures(len(images), texture_names)

    # Set up textures
    for i in range(len(images)):
        texture_setup(textures[i], texture_names[i], images[i].get_width(), images[i].get_height())

# Function to draw textured rectangle
def draw_rect_tex(texture_name, left, bottom, right, top):
    glColor(1, 1, 1, 1)
    glBindTexture(GL_TEXTURE_2D, texture_name)
    glBegin(GL_POLYGON)
    glTexCoord(0, 0)
    glVertex2d(left, bottom)
    glTexCoord(1, 0)
    glVertex2d(right, bottom)
    glTexCoord(1, 1)
    glVertex2d(right, top)
    glTexCoord(0, 1)
    glVertex2d(left, top)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, -1)

def draw_health_bar(x, y, width, height, percentage, is_left_bar=True):
    # Calculate the width of the colored portion of the health bar based on the percentage
    color_width = width * percentage
    if is_left_bar:
        # Calculate the x-coordinate where the colored portion should start for the left bar
        color_x = x
    else:
        # Calculate the x-coordinate where the colored portion should start for the right bar
        color_x = x + (width - color_width)

    # Draw the colored portion of the health bar
    glColor3f(1.0, 0.0, 0.0)  # Red color
    glBegin(GL_QUADS)
    glVertex2f(color_x, y)
    glVertex2f(color_x + color_width, y)
    glVertex2f(color_x + color_width, y + height)
    glVertex2f(color_x, y + height)
    glEnd()

    # Draw the background of the health bar
    glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()


# Function to draw a gray rectangle
def draw_gray_rectangle(left, bottom, width, height):
    glColor3f(0.5, 0.5, 0.5)  # Gray color
    glBegin(GL_QUADS)
    glVertex2f(left, bottom)
    glVertex2f(left + width, bottom)
    glVertex2f(left + width, bottom + height)
    glVertex2f(left, bottom + height)
    glEnd()

# Function to display graphics
def display():
    global show_poster, gray_rect_x, bullet_x,bullet_y , bullet_vy, bullet_vx, GRAVITY, moving_right, circle_x, circle_y, circle_radius, hit_sound, circle_active, left_tank_active, left_tank_health_percentage, right_tank_health_percentage, game_over_1, game_over_2,about_poster_active
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Enable alpha testing to discard fragments with low alpha values
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.1)  # Adjust threshold as needed

    # Display poster for 5 seconds
    if show_poster:
        draw_rect_tex(texture_names[6], 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        
    elif game_over_1 or game_over_2:
        if game_over_1:
            draw_rect_tex(texture_names[7], 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # Display game over screen for left tank victory
        else:
            draw_rect_tex(texture_names[8], 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # Display game over screen for right tank victory
    elif about_poster_active:  # Check if about poster is active
        draw_rect_tex(texture_names[9], 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # Display about poster

    else:
        # Display midwall
        draw_rect_tex(texture_names[5], WINDOW_WIDTH*0.45, 109, WINDOW_WIDTH*0.50, WINDOW_HEIGHT*0.36)

        # Display left tank
        draw_rect_tex(texture_names[1], left_tank_x, tank_y, left_tank_x + 205, tank_y + 114)

        # Rotate and display left tank gun
        glPushMatrix()
        gun_start_x = left_tank_x + 160  # X-coordinate of the gun's starting point
        gun_start_y = tank_y + 49  # Y-coordinate of the gun's starting point
        glTranslatef(gun_start_x, gun_start_y, 0)  # Translate to the point of rotation
        glRotatef(left_gun_angle, 0, 0, 1)  # Rotate around Z-axis by gun angle
        glTranslatef(-gun_start_x, -gun_start_y, 0)  # Translate back to original position
        draw_rect_tex(texture_names[2], left_tank_x + 160, tank_y + 49, left_tank_x + 300, tank_y + 60)
        glPopMatrix()

        if circle_active:
            
            # Draw the bullet
            glColor3f(1, 0, 0)  # Red color
            glBegin(GL_POLYGON)
            for i in range(100):
                angle = 2 * math.pi * i / 100
                x = bullet_x + circle_radius * math.cos(angle)
                y = bullet_y + circle_radius * math.sin(angle)
                glVertex2f(x, y)
            glEnd()

            # Update bullet position
            bullet_x += bullet_vx *0.05
            bullet_y += bullet_vy *0.05
            bullet_vy -= GRAVITY * 0.05
            ################################################
            # time_elapsed = time.time() - start_time
            # bullet_x += bullet_vx * time_elapsed
            # bullet_y += bullet_vy * time_elapsed - 0.5 * GRAVITY * time_elapsed ** 2
            # bullet_vy -= GRAVITY * time_elapsed
            

            # Check if the ball hits the other tank
            if not left_tank_active and right_tank_x <= bullet_x <= right_tank_x + 205 \
                and tank_y <= bullet_y <= tank_y + 114:
                right_tank_health_percentage -= 0.1
                if right_tank_health_percentage <= 0.1:
                    print("Left tank wins!")
                    game_over_1 = True
                    hit_sound = finish_sound
                    hit_sound.play()
                hit_sound = fire_sound
                hit_sound.play()
                circle_active = False

            if left_tank_active and left_tank_x <= bullet_x <= left_tank_x + 205 \
                and tank_y <= bullet_y <= tank_y + 114:
                left_tank_health_percentage -= 0.1
                if left_tank_health_percentage <= 0.1:
                    print("right tank wins!")
                    game_over_2 = True
                    hit_sound = finish_sound
                    hit_sound.play()
                hit_sound = fire_sound
                hit_sound.play()
                circle_active = False

            # If the ball reaches the other side without hitting the tank or hits the midwall, deactivate it
            if bullet_x > WINDOW_WIDTH or bullet_x < 0 or (WINDOW_WIDTH * 0.45 <= bullet_x <= WINDOW_WIDTH * 0.50 and
                                               109 <= bullet_y <= WINDOW_HEIGHT * 0.36) or \
                (gray_rect_x <= bullet_x <= gray_rect_x + gray_rect_width and
                gray_rect_y <= bullet_y <= gray_rect_y + gray_rect_height):
                    circle_active = False

        # Draw health bars based on updated percentages
        draw_health_bar(left_health_bar_x, WINDOW_HEIGHT - health_bar_offset, health_bar_width, health_bar_height,
                        left_tank_health_percentage)
        draw_health_bar(right_health_bar_x, WINDOW_HEIGHT - health_bar_offset, health_bar_width, health_bar_height,
                        right_tank_health_percentage)

        # Display right tank
        draw_rect_tex(texture_names[3], right_tank_x, tank_y, right_tank_x + 205, tank_y + 114)

        # Rotate and display right tank gun
        glPushMatrix()
        gun_start_x = right_tank_x + 300  # X-coordinate of the gun's starting point from the right side
        gun_start_y = tank_y + 40  # Y-coordinate of the gun's starting point
        glTranslatef(gun_start_x, gun_start_y, 0)  # Translate to the point of rotation
        glTranslatef(-244, 30, 0)  # Move the gun
        glRotatef(right_gun_angle, 0, 0, 1)  # Rotate around Z-axis by gun angle
        glScalef(-1, 1, 1)  # Flip horizontally
        glTranslatef(-gun_start_x, -gun_start_y, 0)  # Translate back to original position
        draw_rect_tex(texture_names[4], right_tank_x + 161, tank_y + 49, right_tank_x + 300, tank_y + 60)
        glPopMatrix()

        # Update the position of the grey rectangle
        if moving_right:
            gray_rect_x += movement_speed
        else:
            gray_rect_x -= movement_speed

        # Check if the grey rectangle reaches the window's edge
        if gray_rect_x >= WINDOW_WIDTH - gray_rect_width:
            moving_right = False
        elif gray_rect_x <= 0:
            moving_right = True

        # Draw gray rectangle above midwall
        draw_gray_rectangle(gray_rect_x, gray_rect_y, gray_rect_width, gray_rect_height)

    glDisable(GL_ALPHA_TEST)
    glDisable(GL_BLEND)

    # Display background
    draw_rect_tex(texture_names[0], 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    glutSwapBuffers()

# Function to handle mouse click
def mouse_click(button, state, x, y):
     global start_time, left_tank_active, circle_active, bullet_x, bullet_y, bullet_vx, bullet_vy
     initial_speed = 90
     if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bullet_y= tank_y + 60
        if left_tank_active:
            bullet_x = left_tank_x +310
            # Calculating starting position of the bullet to be relative to the gun angle
            bullet_x -= (bullet_x - left_tank_x) * 0.46 * (1 - math.cos(math.radians(left_gun_angle)))
            bullet_y += (bullet_y - tank_y) * 2.3 * math.sin(math.radians(left_gun_angle))

            bullet_vx = initial_speed * math.cos(math.radians(left_gun_angle))
            bullet_vy = initial_speed * math.sin(math.radians(left_gun_angle))

        elif not left_tank_active:
            bullet_x = right_tank_x - 90
            # Calculating starting position of the bullet to be relative to the gun angle
            bullet_x += (right_tank_x - bullet_x) * 0.2 * (1 - math.cos(math.radians(right_gun_angle)))
            bullet_y += (bullet_y - tank_y) * 2.3 * math.sin(math.radians(right_gun_angle))

            bullet_vx = initial_speed * math.cos(math.radians(right_gun_angle))
            bullet_vy = initial_speed * math.sin(math.radians(right_gun_angle))

        circle_active = True
        start_time = time.time()
        # Switch tank control
        left_tank_active = not left_tank_active  # Switch control to the other tank

# Function to restart the game
def restart_game():
    global game_over_1, game_over_2, left_tank_health_percentage, right_tank_health_percentage
    game_over_1 = False
    game_over_2 = False
    left_tank_health_percentage = 1.0
    right_tank_health_percentage = 1.0
    glutPostRedisplay()

# Function to handle keyboard input
def keyboard(key, x, y):
    global left_tank_x, right_tank_x, left_gun_angle, right_gun_angle, show_poster, game_over_1, game_over_2, about_poster_active

    # Define the movement range for the tanks
    min_tank_x = 5  # Minimum x-coordinate for left tank
    max_tank_x = 240  # Maximum x-coordinate for left tank
    min_right_tank_x = 685  # Minimum x-coordinate for right tank
    max_right_tank_x = WINDOW_WIDTH - 215  # Maximum x-coordinate for right tank

    if key == b'p' or key == b'P':  # Start the game immediately
        show_poster = False
    elif key == b'a' or key == b'A':  # Display about.png image
        if show_poster == True:
            about_poster_active = True
            show_poster = False
    elif key == b'r' or key == b'R':  # Return to poster.png image
        if not game_over_1 and not game_over_2 and about_poster_active:
            show_poster = True
            about_poster_active = False
    elif key == b'y' or key == b'Y':  # Restart the game
        if game_over_1 or game_over_2:
            restart_game()
    elif key == b'n' or key == b'N':  # Exit the game
        if game_over_1 or game_over_2:
            sys.exit()

    if left_tank_active:
        # Move left tank right within the allowed range
        if key == b'd' or key == b'D':
            if left_tank_x + 3 <= max_tank_x:
                left_tank_x += 3

        # Move left tank left within the allowed range
        elif key == b'a' or key == b'A':
            if left_tank_x - 3 >= min_tank_x:
                left_tank_x -= 3

    else:
        # Move right tank right within the allowed range
        if key == GLUT_KEY_RIGHT:
            if right_tank_x + 3 <= max_right_tank_x:
                right_tank_x += 3

        # Move right tank left within the allowed range
        elif key == GLUT_KEY_LEFT:
            if right_tank_x - 3 >= min_right_tank_x:
                right_tank_x -= 3

    glutPostRedisplay()

# Function to calculate the angle between two points
def calculate_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.degrees(math.atan2(dy, dx))

# Function to clamp an angle within a specified range
def clamp_angle(angle, min_angle, max_angle):
    if angle < min_angle:
        return min_angle
    elif angle > max_angle:
        return max_angle
    else:
        return angle

# Function to handle mouse motion
def mouse_motion(x, y):
    global left_gun_angle, right_gun_angle, left_tank_x, right_tank_x, tank_y, WINDOW_HEIGHT
    # Calculate angles between mouse pointer and gun positions
    if left_tank_active:
        left_angle = calculate_angle(left_tank_x + 160, tank_y + 85, x, WINDOW_HEIGHT - y)
        left_gun_angle = clamp_angle(left_angle, 0, 55)  # Restricting angle between 0 and 55 degrees
        # print(f"Left angle: {left_angle}")
        # print(f"Left gun angle: {left_gun_angle}")
        
    else:
        right_angle = calculate_angle(right_tank_x + 300, tank_y + 85, x, WINDOW_HEIGHT - y)
        if right_angle < 0:  # Check if mouse is below the tank gun
            right_gun_angle = 180  # Keep the right gun angle at 180 degrees
        else:
            right_gun_angle = clamp_angle(right_angle, 125, 180)  # Restricting angle between 125 and 180 degrees
        # print(f"Right angle: {right_angle}")
        # print(f"Right gun angle: {right_gun_angle}")
        

# Function to set up mouse motion callback
def mouse_motion_setup():
    glutPassiveMotionFunc(mouse_motion)

# Function to set up mouse click callback
def mouse_click_setup():
    glutMouseFunc(mouse_click)

# Function to set up special keyboard callback
def keyboard_setup():
    glutSpecialFunc(keyboard)

# Function to set up regular keyboard callback
def reg_keyboard_setup():
    glutKeyboardFunc(keyboard)

# Main function
def main():
    global left_gun_angle, right_gun_angle, hit_sound
    pygame.init()
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow("Tank War Game")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    hit_sound = pygame.mixer.Sound("./sounds/click.wav")
    Texture_init()
    
    left_gun_angle = 0  # Initialize left gun angle
    right_gun_angle = 180  # Initialize right gun angle
    glutDisplayFunc(display)
    glutIdleFunc(display)
    reg_keyboard_setup()  # Set up regular keyboard callback
    keyboard_setup()  # Set up special keyboard callback
    mouse_motion_setup()  # Set up mouse motion callback
    mouse_click_setup()  # Set up mouse click callback
    glutMainLoop()

# Entry point of the program
if __name__ == "__main__":
    main()
