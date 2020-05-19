import numpy as np
import cv2

# image is (1303, 2544, 3)
# Way more 255s than 48s
im = cv2.imread('ROMv2.png')
print(im.shape)
height, width, _ = im.shape

def convert_to_black_white(im):
    for y in range(height):
        for x in range(width):
            s = sum(im[y,x])
            if s < 128 * 3:
                im[y,x] = [0,0,0]
            else:
                im[y,x] = [255,255,255]
    return im

def find_lines(im):
    # Does not include the ones on the border of the image
    vert_white_lines = []
    horiz_white_lines = []

    for y in range(height):
        count = 0
        for x in range(width):
            color = im[y, x][0]
            if color == 255:
                count += 1
        ratio = float(count)/width
        if ratio > 0.9:
            if y - 1 not in horiz_white_lines:
                horiz_white_lines += [y]
    print(horiz_white_lines)

    for x in range(width):
        count = 0
        for y in range(height):
            color = im[y, x][0]
            if color == 255:
                count += 1
        ratio = float(count)/height
        if ratio > 0.9:
            if x - 1 not in vert_white_lines:
                vert_white_lines += [x]
    print(vert_white_lines)
    return horiz_white_lines, vert_white_lines

im = convert_to_black_white(im)
print("Done converting")
# find_lines(im)
# Hardcoded to make things faster
horiz_white_lines = [20, 42, 64, 86, 108, 130, 152, 174, 196, 218, 240, 262, 284, 306, 328, 350, 372, 394, 416, 438, 460, 482, 504, 526, 548, 570, 592, 614, 636, 658, 680, 702, 724, 746, 768, 790, 812, 834, 856, 878, 900, 922, 944, 966, 988, 1010, 1032, 1054, 1076, 1098, 1120, 1142, 1164, 1186, 1208, 1230, 1252, 1274]
vert_white_lines = [0, 21, 43, 65, 87, 109, 131, 153, 175, 197, 219, 241, 263, 285, 307, 329, 351, 373, 395, 417, 439, 461, 483, 505, 527, 549, 571, 593, 615, 637, 659, 681, 703, 725, 747, 769, 791, 813, 835, 857, 879, 901, 923, 945, 967, 989, 1011, 1033, 1055, 1077, 1099, 1121, 1143, 1165, 1187, 1209, 1231, 1253, 1275, 1297, 1319, 1341, 1363, 1385, 1407, 1429, 1451, 1473, 1495, 1517, 1539, 1561, 1583, 1605, 1627, 1649, 1671, 1693, 1715, 1737, 1759, 1781, 1803, 1825, 1847, 1869, 1891, 1913, 1935, 1957, 1979, 2001, 2023, 2045, 2067, 2089, 2111, 2133, 2155, 2177, 2199, 2221, 2243, 2265, 2287, 2309, 2331, 2353, 2375, 2397, 2419, 2441, 2463, 2485]

ROM = [[] for _ in range(len(horiz_white_lines))]

for index_y, y in enumerate(horiz_white_lines):
    for index_x in range(len(vert_white_lines)):
        start_x = vert_white_lines[index_x]
        if index_x == len(vert_white_lines) - 1:
            end_x = width-1
        else:
            end_x = vert_white_lines[index_x+1]
        value = 0
        for x in range(start_x, end_x):
            color = im[y, x][0]
            if color != 255:
                value = 1
        ROM[index_y] += [value]
print(len(ROM))
print(len(ROM[0]))
for l in ROM:
    print("".join(map(str, l)))