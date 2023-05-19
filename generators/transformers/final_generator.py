import datetime
import sys
import os

sys.path.append("Los-Angeles-Music-Composer")
import statistics
from time import time

import music21
import TMIDIX
import torch
from lwa_transformer import *
from torchsummary import summary

# ============ CHANGEABLE PARAMETERS ============
"""
full_path_to_custom_seed_MIDI (str): full path to midi/mxl file to generate music from 
number_of_batches_to_generate (int): how many generations to create (standard to use 1) [1, 16]
temperature (float): temperature of generation (keep >=0.8 for interesting results) [0.1, 1]
generator_sequence_length (int): how many sequences should eb created in the music [1, inf]
number_of_prime_tokens (int): how many tokens to get from the midi file [126, 300, steps of 3]
number_of_memory_tokens (int): transformer parameter (don't change probably) [402, 4095]
"""
full_path_to_custom_seed_MIDI = "../../data/chopin_fantaisie_impromptu.mxl"
number_of_batches_to_generate = 1
temperature = 0.75
generator_sequence_length = 512
number_of_prime_tokens = 480
number_of_memory_tokens = 4095

# ============ DON'T CHANGE ANYTHING BELOW THIS POINT ============
if "mxl" in full_path_to_custom_seed_MIDI:
    print(
        "If you receive an error here, your XML file is corrupted, download another version of the piece or just download the actual midi file"
    )
    s = music21.converter.parse(full_path_to_custom_seed_MIDI)
    fp = s.write(
        "midi",
        fp=os.path.splitext(full_path_to_custom_seed_MIDI)[0] + ".mid",
    )

full_path_to_custom_seed_MIDI = (
    os.path.splitext(full_path_to_custom_seed_MIDI)[0] + ".mid"
)

full_path_to_model_checkpoint = "Los-Angeles-Music-Composer/Model/Los_Angeles_Music_Composer_Model_88835_steps_0.643_loss.pth"

SEQ_LEN = 4096

model = LocalTransformer(
    num_tokens=2831,
    dim=1024,
    depth=36,
    causal=True,
    local_attn_window_size=512,
    max_seq_len=SEQ_LEN,
)

model = torch.nn.DataParallel(model)

model.load_state_dict(
    torch.load(full_path_to_model_checkpoint, map_location=torch.device("cpu"))
)

print("Model summary...")
print(summary(model))

# @title Load Seed MIDI
select_seed_MIDI = "/Users/danielsuh/Downloads/twinkle"  # @param ["Los-Angeles-Music-Composer-Piano-Seed-1", "Los-Angeles-Music-Composer-Piano-Seed-2", "Los-Angeles-Music-Composer-Piano-Seed-3", "Los-Angeles-Music-Composer-Piano-Seed-4", "Los-Angeles-Music-Composer-Piano-Seed-5", "Los-Angeles-Music-Composer-MI-Seed-1", "Los-Angeles-Music-Composer-MI-Seed-2", "Los-Angeles-Music-Composer-MI-Seed-3", "Los-Angeles-Music-Composer-MI-Seed-4", "Los-Angeles-Music-Composer-MI-Seed-5"]


if full_path_to_custom_seed_MIDI == "":
    f = "Los-Angeles-Music-Composer/Seeds/" + select_seed_MIDI + ".mid"

else:
    f = full_path_to_custom_seed_MIDI

print("=" * 70)
print("Los Angeles Music Composer Seed MIDI Loader")
print("=" * 70)
print("Loaded file", f, "successfully.")
print("=" * 70)

# =======================================================
# START PROCESSING

# Convering MIDI to ms score with MIDI.py module
score = TMIDIX.midi2ms_score(open(f, "rb").read())

# INSTRUMENTS CONVERSION CYCLE
events_matrix = []
melody_chords_f = []
melody_chords_f1 = []
itrack = 1
patches = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

patch_map = [
    [0, 1, 2, 3, 4, 5, 6, 7],  # Piano
    [24, 25, 26, 27, 28, 29, 30],  # Guitar
    [32, 33, 34, 35, 36, 37, 38, 39],  # Bass
    [40, 41],  # Violin
    [42, 43],  # Cello
    [46],  # Harp
    [56, 57, 58, 59, 60],  # Trumpet
    [64, 65, 66, 67, 68, 69, 70, 71],  # Sax
    [72, 73, 74, 75, 76, 77, 78],  # Flute
    [-1],  # Drums
    [52, 53],  # Choir
    [16, 17, 18, 19, 20],  # Organ
]

