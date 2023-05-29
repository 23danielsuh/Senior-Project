from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

import music21 as m

import os

from music21 import *

from concurrent.futures import ThreadPoolExecutor

import time

import tkinter as tk

import tkinter.font as TkFont
from tkinter import filedialog
from tkinter import *
import tkinter.simpledialog

from tkinter import ttk

BPM = 90
ANGLE = 30
selected_file = "../data/beethoven_fur_elise.mxl"
d = {}
name_of_song = None


class Robot:
    left_arm_position = 0

    right_arm_position = 0

    def __init__(self, init_left_position):
        kit.servo[0].angle = 31
        kit.servo[2].angle = 38
        kit.servo[4].angle = 43
        kit.servo[5].angle = 40
        kit.servo[7].angle = 0
        kit.servo[9].angle = 12
        kit.servo[11].angle = 17
        kit.servo[1].angle = 40
        kit.servo[3].angle = 35
        kit.servo[6].angle = 15
        kit.servo[8].angle = 4
        kit.servo[10].angle = 1

        # for i in range(0, 6):
        #    kit.servo[i].angle = ANGLE

        # for i in range(6, 12):
        #    kit.servo[i].angle = 0
        self.left_arm_position = init_left_position

    def move_motor(self, motorID, accidental, window):
        while motorID < 0:
            motorID += 12
        while motorID >= 12:
            motorID -= 12
        # print("Moving motor " + str(motorID))

        if accidental == "natural":
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="#FFA32B")
        else:
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="#C03A38")

        # print('made it here')

        if motorID == 0:
            kit.servo[0].angle = 0
        if motorID == 2:
            kit.servo[2].angle = 16 - 10
        if motorID == 4:
            kit.servo[4].angle = 21 - 10
        if motorID == 5:
            kit.servo[5].angle = 18 - 10
        if motorID == 7:
            kit.servo[7].angle = 22 + 10
        if motorID == 9:
            kit.servo[9].angle = 36 + 10
        if motorID == 11:
            kit.servo[11].angle = 39 + 10
        if motorID == 1:
            kit.servo[1].angle = 25 - 10
        if motorID == 3:
            kit.servo[3].angle = 20 - 10
        if motorID == 6:
            kit.servo[6].angle = 30 + 10
        if motorID == 8:
            kit.servo[8].angle = 19 + 10
        if motorID == 10:
            kit.servo[10].angle = 16 + 10

        # if motorID >= 0 and motorID <= 5:
        #    kit.servo[int(motorID)].angle = 0
        # else:
        #    kit.servo[int(motorID)].angle = ANGLE

        # print(type(motorID))
        # print(motorID)
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

        # print("Returning motor " + str(motorID))

        if accidental == "natural":
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="white")
        else:
            window.canvas.itemconfig(str(int(motorID + 60)) + "A", fill="black")

        # kit.servo[motorID].angle = 0

        if motorID == 0:
            kit.servo[0].angle = 31
        if motorID == 2:
            kit.servo[2].angle = 38
        if motorID == 4:
            kit.servo[4].angle = 43
        if motorID == 5:
            kit.servo[5].angle = 40
        if motorID == 7:
            kit.servo[7].angle = 0
        if motorID == 9:
            kit.servo[9].angle = 12
        if motorID == 11:
            kit.servo[11].angle = 17
        if motorID == 1:
            kit.servo[1].angle = 40
        if motorID == 3:
            kit.servo[3].angle = 35
        if motorID == 6:
            kit.servo[6].angle = 25
        if motorID == 8:
            kit.servo[8].angle = 4
        if motorID == 10:
            kit.servo[10].angle = 1

        # if motorID >= 0 and motorID <= 5:
        #    kit.servo[int(motorID)].angle = ANGLE
        # else:
        #    kit.servo[int(motorID)].angle = 0


def open_file(xml_path, play_left_hand):
    file = converter.parse(xml_path)

    if play_left_hand:
        return file
    else:
        return file.getElementsByClass(stream.Part)[0]


def get_keys(min_pitch, max_pitch):
    pitch_range = range(min_pitch, max_pitch)

    pitches = [pitch.Pitch(p) for p in pitch_range]

    pitches = [str(p) for p in pitches]

    return pitches


def playNotes(part, robot, window):
    keys = get_keys(36, 85)

    beats = []
    for temp in part.recurse():
        beats.append(temp)

    for i, el in enumerate(beats):
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
            print("Playing chord")

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


