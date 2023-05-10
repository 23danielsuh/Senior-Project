#!/usr/bin/env pybricks-micropython
"""from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
#import music21 as m
import time
import xml.etree.ElementTree as ET
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    TouchSensor,
    ColorSensor,
    InfraredSensor,
    UltrasonicSensor,
    GyroSensor,
)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

# Create your objects here.

#Initialize the EV3 Brick
ev3 = EV3Brick()

#Initialize the motors
PortA_Motor = Motor(Port.A)

PortB_Motor = Motor(Port.B)

#PortC_Motor = Motor(Port.C)

#PortD_Motor = Motor(Port.D)

#PortA_Motor.run_target(500, 20)

#PortB_Motor.run_target(500, 20)

count = 0

while True:

    if count % 2 == 0:

        start_time = time.time()

        PortA_Motor.run_target(5000, -40, wait = False)
        
        PortB_Motor.run_target(5000, -40)

        time.sleep(60 / 105 - (time.time() - start_time + 0.05))


    else:

        start_time = time.time()

        PortA_Motor.run_target(5000, 40, wait = False)

        PortB_Motor.run_target(500, 40)

        time.sleep(60 / 105 - (time.time() - start_time + 0.05))

    count += 1"""
import time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    TouchSensor,
    ColorSensor,
    InfraredSensor,
    UltrasonicSensor,
    GyroSensor,
)

from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import pickle

TEMPO_BPM = 60
MOTOR_SPEED_DPS = 100
ROBOT_ARM_SPAN = 4

class Chord:
    note_names = []
    pitches = []

    def __init__(self, notes):
        for note in notes:
            self.note_names.append(note.name)
            self.pitches.append(note.pitch.ps)

    def get_highest_pitch(self):
        return max(self.pitches)

    def get_lowest_pitch(self):
        return min(self.pitches)


class Robot:
    left_arm_position = 0
    right_arm_position = 0

    motor1 = Motor(Port.A)
    motor2 = Motor(Port.B)
    # motor3 = Motor(Port.A)
    # motor4 = Motor(Port.B)

    def __init__(self, init_left_position):
        self.left_arm_position = init_left_position
        self.right_arm_position = self.left_arm_position + ROBOT_ARM_SPAN

        self.motor1.reset_angle(0)
        self.motor2.reset_angle(0)
        # self.motor3.reset_angle(0)
        # self.motor4.reset_angle(0)

    def note_in_range(self, note):
        if note >= self.left_arm_position and note <= self.right_arm_position:
            return True

        return False

    def move_position(self, left_position):
        self.left_arm_position = left_position
        self.right_arm_position = self.left_arm_position + ROBOT_ARM_SPAN

    def move_motor(self, motor_id, move_left_arm, wait):
        motor_to_move = None
        desired_target = 30

        if motor_id == 1:
            motor_to_move = self.motor1
        elif motor_id == 2:
            motor_to_move = self.motor2
        # elif motor_id == 3:
            # motor_to_move = self.motor3
        # else:
            # motor_to_move = self.motor4

        if move_left_arm:
            desired_target *= -1

        motor_to_move.run_target(MOTOR_SPEED_DPS, desired_target, wait=wait)
        # motor_to_move.track_target(desired_target) <- TODO: test later

    def move_arm(self, arm, wait):
        # print(f"moving arm {arm // 2 + 1}, at translation {self.left_arm_position}")
        self.move_motor((arm + 1) // 2, arm % 2 == 0, wait)

    def play_note(self, note, wait):
        print('moving arm', note - self.left_arm_position + 1)
        self.move_arm(note - self.left_arm_position + 1, wait)

    def move_to_neutral_position(self):

        self.motor1.run_target(MOTOR_SPEED_DPS, 0, wait=False)
        self.motor2.run_target(MOTOR_SPEED_DPS, 0, wait=False)

        # self.motor3.run_target(MOTOR_SPEED_DPS, 0, wait=False)
        # self.motor4.run_target(MOTOR_SPEED_DPS, 0, wait=False)
        time.sleep(1.5)
        print('motor1', self.motor1.angle())
        print('motor2', self.motor2.angle())




def main():

    robot = Robot(60)

    # Open the pickle file in binary mode
    with open(r'./twinkle copy.txt', 'r') as fp:

        for line in fp:

            start_time = time.time()

            x = line[:-1] # remove linebreak from the line

            XList = x.split()

            duration = XList[len(XList) - 1]

            notes = XList[0:len(XList) - 1]

            time.sleep(1)

            for note in notes:

                robot.play_note(float(note), True)

                print(note)
            
            # time.sleep(max(0, 60 / TEMPO_BPM - (time.time() - start_time + 0.2)))
            
            robot.move_to_neutral_position()

    # we start with the assumption that we start from note 60 (middle C)

    # for beat in song.recurse().notes:
    #     start_time = time.time()

    #     if beat.isNote:
    #         print("playing note", beat.name)
    #         robot.play_note(beat.pitch.ps, True)

    #     if beat.isChord:
    #         print("playing chord:")
    #         for x in beat._notes:
    #             print(x.name)
    #             robot.play_note(x.pitch.ps, False)

        # some time has elapsed such that the note is being played currently. we want to release the note 0.05 seconds before the next beat.
        # each beat should last 60 / BPM seconds
        # time.sleep(60 / TEMPO_BPM - (time.time() - start_time + 0.05))
        # print("time elapsed: ", time.time() - start_time)
        # robot.move_to_neutral_position()

    print("Done")


if __name__ == "__main__":

    main()