import music21 as m

from music21 import *

from music21 import *

keys = []

def get_white_keys(min_pitch, max_pitch):
    # Create a range of pitches using music21's pitch class
    pitch_range = range(min_pitch, max_pitch + 1)
    pitches = [pitch.Pitch(p) for p in pitch_range]
    
    # Filter out all the non-white keys
    white_keys = [str(p) for p in pitches if str(p.accidental) == "natural"]
    
    return white_keys

print(get_white_keys(60, 67))
