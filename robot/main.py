#!/usr/bin/env pybricks-micropython
import music21 as m
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
from music21 import *
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import pickle

def open_file(midi_path):

    midi = converter.parse(midi_path)

    right_hand = midi.getElementsByClass(stream.Part)[0]

    return right_hand.stripTies()

def main():

    song = open_file("../data/twinkle.xml")

    with open(r"./twinkle.txt", 'w') as file:

        for beat in song.recurse().notes:

            if beat.isNote:

                file.write(str(beat.pitch.ps))

            if beat.isChord:

                for i, x in enumerate(beat._notes):
                    
                    if i != len(beat._notes) - 1:

                        file.write(str(x.pitch.ps) + " ")

                    else:

                        file.write(str(x.pitch.ps))

            file.write(" " + str(beat.duration.quarterLength))

            file.write("\n")

if __name__ == "__main__":
    main()