def playSong():
    robot = Robot(get_keys(36, 85).index("C4"))

    global d
    d = {
        "Fur Elise": "../data/beethoven_fur_elise.mxl",
        "Twinkle Twinkle Little Star": "../data/mozart_twinkle.mxl",
        "One Octave": "../data/test_one_octave.mxl",
        "Moonlight Sonata Mvt. 1": "../data/beethoven_moonlight_1.mxl",
        "Moonlight Sonata Mvt. 3": "../data/beethoven_moonlight_3.mxl",
        "Nocturne Op. 9 No. 2": "../data/chopin_nocturne_9_2.mxl",
        "Clair de Lune": "../data/debussy_clair_de_lune.mxl",
        "Turkish March": "../data/mozart_turkish_march.mxl",
        "Mary Had a Little Lamb": "../data/mary_had_a_little_lamb.mxl",
        "Happy Birthday": "../data/happy_birthday.mxl",
        "Canon in D": "../data/pachelbel_canon_d.mxl",
        "Invention 13": "../data/bach_invention_13.mxl",
        "All of me": "../data/all_of_me.midi",
        "Clocks": "../data/clocks.mxl",
        "Entertainer": "../data/entertainer.mxl",
        "Flight of the Bumblebee": "../data/flight_of_the_bumblebee.mxl",
        "Game of Thrones": "../data/game_of_thrones.mxl",
        "Liebestraum": "../data/liebestraum.mxl",
        "Maple Leaf Rag": "../data/maple_leaf_rag.mxl",
        "Piano Man": "../data/piano_man.mxl",
        "Still Dre": "../data/still_dre.mxl",
        "Subwoofer Lullaby": "../data/subwoofer_lullaby.mxl",
        "Sweden": "../data/sweden.mxl",
    }
    d[name_of_song] = selected_file
    print(d)

    print(window.get_selected_LH_bool())
    song = open_file(d[window.get_selected_song()], window.get_selected_LH_bool())
    global BPM
    BPM = int(window.get_selected_bpm())
    song = song.stripTies()
    song = song.voicesToParts()

    with ThreadPoolExecutor() as executor:
        for part in song:
            a = executor.submit(playNotes, part, robot, window)
        # os.environ["TK_SILENCE_DEPRECATION"] = "1"
        # os.environ["DISPLAY"] = ":0"
        # window.draw()
        window.mainloop()


