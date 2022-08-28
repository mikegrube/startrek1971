from math import atan2, pi, sqrt, cos, sin
from random import randint, uniform


def input_double(prompt):
    text = input(prompt)
    try:
        value = float(text)
    except:
        return False
    return value


def input_int(prompt):
    text = input(prompt)
    try:
        value = int(text)
    except:
        return False
    return value


def direction(x1, y1, x2, y2):
    if x1 == x2:
        if y1 < y2:
            dirct = 7   # south
        else:
            dirct = 3   # north
    elif y1 == y2:
        if x1 < x2:
            dirct = 1   # east
        else:
            dirct = 5   # west
    else:
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        angle = atan2(dy, dx)
        if x1 < x2:
            if y1 < y2: # southeast
                dirct = 9.0 - 4.0 * angle / pi
            else:   # northeast
                dirct = 1.0 + 4.0 * angle / pi
        else:
            if y1 < y2: # southwest
                dirct = 5.0 + 4.0 * angle / pi
            else:   # northwest
                dirct = 5.0 - 4.0 * angle / pi
    return dirct


def location():
    x = randint(0, 7)
    y = randint(0, 7)
    return x, y


def distance(x1, y1, x2, y2):

    x = x2 - x1
    y = y2 - y1
    return sqrt(x * x + y * y)


def variability(n):
    return randint(0, n)


def print_strings(string_list):
    for string in string_list:
        print(string)
    print()


def print_line(line, nb=0, na=0):
    for _ in range(nb):
        print()
    print(line)
    for _ in range(na):
        print()


def calculate_vector(dirct, dist):
    angle = -(pi * (dirct - 1.0) / 4.0)
    vx = dist * cos(angle)
    vy = dist * sin(angle)
    return vx, vy


def calculate_approx_vector(dirct):
    angle = -(pi * (dirct - 1.0) / 4.0)
    if variability(2) == 0:
        angle += (1.0 - 2.0 * uniform(0.0, 1.0) * pi * 2.0) * 0.03
    vx = cos(angle)
    vy = sin(angle)
    return vx, vy


def calculate_delivered_energy(dist):
    return 300 * uniform(0.0, 1.0) * (1.0 - dist / 11.3)
