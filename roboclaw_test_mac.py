# import the relevant code from the RoboClaw library

from roboclaw_3 import Roboclaw
import pygame

# address of the RoboClaw as set in Motion Studio

address = 0x80

# Creating the RoboClaw object, serial port and baud rate passed

roboclaw = Roboclaw("/dev/tty.usbmodem11101", 38400)

# Starting communication with the RoboClaw hardware

roboclaw.Open()

# Basic enums for motor states

class MotorState:
    STOP = 0
    FORWARD = 1
    BACKWARD = 2

# Initial motor state and speeds

motor_state = MotorState.STOP
positive_speed = 63.0
negative_speed = 63.0

pygame.init()  # initializes pygame
screen = pygame.display.set_mode((768, 480))  # Sets up basic window
screen_rect = screen.get_rect()

# FSM to control the direction of the motor
def driveMotorState():
    global motor_state
    if motor_state == MotorState.STOP:
        roboclaw.ForwardM2(address, 0)

        # State transition logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            motor_state = MotorState.FORWARD
        elif keys[pygame.K_LEFT]:
            motor_state = MotorState.BACKWARD
    elif motor_state == MotorState.FORWARD:
        speedState()
        roboclaw.ForwardM2(address, int(positive_speed))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            motor_state = MotorState.STOP
        elif keys[pygame.K_LEFT]:
            motor_state = MotorState.BACKWARD
    elif motor_state == MotorState.BACKWARD:
        speedState()
        roboclaw.BackwardM2(address, int(negative_speed))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            motor_state = MotorState.STOP
        elif keys[pygame.K_RIGHT]:
            motor_state = MotorState.FORWARD

# Responsible for changing the speed of the motor
def speedState():
    global motor_state, positive_speed, negative_speed, events
    for event1 in events:
        if event1.type == pygame.QUIT:
            roboclaw.ForwardM2(address, 0)
            pygame.quit()
            exit()
        if event1.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                pygame.time.set_timer(pygame.USEREVENT, 1000)
                if motor_state == MotorState.FORWARD and positive_speed < 127:
                    positive_speed += 1
                elif motor_state == MotorState.BACKWARD and negative_speed < 127:
                    negative_speed += 1
            elif keys[pygame.K_DOWN]:
                pygame.time.set_timer(pygame.USEREVENT, 1000)
                if motor_state == MotorState.FORWARD and positive_speed > 0:
                    positive_speed -= 1
                elif motor_state == MotorState.BACKWARD and negative_speed > 0:
                    negative_speed -= 1
        if event1.type == pygame.KEYUP:
            pygame.time.set_timer(pygame.USEREVENT, 0)
        if event1.type == pygame.USEREVENT:
            rapidSpeed()

# If key to increase speed is held for longer the speed will rapidly increase
def rapidSpeed():
    global positive_speed, negative_speed
    pygame.time.set_timer(pygame.USEREVENT, 0)
    loop_breaker = False
    while not loop_breaker:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                roboclaw.ForwardM2(address, 0)
                pygame.quit()
                exit()
            if e.type == pygame.KEYUP:
                loop_breaker = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if motor_state == MotorState.FORWARD and positive_speed < 127:
                positive_speed += 0.01
                roboclaw.ForwardM2(address, int(positive_speed))
            elif motor_state == MotorState.BACKWARD and negative_speed < 127:
                negative_speed += 0.01
                roboclaw.BackwardM2(address, int(negative_speed))
        elif keys[pygame.K_DOWN]:
            if motor_state == MotorState.FORWARD and positive_speed > 0:
                positive_speed -= 0.01
                roboclaw.ForwardM2(address, int(positive_speed))
            elif motor_state == MotorState.BACKWARD and negative_speed > 0:
                negative_speed -= 0.01
                roboclaw.BackwardM2(address, int(negative_speed))


while True:
    events = pygame.event.get()
    driveMotorState()
    print(roboclaw.ReadTemp2(address))
    for event in events:
        if event.type == pygame.QUIT:
            roboclaw.ForwardM2(address, 0)
            pygame.quit()
            exit()
