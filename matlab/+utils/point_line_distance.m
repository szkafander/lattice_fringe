function d = point_line_distance(point, start_, end_)

if start_ == end_
    d = distance(point, start_);
else
    n = abs( (end_(1) - start_(1)) * (start_(2) - point(2)) - ...
        (start_(1) - point(1)) * (end_(2) - start_(2)) );
    d = sqrt( (end_(1) - start_(1)) .^ 2 + (end_(2) - start_(2)) .^ 2 );
    d = n ./ d;
end