def browseFiles():
    filename = filedialog.askopenfilename(
        initialdir="./",
        title="Select a File",
        filetypes=(("Music files", "*.mid *.midi *.mxl *.xml"), ("all files", "*.*")),
    )
    global selected_file
    selected_file = filename

    print(selected_file)

    global name_of_song
    name_of_song = tk.simpledialog.askstring("Song name", "Song name:")
    window.append_song(name_of_song)

    window.option_menu.option_add(selected_file, selected_file)


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

        print(self.winfo_screenwidth())
        print(self.winfo_screenheight())

        self.whiteKeyWidth = self.width * 0.0325
        self.whiteKeyHeight = self.whiteKeyWidth * 4.5

        self.pianoWidth = numWhiteKeys * self.whiteKeyWidth

        self.blackKeyWidth = self.width * 0.0325 * (13.5 / 23.5)
        self.blackKeyHeight = self.blackKeyWidth * 5

        self.title("BOThoven UI")
        offsetX = int((self.winfo_screenwidth() - self.width) / 2)
        offsetY = int((self.winfo_screenheight() - self.height) / 2)

        self.configure(bg="#D3D3D3")

        OptionFont = TkFont.Font(family="Sans Serif")
        self.variable = tk.StringVar(self)

        self.variable.set("Fur Elise")
        self.values = [
            "Fur Elise",
            "Twinkle Twinkle Little Star",
            "One Octave",
            "Moonlight Sonata Mvt. 1",
            "Moonlight Sonata Mvt. 3",
            "Nocturne Op. 9 No. 2",
            "Clair de Lune",
            "Turkish March",
            "Mary Had a Little Lamb",
            "Happy Birthday",
            "Canon in D",
            "Invention 13",
            "All of me",
            "Clocks",
            "Entertainer",
            "Flight of the Bumblebee",
            "Game of Thrones",
            "Liebestraum",
            "Maple Leaf Rag",
            "Piano Man",
            "Still Dre",
            "Subwoofer Lullaby",
            "Sweden",
        ]

        self.option_menu = tk.OptionMenu(self, self.variable, *self.values)
        text = self.nametowidget(self.option_menu.menuname)
        text.config(font=OptionFont)
        self.option_menu.config(font=OptionFont)

        self.option_menu.config(width=self.width)
        self.option_menu.pack(
            padx=int(5 * (self.winfo_screenwidth() / 1440)),
            pady=int(5 * (self.winfo_screenheight() / 900)),
            side="top",
        )  # Adjusted position to top left corner

        button_frame = tk.Frame(self, bg="#D3D3D3")
        button_frame.pack(
            side="top", pady=int(5 * (self.winfo_screenheight() / 900))
        )  # Buttons on the left side

        button_text = ["Play Song", "Generate Music", "Import File"]
        for text in button_text:
            button = tk.Button(button_frame, text=text, font=OptionFont)
            if text == "Play Song":
                button = tk.Button(
                    button_frame,
                    text=text,
                    font=OptionFont,
                    command=playSong,
                )

            if text == "Import File":
                button = tk.Button(
                    button_frame, text=text, font=OptionFont, command=browseFiles
                )
            button.pack(
                side="left",
                ipady=int(5 * (self.winfo_screenheight() / 900)),
                padx=int(self.width * 0.01),
                ipadx=int(self.width * 0.05),
            )
            button.config(bg="white")

        self.BPM_SPINBOX = tk.StringVar(self)
        self.BPM_SPINBOX.set(90)

        BPM_FRAME = tk.Frame(self, bg="#D3D3D3")
        BPM_FRAME.pack(side="top", pady=int(5 * (self.winfo_screenheight() / 900)))

        self.spinbox = tk.Spinbox(
            BPM_FRAME, from_=30, to=240, textvariable=self.BPM_SPINBOX, wrap=False
        )

        self.LH = tk.BooleanVar(self)

        self.LH_radio = tk.Checkbutton(
            BPM_FRAME, text="Both Hands", variable=self.LH, bg="#D3D3D3"
        )
        self.LH_radio.pack(side="right")

        self.spinbox.pack(
            side="right",
            padx=int(5 * (self.winfo_screenwidth() / 1440)),
            pady=int(5 * (self.winfo_screenheight() / 900)),
        )

        self.bpm_label = tk.Label(BPM_FRAME, text="BPM:", bg="#D3D3D3")
        self.bpm_label.pack(side="left")

        self.option_menu.pack(
            padx=5, pady=5, side="top"
        )  # Adjusted position to top left corner

        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#D3D3D3",
        )

        self.geometry(
            "{0}x{1}+{2}+{3}".format(self.width, self.height, offsetX, offsetY)
        )

        self.canvas.pack()  # Fill and expand to fill the entire window

    def draw(self):
        self.keyWidth = 0
        self.keyHeight = 0
        self.xPos = (self.width - self.pianoWidth) / 2
        self.spinBoxBottom = self.spinbox.winfo_rooty() + self.spinbox.winfo_height()

        self.yPos = (
            (self.height - self.spinBoxBottom - self.whiteKeyHeight) / 2
        ) - self.whiteKeyHeight / 2
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

        # OptionFont = TkFont.Font(family="Sans Serif")

        # self.option_menu = tk.OptionMenu(self, self.variable, *self.values)
        # text = self.nametowidget(self.option_menu.menuname)
        # text.config(font=OptionFont)
        # self.option_menu.config(font=OptionFont)

        # self.option_menu.config(width=self.width)
        # self.option_menu.pack(
        #     padx=int(500 * (self.winfo_screenwidth() / 1440)),
        #     pady=int(5 * (self.winfo_screenheight() / 900)),
        #     side="top",
        # )  # Adjusted position to top left corner

        # self.option_menu.pack(
        #     padx=5, pady=5, side="top"
        # )  # Adjusted position to top left corner

    def get_selected_song(self):
        return self.variable.get()

    def get_selected_bpm(self):
        return self.BPM_SPINBOX.get()

    def get_selected_LH_bool(self):
        return self.LH.get()

    # def append_song(self, path):
    #     self.values.append(path)

    def append_song(self, path):
        self.values.append(path)
        self.option_menu["menu"].delete(0, "end")
        for option in self.values:
            self.option_menu["menu"].add_command(
                label=option, command=tk._setit(self.variable, option)
            )


window = PianoWindow(48, 84)


def main():
    os.environ["TK_SILENCE_DEPRECATION"] = "1"
    os.environ["DISPLAY"] = ":0"
    window.draw()
    window.mainloop()


if __name__ == "__main__":
    main()
