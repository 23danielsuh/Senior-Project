from music21 import *


def open_file(midi_path):
    midi = converter.parse(midi_path)
    right_hand = midi.getElementsByClass(stream.Part)[0]

    return right_hand