while itrack < len(score):
    for event in score[itrack]:
        if event[0] == "note" or event[0] == "patch_change":
            events_matrix.append(event)
    itrack += 1

events_matrix.sort(key=lambda x: x[1])

events_matrix1 = []

for event in events_matrix:
    if event[0] == "patch_change":
        patches[event[2]] = event[3]

    if event[0] == "note":
        event.extend([patches[event[3]]])
        once = False

        for p in patch_map:
            if event[6] in p and event[3] != 9:  # Except the drums
                event[3] = patch_map.index(p)
                once = True

        if not once and event[3] != 9:  # Except the drums
            event[3] = 15  # All other instruments/patches channel
            event[5] = max(80, event[5])

        if event[3] < 12:  # We won't write chans 12-16 for now...
            events_matrix1.append(event)
            # stats[event[3]] += 1

# =======================================================
# PRE-PROCESSING

# checking number of instruments in a composition
instruments_list_without_drums = list(set([y[3] for y in events_matrix1 if y[3] != 9]))

if len(events_matrix1) > 0 and len(instruments_list_without_drums) > 0:
    # recalculating timings
    for e in events_matrix1:
        e[1] = int(e[1] / 10)  # Max 1 seconds for start-times
        e[2] = int(e[2] / 20)  # Max 2 seconds for durations

    # Sorting by pitch, then by start-time
    events_matrix1.sort(key=lambda x: x[4], reverse=True)
    events_matrix1.sort(key=lambda x: x[1])

    # =======================================================
    # FINAL PRE-PROCESSING

    melody_chords = []

    pe = events_matrix1[0]

    for e in events_matrix1:
        if e[1] >= 0 and e[2] > 0:
            # Cliping all values...
            tim = max(0, min(127, e[1] - pe[1]))
            dur = max(1, min(127, e[2]))
            cha = max(0, min(11, e[3]))
            ptc = max(1, min(127, e[4]))
            vel = max(8, min(127, e[5]))

            velocity = round(vel / 15)

            # Writing final note
            melody_chords.append([tim, dur, cha, ptc, velocity])

            pe = e


instruments_list = list(set([y[2] for y in melody_chords]))
num_instr = len(instruments_list)

# =======================================================
# FINAL PROCESSING
# =======================================================

# Break between compositions / Intro seq

if 9 in instruments_list:
    drums_present = 2818  # Yes
else:
    drums_present = 2817  # No

melody_chords_f.extend([2816, drums_present, 2819 + (num_instr - 1)])

# =======================================================

# Composition control seq
intro_mode_time = statistics.mode(
    [0] + [y[0] for y in melody_chords if y[2] != 9 and y[0] != 0]
)
intro_mode_dur = statistics.mode([y[1] for y in melody_chords if y[2] != 9])
intro_mode_pitch = statistics.mode([y[3] for y in melody_chords if y[2] != 9])
intro_mode_velocity = statistics.mode([y[4] for y in melody_chords if y[2] != 9])

# Instrument value 12 is reserved for composition control seq
intro_dur_vel = (intro_mode_dur * 8) + (intro_mode_velocity - 1)
intro_cha_ptc = (12 * 128) + intro_mode_pitch

melody_chords_f.extend([intro_mode_time, intro_dur_vel + 128, intro_cha_ptc + 1152])

# TOTAL DICTIONARY SIZE 2831

# =======================================================
# MAIN PROCESSING CYCLE
# =======================================================

for m in melody_chords:
    # WRITING EACH NOTE HERE
    dur_vel = (m[1] * 8) + (m[4] - 1)
    cha_ptc = (m[2] * 128) + m[3]

    melody_chords_f.extend([m[0], dur_vel + 128, cha_ptc + 1152])
    melody_chords_f1.append([m[0], dur_vel + 128, cha_ptc + 1152])

