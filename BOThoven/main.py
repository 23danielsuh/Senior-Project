# from adafruit_servokit import ServoKit

# kit = ServoKit(channels=16)

import music21 as m

import os

from music21 import *

from concurrent.futures import ThreadPoolExecutor

import time

import tkinter as tk

import tkinter.font as TkFont

from tkinter import ttk

BPM = 90
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

        print("pressing" + str(int(motorID)) + "A")

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

        print("releasing" + str(int(motorID)) + "A")

        if accidental == "natural":
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="white")
        else:
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="black")

        # kit.servo[motorID].angle = 0

    def translate(self, position):
        self.left_arm_position = position
        # print('moving to position', position)


def open_file(xml_path, play_left_hand):
    file = converter.parse(xml_path)

    if play_left_hand:
        return file
    else:
        return midi.getElementsByClass(stream.Part)[0]


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
            print("sdlfksdflkjsdf", el.getGrace())
            if el.duration.isGrace:
                continue
            pitch = el.pitch.ps

            if pitch % 12 in [1, 3, 6, 8, 10]:
                accidental = "black"
            else:
                accidental = "natural"

            # accidental = "natural"

            duration = el.duration.quarterLength * (60 / BPM)

            robot.play_note(pitch - 60, window, accidental)

            print("Playing " + (el.pitch.name) + str(el.pitch.octave))

            time.sleep(max(0, duration - 0.075))

            robot.release(pitch - 60, duration, window, pitch, accidental)

            time.sleep(0.075)

        if type(el) == chord.Chord:
            print("playing chord")

            for x in el._notes:
                pitch = x.pitch.ps

                if pitch % 12 in [1, 3, 6, 8, 10]:
                    accidental = "black"
                else:
                    accidental = "natural"

                duration = x.duration.quarterLength * (60 / BPM)

                robot.play_note(pitch - 60, window, accidental)

            time.sleep(max(0, duration - 0.075))

            for x in el._notes:
                pitch = x.pitch.ps

                if pitch % 12 in [1, 3, 6, 8, 10]:
                    accidental = "black"
                else:
                    accidental = "natural"

                robot.release(x.pitch.ps - 60, duration, window, x.pitch.ps, accidental)

            time.sleep(0.075)

        elif type(el) == note.Rest:
            duration = el.duration.quarterLength * (60 / BPM)
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

        self.width = int(self.winfo_screenwidth() / 2)
        self.height = int(self.winfo_screenheight() / 3)

        self.whiteKeyWidth = self.width * 0.0325
        self.whiteKeyHeight = self.whiteKeyWidth * 4.5

        self.pianoWidth = numWhiteKeys * self.whiteKeyWidth

        self.blackKeyWidth = self.width * 0.0325 * (13.5 / 23.5)
        self.blackKeyHeight = self.blackKeyWidth * 5

        self.title("BOThoven UI")
        offsetX = int((self.winfo_screenwidth() - self.width) / 2)
        offsetY = int((self.winfo_screenheight() - self.height) / 2)
        self.geometry(
            "{0}x{1}+{2}+{3}".format(self.width, self.height, offsetX, offsetY)
        )  # Set initial size and position

        self.configure(bg="#D3D3D3")

        OptionFont = TkFont.Font(family="Sans Serif")
        self.variable = tk.StringVar(self)
        self.variable.set("Song 1")
        self.values = ["Song 1", "Song 2", "Song 3", "Song 4"]

        self.option_menu = tk.OptionMenu(self, self.variable, *self.values)
        text = self.nametowidget(self.option_menu.menuname)
        text.config(font=OptionFont)
        self.option_menu.config(font=OptionFont)
        self.option_menu.pack(
            padx=5, pady=5, side="top"
        )  # Adjusted position to top left corner

        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#D3D3D3",
        )
        self.canvas.pack()  # Fill and expand to fill the entire window

    def draw(self):
        self.keyWidth = 0
        self.keyHeight = 0
        self.xPos = (self.width - self.pianoWidth) / 2
        self.yPos = (self.height) - (self.whiteKeyHeight * 1.6)

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

        # for x in self.keyPos:
        # print(x[1])

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

        border_width = 5
        startX = (self.width - self.pianoWidth) / 2
        self.canvas.create_rectangle(
            startX,
            self.yPos,
            startX + self.pianoWidth,
            self.yPos + self.whiteKeyHeight,
            width=border_width,
            outline="black",
        )


def main():
    robot = Robot(get_keys(36, 85).index("C4"))
    # song = open_file("../data/twinkle.xml")
    # song = open_file("../BOThoven/difficult_test.xml")
    # song = open_file("../data/fur_elise.mxl")
    # song = open_file("../data/one_octave.mxl")

    with ThreadPoolExecutor() as executor:
        window = PianoWindow(48, 84)
        song = open_file("../data/beethoven_fur_elise.mxl", True)
        song = song.stripTies()
        song = song.voicesToParts()
        for part in song:
            a = executor.submit(playNotes, part, robot, window)
        os.environ["TK_SILENCE_DEPRECATION"] = "1"
        os.environ["DISPLAY"] = ":0"
        window.draw()
        window.mainloop()


if __name__ == "__main__":
    main()
