#from adafruit_servokit import ServoKit

#kit = ServoKit(channels=16)

import music21 as m

import os

from music21 import *

from concurrent.futures import ThreadPoolExecutor

import time

import tkinter as tk

BPM = 120
ANGLE = 30

class Robot:

    left_arm_position = 0

    right_arm_position = 0

    def __init__(self, init_left_position):

        self.left_arm_position = init_left_position

    def move_motor(self, motorID):

        print("Moving motor " + str(motorID))
        
        #kit.servo[motorID].angle = ANGLE

    def play_note(self, note, window):

        self.move_motor(note)
        
        window.canvas.itemconfig("30", fill="red")
        window.canvas.itemconfig("31", fill="red")
        window.canvas.itemconfig("32", fill="red")
        window.canvas.itemconfig("33", fill="red")
        window.canvas.itemconfig("34", fill="red")
        window.canvas.itemconfig("35", fill="red")
        window.canvas.itemconfig("36", fill="red")
        window.canvas.itemconfig("37", fill="red")
        window.canvas.itemconfig("38", fill="red")
        window.canvas.itemconfig("39", fill="red")
        window.canvas.itemconfig("40", fill="red")
        window.canvas.itemconfig("41", fill="red")

        # Get the corresponding key_id for the played note
        #key_id = str(note)

        # Change the color of the key to green

    def release(self, motorID, duration, window):

        print("Returning motor " + str(motorID))

        window.canvas.itemconfig("30", fill="white")
        window.canvas.itemconfig("31", fill="white")
        window.canvas.itemconfig("32", fill="white")
        window.canvas.itemconfig("33", fill="white")
        window.canvas.itemconfig("34", fill="white")
        window.canvas.itemconfig("35", fill="white")
        window.canvas.itemconfig("36", fill="white")
        window.canvas.itemconfig("37", fill="white")
        window.canvas.itemconfig("38", fill="white")
        window.canvas.itemconfig("39", fill="white")
        window.canvas.itemconfig("40", fill="white")
        window.canvas.itemconfig("41", fill="white")
    
        #kit.servo[motorID].angle = 0
        
    def translate(self, position):
        self.left_arm_position = position
        #print('moving to position', position)
    

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

def playNotes(part, robot, window):  
    keys = get_keys(36, 85)
    print(keys)
    
    beats = []
    for temp in part.recurse():
        beats.append(temp)
        print(temp)

    for i, el in enumerate(beats):  
        print(el)
        if i < len(beats) - 1 and type(beats[i]) == stream.Measure and type(beats[i + 1]) == stream.Measure:
            time.sleep((beats[i + 1].getOffsetInHierarchy(part) - beats[i].getOffsetInHierarchy(part)) * (60 / BPM))
            continue
        
        if type(el) == note.Note:
            pitch = el.pitch.ps

            duration = el.duration.quarterLength * (60 / BPM)
            
            robot.play_note(keys.index(str(el.pitch.name) + str(el.pitch.octave)) - robot.left_arm_position, window)
            
            print("Playing " + (el.pitch.name) + str(el.pitch.octave))
            
            time.sleep(duration - 0.075)

            robot.release(keys.index(str(el.pitch.name) + str(el.pitch.octave)) - robot.left_arm_position, duration, window)

            time.sleep(0.075)
                
        if type(el) == chord.Chord:

            print("playing chord")

            for x in el._notes:

                pitch = x.pitch.ps

                duration = x.duration.quarterLength * (60 / BPM)
                
                robot.play_note(keys.index(str(x.pitch.name) + str(x.pitch.octave)) - robot.left_arm_position, window)
                
                print("Playing " + (x.pitch.name) + str(x.pitch.octave))

            time.sleep(duration - 0.075)
            
            for x in el._notes:

                robot.release(keys.index(str(x.pitch.name) + str(x.pitch.octave)) - robot.left_arm_position, duration, window)

            time.sleep(0.075)

        elif type(el) == note.Rest:
            duration = el.duration.quarterLength * (60 / BPM)
            time.sleep(duration)
            print(f"Resting for {duration} seconds")
    
    print("done")

class PianoWindow(tk.Tk):

    def __init__(self, startNote, endNote):
        super().__init__()

        numWhiteKeys = 0

        for key in range(startNote, endNote + 1):

            if not key % 12 in [1, 3, 6, 8, 10]:

                numWhiteKeys += 1

        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        self.whiteKeyWidth = self.width * 0.02
        self.whiteKeyHeight = self.height * 0.14

        self.pianoWidth = numWhiteKeys * self.whiteKeyWidth

        self.blackKeyWidth = self.width * 0.02 * (13.5 / 23.5)
        self.blackKeyHeight = self.blackKeyWidth * 5
        
        self.title("BOThoven UI")
        self.geometry("{0}x{1}+0+0".format(self.width, self.height))  # Set initial size and position

        self.configure(bg="white")

        self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg="#D3D3D3")
        self.canvas.pack()  # Fill and expand to fill the entire window

        keyWidth = 0
        keyHeight = 0
        xPos = (self.width - self.pianoWidth) / 2
        yPos = (self.height * 3/4) - self.whiteKeyHeight

        blackKeyPos = []

        for note in range(startNote, endNote + 1):
            x = xPos
            if note % 12 in [1, 3, 6, 8, 10]:
                blackKeyPos.append([x, note])

            else:
                color = 'white'
                keyWidth = self.whiteKeyWidth
                keyHeight = self.whiteKeyHeight
                key = self.canvas.create_rectangle(x, yPos, x + keyWidth, yPos + keyHeight, fill=color, outline='black')
                self.canvas.itemconfig(key, tags=str(note))  # Add 'key' tag to identify white keys 

                xPos += keyWidth
        
        for pos in blackKeyPos:
            color = 'black'
            keyWidth = self.blackKeyWidth
            keyHeight = self.blackKeyHeight
            key = self.canvas.create_rectangle(pos[0] - keyWidth / 2, yPos, pos[0] + keyWidth / 2, yPos + keyHeight, fill=color, outline='black')
            self.canvas.itemconfig(key, tags=str(pos[1]))

def main():
    robot = Robot(get_keys(36, 85).index("C4"))
    song = open_file("../BOThoven/difficult_test.xml")
    song = song.stripTies()
    song = song.voicesToParts()

    with ThreadPoolExecutor() as executor:
        window = PianoWindow(24, 84)
        a = executor.submit(playNotes, song, robot, window)
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        os.environ["DISPLAY"] = ":0"
        window.mainloop()

if __name__ == "__main__":
    main()
    
