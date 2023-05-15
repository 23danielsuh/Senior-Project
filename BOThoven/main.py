#from adafruit_servokit import ServoKit

#kit = ServoKit(channels=16)

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

        self.move_motor(note)

    def release(self, motorID, duration):

        time.sleep(duration - 0.05)

        print("Returning motor " + str(motorID))

def open_file(xml_path):

    midi = converter.parse(xml_path)

    right_hand = midi.getElementsByClass(stream.Part)[0]

    return right_hand

def get_pitch_boundaries(song):

    lowestPitch = 60
    
    highestPitch = 60

    for note in song.recurse().notes:

        if note.isNote:

            if note.pitch.ps < lowestPitch:

                lowestPitch = note.pitch.ps
            
            elif note.pitch.ps > highestPitch:

                highestPitch = note.pitch.ps
        
        elif note.isChord:

            for x in note._notes:

                if x.pitch.ps < lowestPitch:

                    lowestPitch = x.pitch.ps
            
                elif x.pitch.ps > highestPitch:

                    highestPitch = x.pitch.ps
        
    return [lowestPitch, highestPitch]

def get_white_keys(min_pitch, max_pitch):

    pitch_range = range(int(min_pitch), int(max_pitch) + 1)

    pitches = [pitch.Pitch(p) for p in pitch_range]

    # Filter out all the non-white keys
    white_keys = [str(p) for p in pitches if str(p.accidental) == "natural"]

    return white_keys

def main():

    robot = Robot(60)

    song = open_file("/Users/benpomeranets/Documents/GitHub/senior_project/data/twinkle.xml")
    
    song = song.stripTies()

    whiteKeys = get_white_keys(get_pitch_boundaries(song)[0], get_pitch_boundaries(song)[1])

    print(whiteKeys)

    def playNotes():

        for note in song.recurse().notes:

            if note.isNote:

                pitch = note.pitch.ps

                duration = note.duration.quarterLength * (60 / BPM)
                
                robot.play_note(whiteKeys.index(str(note.pitch.name) + str(note.pitch.octave)))

                robot.release(whiteKeys.index(str(note.pitch.name) + str(note.pitch.octave)), duration)

                time.sleep(duration)

            if note.isChord:

                for x in note._notes:

                    pitch = x.pitch.ps

                    duration = x.duration.quarterLength * (60 / BPM)

                    robot.play_note(pitch)

                    robot.release(pitch - 60, duration)

                time.sleep(duration)
    
    playNotes()

if __name__ == "__main__":
    main()
