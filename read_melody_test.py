# For test/dev

from read_melody import *
from util import getBinFromFrequency

def test_reading():
    name = "AimeeNorwich_Child"
    pitches = read_melody(name, sampling_rate=1)
    dir = "../MedleyDB_selected/Annotations/Melody_Annotations/MELODY1/"
    csv_file = dir+name+"_MELODY1.csv"
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            curr_frequency = float(row.values()[0])
            if  curr_frequency > 0 and getBinFromFrequency(curr_frequency)!= pitches[count]:
                return False
            count += 1
    return True

print test_reading()
