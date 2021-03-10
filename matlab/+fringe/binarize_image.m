function [skel, P] = binarize_image( ...
    I, mask, nmperpix, ...
    threshold, ...      % varying
    lowpass_sigma, ...  % varying
    tophat_radius, ...  % varying
    closing_size, ...   % varying
    opening_size, ...   % varying
    min_fringe_length)
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

% negative transformation
P = 255 - I;

% histogram equalization
[~, T] = histeq(P(mask));
P = uint8(255 * T(P + 1));

% set up low-pass filter
% this is based on the paper - we try to maintain the ratio given there
% sigma = 1 / (4.711 * 2 * pi * nmperpix);
fsize = ceil(10 * lowpass_sigma);
if rem(fsize, 2) == 0
    fsize = fsize + 1;
end
P = imfilter(P, fspecial('gaussian', fsize, lowpass_sigma));

% top-hat transform
se = strel('disk', tophat_radius, 4);
P = imtophat(P, se);

% otsu thresholding
P = P > (255 * threshold);

% closing and opening
P = imclose(P, ones(closing_size, closing_size));
P = imopen(P, ones(opening_size, opening_size));
P = P & mask;

% skeletonize
skel = bwmorph(P, 'thin', inf);

% break up branches
bps = bwmorph(skel, 'branchpoints');
skel = bwmorph(max(0, skel-bwmorph(bps, 'dilate')), 'spur');

% remove boundary objects and small fringes
boundary_inds = find(bwperim(mask));
props = regionprops(skel, 'PixelIdxList', 'Area');
for i = 1:numel(props)
    if any(ismember(props(i).PixelIdxList, boundary_inds)) || props(i).Area * nmperpix < min_fringe_length
        skel(props(i).PixelIdxList) = false;
    end
end
