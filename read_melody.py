import csv
from pitch_contour import *


def read_melody(folder_name, dir="../MedleyDB_selected/Annotations/Melody_Annotations/MELODY1/"):

    csv_file = dir+folder_name+"_MELODY1.csv"
    pitch_list = []
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            #print(row,row.keys())
            if (count%2!=0):
                count+=1
                continue
            newFrequency = 0.0
            lst = list(row.values())
            if float(lst[0]) > 0:
                newFrequency = getFrequencyFromBin(getBinFromFrequency(float(list(row.values())[0])))
                # print newFrequency
            pitch_list.append(newFrequency)
            count+=1
#        if True:
#          print(len(pitch_list))
#          print(pitch_list[:3])
    return pitch_list


if __name__ == '__main__':
    pitch_list = read_melody("AimeeNorwich_Child")
