from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

import music21 as m

from music21 import *

from concurrent.futures import ThreadPoolExecutor

import time

BPM = 120
ANGLE = 30

class Robot:

    left_arm_position = 0

    right_arm_position = 0

    def __init__(self, init_left_position):

        self.left_arm_position = init_left_position

    def move_motor(self, motorID):

        print("Moving motor " + str(motorID))
        
        kit.servo[motorID].angle = ANGLE

    def play_note(self, note):

        self.move_motor(note)

    def release(self, motorID, duration):

        print("Returning motor " + str(motorID))
        
        kit.servo[motorID].angle = 0

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

def playNotes(part, robot):  
    whiteKeys = get_white_keys(get_pitch_boundaries(part)[0], get_pitch_boundaries(part)[1])
    print(whiteKeys)
    
    beats = []
    for temp in part.recurse():
        beats.append(temp)
        print(temp)

    for i, el in enumerate(beats):  
        print(el)
        if i < len(beats) - 1 and type(beats[i]) == stream.Measure and type(beats[i + 1]) == stream.Measure:
            print(f'RUNNING ON {part}')
            time.sleep((beats[i + 1].getOffsetInHierarchy(part) - beats[i].getOffsetInHierarchy(part)) * (60 / BPM))
            continue
        
        if type(el) == note.Note:
            pitch = el.pitch.ps

            duration = el.duration.quarterLength * (60 / BPM)
            
            robot.play_note(whiteKeys.index(str(el.pitch.name) + str(el.pitch.octave)))
            
            print("Playing " + (el.pitch.name) + str(el.pitch.octave))
            
            time.sleep(duration - 0.075)

            robot.release(whiteKeys.index(str(el.pitch.name) + str(el.pitch.octave)), duration)

            time.sleep(0.075)
                
        if type(el) == chord.Chord:
            print('WOEIJFOIJEFOIJEWFOIJWEOIFJWEOIJFOWEIJFOIJWEFO')

            for x in el._notes:

                pitch = x.pitch.ps

                duration = x.duration.quarterLength * (60 / BPM)
                
                robot.play_note(whiteKeys.index(str(x.pitch.name) + str(x.pitch.octave)))
                
                print("Playing " + (x.pitch.name) + str(x.pitch.octave))

            time.sleep(duration - 0.075)
            
            for x in el._notes:
                robot.release(whiteKeys.index(str(x.pitch.name) + str(x.pitch.octave)), duration)
            time.sleep(0.075)

        elif type(el) == note.Rest:
            duration = el.duration.quarterLength * (60 / BPM)
            time.sleep(duration)
            print(f"Resting for {duration} seconds")

def main():
    robot = Robot(60)

    song = open_file("../data/difficult_test.xml")
    
    song = song.stripTies()
    
    song = song.voicesToParts()
        
    with ThreadPoolExecutor() as executor:
        for part in song.getElementsByClass("Part"):
            
            print(part.show('T'))
            a = executor.submit(playNotes, part, robot)
            
if __name__ == "__main__":
    main()
