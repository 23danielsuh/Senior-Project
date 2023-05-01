from music_reader import open_file
import music21 as m


def main():
    song = open_file("../data/twinkle.xml")
    # song = open_file(
    #     "../data/schema_annotation_data/data/mozart_sonatas/musicxml/K279-2.xml"
    # )
    song.show()

    song = song.stripTies()

    print("pitch, duration_string, duration, tie, midi pitch, octave")
    cnt = 0
    for a in song.recurse().notes:
        cnt += 1
        if a.isNote:
            x = a
            s = getMusicProperties(x)
            # print(s)

        if a.isChord:
            for x in a._notes:
                s = getMusicProperties(x)
                print(s)
            print()

    print("pitch, duration, midi pitch, octave")
    print("Done.", cnt)


def getMusicProperties(x):
    s = ""
    s = str(x.name) + ", " + str(x.duration.quarterLength)
    s += ", "
    s += str(x.pitch.ps) + ", " + str(x.octave)
    return s


if __name__ == "__main__":
    main()
