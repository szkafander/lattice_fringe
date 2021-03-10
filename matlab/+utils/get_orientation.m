function o = get_orientation(segment)

o = atand((segment(2, 2) - segment(1, 2)) / (segment(2, 1) - segment(1, 1)));
