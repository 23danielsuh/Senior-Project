# from adafruit_servokit import ServoKit

# kit = ServoKit(channels=16)

import music21 as m

import os

from music21 import *

from concurrent.futures import ThreadPoolExecutor

import time

import tkinter as tk

BPM = 80
ANGLE = 30


class Robot:
    left_arm_position = 0

    right_arm_position = 0

    def __init__(self, init_left_position):
        self.left_arm_position = init_left_position

    def move_motor(self, motorID, accidental, window):
        while motorID < 0:
            motorID += 12
        while motorID >= 12:
            motorID -= 12
        print("Moving motor " + str(motorID))
        
        print('pressing' + str(int(motorID)) + "A")

        if accidental == "natural":
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="#FFA32B")
        else:
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="#C03A38")
        

        # kit.servo[motorID].angle = ANGLE

    def play_note(self, note, window, accidental):
        self.move_motor(note, accidental, window)

        # Get the corresponding key_id for the played note
        # key_id = str(note)

        # Change the color of the key to green

    def release(self, motorID, duration, window, pitch, accidental):
        while motorID < 0:
            motorID += 12
        while motorID >= 12:
            motorID -= 12

        print("Returning motor " + str(motorID))
        
        print('releasing' + str(int(motorID)) + "A")
        
        if accidental == "natural":
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="white")
        else:
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="black") 
        
        # kit.servo[motorID].angle = 0

    def translate(self, position):
        self.left_arm_position = position
        # print('moving to position', position)


def open_file(xml_path):
    midi = converter.parse(xml_path)

    right_hand = midi.getElementsByClass(stream.Part)[0]

    return right_hand


def get_keys(min_pitch, max_pitch):
    pitch_range = range(min_pitch, max_pitch)

    pitches = [pitch.Pitch(p) for p in pitch_range]

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
        if (
            i < len(beats) - 1
            and type(beats[i]) == stream.Measure
            and type(beats[i + 1]) == stream.Measure
        ):
            time.sleep(
                (
                    beats[i + 1].getOffsetInHierarchy(part)
                    - beats[i].getOffsetInHierarchy(part)
                )
                * (60 / BPM)
            )
            continue

        if type(el) == note.Note:
            pitch = el.pitch.ps
            
            if pitch % 12 in [1, 3, 6, 8, 10]:
                accidental = "black"
            else:
                accidental = "natural"
            
            #accidental = "natural"

            duration = el.duration.quarterLength * (60 / BPM)

            robot.play_note(
                pitch - 60,
                window,
                accidental
            )

            print("Playing " + (el.pitch.name) + str(el.pitch.octave))

            time.sleep(duration - 0.075)

            robot.release(
                pitch - 60,
                duration,
                window,
                pitch,
                accidental
            )

            time.sleep(0.075)

        if type(el) == chord.Chord:
            print("playing chord")

            for x in el._notes:
                pitch = x.pitch.ps

                if pitch % 12 in [1, 3, 6, 8, 10]:
                    accidental = "black"
                else:
                    accidental = "natural"
                    
                #accidental = "natural"
                
                duration = x.duration.quarterLength * (60 / BPM)

                robot.play_note(
                    pitch - 60,
                    window,
                    accidental
                )

            time.sleep(duration - 0.075)

            for x in el._notes:
                robot.release(
                    x.pitch.ps - 60,
                    duration,
                    window,
                    x.pitch.ps,
                    accidental
                )

            time.sleep(0.075)

        elif type(el) == note.Rest:
            time.sleep(duration)
            print(f"Resting for {duration} seconds")

    print("done")


class PianoWindow(tk.Tk):
    def __init__(self, startNote, endNote):
        super().__init__()

        self.startNote = startNote
        self.endNote = endNote

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
        self.geometry(
            "{0}x{1}+0+0".format(self.width, self.height)
        )  # Set initial size and position

        self.configure(bg="white")

        self.canvas = tk.Canvas(
            self,
            width=self.winfo_screenwidth(),
            height=self.winfo_screenheight(),
            bg="#D3D3D3",
        )
        self.canvas.pack()  # Fill and expand to fill the entire window

    def draw(self):
        self.keyWidth = 0
        self.keyHeight = 0
        self.xPos = (self.width - self.pianoWidth) / 2
        self.yPos = (self.height * 3 / 4) - self.whiteKeyHeight

        self.blackKeyPos = []

        self.keyPos = []

        for note in range(self.startNote, self.endNote + 1):
            x = self.xPos
            if note % 12 in [1, 3, 6, 8, 10]:
                self.blackKeyPos.append([x, note])
                self.keyPos.append(
                    [x + -(self.blackKeyWidth / 2), note, False, "black"]
                )
            else:
                keyWidth = self.whiteKeyWidth
                keyHeight = self.whiteKeyHeight
                self.keyPos.append([x, note, False, "white"])

                self.xPos += keyWidth
                
        #for x in self.keyPos:
            #print(x[1])

        for key in self.keyPos:
            if key[3] == "white":
                self.canvas.create_rectangle(
                    key[0],
                    self.yPos,
                    key[0] + self.whiteKeyWidth,
                    self.yPos + self.whiteKeyHeight,
                    fill="white",
                    outline="black",
                    tags=str(key[1]) + "A",
                )

        for key in self.keyPos:
            if key[3] == "black":
                self.canvas.create_rectangle(
                    key[0],
                    self.yPos,
                    key[0] + self.blackKeyWidth,
                    self.yPos + self.blackKeyHeight,
                    fill="black",
                    outline="black",
                    tags=str(key[1]) + "A",
                )


def main():
    robot = Robot(get_keys(36, 85).index("C4"))
    #song = open_file("../data/twinkle.xml")
    #song = open_file("../BOThoven/difficult_test.xml")
    song = open_file("../data/fur_elise.mxl")
    #song = open_file("../data/one_octave.mxl")
    song = song.stripTies()
    song = song.voicesToParts()

    with ThreadPoolExecutor() as executor:
        window = PianoWindow(24, 84)
        for part in song:
            a = executor.submit(playNotes, part, robot, window)
            #print(a.result())
        os.environ["TK_SILENCE_DEPRECATION"] = "1"
        os.environ["DISPLAY"] = ":0"
        window.draw()
        window.mainloop()


if __name__ == "__main__":
    main()
