function director = direction_to_director(direction)
% direction is a modulo 2pi angle
% director is a unit length 2-vector

director = [cos(direction) sin(direction)];
