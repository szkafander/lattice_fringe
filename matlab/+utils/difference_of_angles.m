function da = difference_of_angles(a_1, a_2)

d_a = a_2 - a_1;
da = abs(mod(d_a + 90, 180) - 90);
