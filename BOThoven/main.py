#from adafruit_servokit import ServoKit

import music21 as m

from music21 import *

from concurrent.futures import ThreadPoolExecutor

import time

BPM = 60

class Robot:

    left_arm_position = 0

    right_arm_position = 0

    def __init__(self, init_left_position):

        self.left_arm_position = init_left_position

    def move_motor(self, motorID):

        print("Moving motor " + str(motorID))

    def play_note(self, note):

        self.move_motor(note - self.left_arm_position)

    def release(self, motorID, duration):

        time.sleep(duration - 0.05)

        print("Returning motor " + str(motorID))


def open_file(xml_path):

    midi = converter.parse(xml_path)

    right_hand = midi.getElementsByClass(stream.Part)[0]

    return right_hand

def main():

    robot = Robot(60)

    song = open_file("/Users/benpomeranets/Documents/GitHub/senior_project/data/test.mxl")
    
    song = song.stripTies()

    song = song.voicesToParts(separateById = True)

    print(' '.join([p.nameWithOctave for p in song.parts[0].pitches]))

    print(' '.join([p.nameWithOctave for p in song.parts[1].pitches]))

    def playNotes(executor, part):

        for note in part.recurse().notes:

            if note.isNote:
                pitch = note.pitch.ps
                duration = note.duration.quarterLength

                robot.play_note(pitch)
                executor.submit(robot.release, pitch - 60, duration)

                time.sleep(duration)

            if note.isChord:
                for x in note._notes:
                    pitch = note.pitch.ps
                    duration = note.duration.quarterLength

                    robot.play_note(pitch)
                    executor.submit(robot.release, pitch - 60, duration)

                time.sleep(duration)

    #print("pitch, duration_string, duration, tie, midi pitch, octave")
    with ThreadPoolExecutor() as executor:

        for part in song.parts:

            executor.submit(playNotes, executor, part)

def getMusicProperties(x):
    s = ""
    s = str(x.name) + ", " + str(x.duration.quarterLength)
    s += ", "
    s += str(x.pitch.ps) + ", " + str(x.octave)
    return s

if __name__ == "__main__":
    main()
