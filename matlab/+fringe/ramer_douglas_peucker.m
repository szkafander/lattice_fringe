function res = ramer_douglas_peucker(points, epsilon)

d_max = 0;
ind = 0;

for i = 2:size(points, 1)
    
    d = utils.point_line_distance(points(i, :), points(1, :), points(end, :));
    if d > d_max
        ind = i;
        d_max = d;
    end
    
end

if d_max >= epsilon
    res = fringe.ramer_douglas_peucker(points(1 : ind + 1, :), epsilon);
    res = [res(1:end-1, :); fringe.ramer_douglas_peucker(points(ind:end, :), epsilon)];
else
    res = [points(1, :); points(end, :)];
end
