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

def get_keys(min_pitch, max_pitch):

    pitch_range = range(min_pitch, max_pitch)

    pitches = [pitch.Pitch(p) for p in pitch_range]
    
    for i, x in reversed(list(enumerate(pitches))):
        if pitches[i].name == "E" and pitches[i+1].name == "F" and i > 0:
            pitches.insert(i+1, "FILLER")
            
        if pitches[i].name == "B" and pitches[i+1].name == "C" and i > 0:
            pitches.insert(i+1, "FILLER")
    
    pitches = [str(p) for p in pitches]
            
    print(pitches)

    return pitches

def playNotes(part, robot):  
    keys = get_keys(36, 85)
    print(keys)
    
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
            
            robot.play_note(keys.index(str(el.pitch.name) + str(el.pitch.octave)) - robot.left_arm_position)
            
            print("Playing " + (el.pitch.name) + str(el.pitch.octave))
            
            time.sleep(duration - 0.075)

            robot.release(keys.index(str(el.pitch.name) + str(el.pitch.octave)) - robot.left_arm_position, duration)

            time.sleep(0.075)
                
        if type(el) == chord.Chord:
            print('WOEIJFOIJEFOIJEWFOIJWEOIFJWEOIJFOWEIJFOIJWEFO')

            for x in el._notes:

                pitch = x.pitch.ps

                duration = x.duration.quarterLength * (60 / BPM)
                
                robot.play_note(keys.index(str(x.pitch.name) + str(x.pitch.octave)) - robot.left_arm_position)
                
                print("Playing " + (x.pitch.name) + str(x.pitch.octave))

            time.sleep(duration - 0.075)
            
            for x in el._notes:
                robot.release(keys.index(str(x.pitch.name) + str(x.pitch.octave)) - robot.left_arm_position, duration)
            time.sleep(0.075)

        elif type(el) == note.Rest:
            duration = el.duration.quarterLength * (60 / BPM)
            time.sleep(duration)
            print(f"Resting for {duration} seconds")

def main():
    robot = Robot(get_keys(36, 85).index("C4"))

    song = open_file("../data/difficult_test.xml")
    
    song = song.stripTies()
    
    song = song.voicesToParts()
        
    with ThreadPoolExecutor() as executor:
        for part in song.getElementsByClass("Part"):
            a = executor.submit(playNotes, part, robot)
            print(a.result())
            
if __name__ == "__main__":
    main()
