function is_between = is_point_between_parallel_lines(line_1, line_2, point)
% line_1: [x0 y0 dx dy]
% line_2: [x1 y1 dx dy]
% point: [xp yp]

x0 = line_1(1);
y0 = line_1(2);
x1 = line_2(1);
y1 = line_2(2);
dx = line_1(3);
dy = line_1(4);
xp = point(1);
yp = point(2);

% get line_1 y at xp
t = (xp - x0) / dx;
line_1_y_at_xp = y0 + t * dy;

% get line_2 y at xp
t = (xp - x1) / dx;
line_2_y_at_xp = y1 + t * dy;

upper_y = max([line_1_y_at_xp line_2_y_at_xp]);
lower_y = min([line_1_y_at_xp line_2_y_at_xp]);

is_between = yp <= upper_y && yp >= lower_y;
