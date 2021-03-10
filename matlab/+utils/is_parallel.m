function is_p = is_parallel(segment_1, segment_2, angle_tolerance)
% segment_1 (2 x 2)
% segment_2 (2 x 2)

is_p = difference_of_angles(get_orientation(segment_1), get_orientation(segment_2)) <= angle_tolerance;