melody_chords_f1 = melody_chords_f1[: (number_of_prime_tokens // 3)]
melody_chords_f = melody_chords_f[:number_of_prime_tokens]

# =======================================================

song = melody_chords_f
song_f = []
tim = 0
dur = 0
vel = 0
pitch = 0
channel = 0

son = []
song1 = []

for s in song:
    if s >= 128 and s < (12 * 128) + 1152:
        son.append(s)
    else:
        if len(son) == 3:
            song1.append(son)
        son = []
        son.append(s)

for ss in song1:
    tim += ss[0] * 10

    dur = ((ss[1] - 128) // 8) * 20
    vel = (((ss[1] - 128) % 8) + 1) * 15

    channel = (ss[2] - 1152) // 128
    pitch = (ss[2] - 1152) % 128

    song_f.append(["note", tim, dur, channel, pitch, vel])


print("generating...")

preview = melody_chords_f[-120:]

inp = [melody_chords_f[-number_of_memory_tokens:]] * number_of_batches_to_generate

inp = torch.LongTensor(inp)

start_time = time()

out = model.module.generate(
    inp,
    generator_sequence_length,
    temperature=temperature,
    return_prime=False,
    verbose=True,
)

out0 = out.tolist()

print("=" * 70)
print("Done!")

print("=" * 70)
print("Generation took", time() - start_time, "seconds")

# ======================================================================
print("=" * 70)
print("Rendering results...")

for i in range(number_of_batches_to_generate):
    print("=" * 70)
    print("Batch #", i)
    print("=" * 70)

    out1 = out0[i]

    print("Sample INTs", out1[:12])
    print("=" * 70)

    if len(out) != 0:
        song = preview + out1
        song_f = []
        tim = 0
        dur = 0
        vel = 0
        pitch = 0
        channel = 0

        son = []
        song1 = []

        for s in song:
            if s >= 128 and s < (12 * 128) + 1152:
                son.append(s)
            else:
                if len(son) == 3:
                    song1.append(son)
                son = []
                son.append(s)

        for ss in song1:
            tim += ss[0] * 10

            dur = ((ss[1] - 128) // 8) * 20
            vel = (((ss[1] - 128) % 8) + 1) * 15

            channel = (ss[2] - 1152) // 128
            pitch = (ss[2] - 1152) % 128

            song_f.append(["note", tim, dur, channel, pitch, vel])

        detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(
            song_f,
            output_signature="Los Angeles Music Composer",
            output_file_name=f"{os.path.dirname(full_path_to_custom_seed_MIDI)}/generated/{os.path.split(full_path_to_custom_seed_MIDI)[1].split('.')[0]}_{datetime.datetime.now()}",
            track_name="Project Los Angeles",
            list_of_MIDI_patches=[
                0,
                24,
                32,
                40,
                42,
                46,
                56,
                71,
                73,
                0,
                53,
                19,
                0,
                0,
                0,
                0,
            ],
            number_of_ticks_per_quarter=500,
        )

block_action = "add_last_generated_block"  # @param ["add_last_generated_block", "remove_last_added_block"]
add_block_with_batch_number = 0  # @param {type:"slider", min:0, max:15, step:1}

if block_action == "add_last_generated_block":
    melody_chords_f.extend(out0[min(len(out0) - 1, add_block_with_batch_number)])
    print("Block added!")
else:
    melody_chords_f = melody_chords_f[
        : max(number_of_prime_tokens, (len(melody_chords_f) - 402))
    ]
    print("Block removed!")

if len(melody_chords_f) != 0:
    song = melody_chords_f
    song_f = []
    tim = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []
    song1 = []

    for s in song:
        if s >= 128 and s < (12 * 128) + 1152:
            son.append(s)
        else:
            if len(son) == 3:
                song1.append(son)
            son = []
            son.append(s)

    for ss in song1:
        tim += ss[0] * 10

        dur = ((ss[1] - 128) // 8) * 20
        vel = (((ss[1] - 128) % 8) + 1) * 15

        channel = (ss[2] - 1152) // 128
        pitch = (ss[2] - 1152) % 128

        song_f.append(["note", tim, dur, channel, pitch, vel])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(
        song_f,
        output_signature="Los Angeles Music Composer",
        output_file_name=f"{os.path.dirname(full_path_to_custom_seed_MIDI)}/continued/{os.path.split(full_path_to_custom_seed_MIDI)[1].split('.')[0]}_{datetime.datetime.now()}",
        track_name="Project Los Angeles",
        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0],
        number_of_ticks_per_quarter=500,
    )
    print("=" * 70)
    print("Displaying resulting composition...")
    print("=" * 70)

    fname = "Los-Angeles-Music-Composer-Music-Composition"

    x = []
    y = []
    c = []

print("Done!")
