function [L, T, n] = measure_fringes(binary)
% this roughly implements the method described in
% @article{2011yehliu,
%   title={Development of an {HRTEM} image analysis method to quantify carbon nanostructure},
%   author={Yehliu, Kuen and Vander Wal, Randy L and Boehman, Andr{\'e} L},
%   journal={Combustion and Flame},
%   volume={158},
%   number={9},
%   pages={1837--1851},
%   year={2011},
%   publisher={Elsevier}
% }

S = regionprops(binary, 'Image', 'PixelIdxList');
n = numel(S);
L = zeros(n, 1);
T = zeros(n, 1);

for i = 1:n
    im = S(i).Image;
    endpoints = bwmorph(im, 'endpoints');
    [x, y] = find(endpoints);
    d = 0;
    for j = 1:numel(x)
        for k = 1:numel(x)
            if k ~= j
                d = max(d, (x(j) - x(k))^2 + (y(j) - y(k))^2);
            end
        end
    end
    L_ = bwarea(im);
    L(i) = L_;
    T(i) = L_ / sqrt(d);
end
