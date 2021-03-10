%% read test image

% change this path if needed 
% this should point to the test image in the data folder
fn = 'data\image.png';

% pixel size
nmperpix = 5 / (195 - 31);

% read image
im = common.Image.from_bitmap(fn, 'scale', nmperpix, 'unit', 'nm');

% draw mask - mask should be a closed contour around the sample
mask = roipoly(im.Channels);

% histogram edges
% 30 length bins between 0.5 and 2 nm
Lbins = linspace(0.5, 2, 30);
% 30 tortuosity bins between 1 and 2
Tbins = linspace(1, 2, 30);
% 30 spacing bins between 0.25 and 0.6 nm
dbins = linspace(0.25, 0.6, 30);

% resize scale
scale = 0.5;

%% Gabor filtering

% wavelength range of filter bank
% this should have a wide margin around the valid 0.3...0.5 nm range
lambda_min = 0.25;
lambda_max = 0.83;

% convert wavelength to frequency
freq_min = 1 / lambda_max;
freq_max = 1 / lambda_min;

% number of filters in the filter bank
% the higher the better, but increases computation cost
n_filts = 50;

% create a circular Gabor filter bank
fb = filters.circular_gabor.CircularGaborFilterBank.create(...
    freq_min, ...       % min frequency (max wavelength)
    freq_max, ...       % max frequency (min wavelength)
    n_filts, ...        % number of filters
    0.005, ...          % selectivity
    'spacing', ...      % distribute filter centers following an exponential series
    'exponential');

figure('Units', 'normalized', 'Position', [0.1 0.1 0.7 0.8]);

subplot(2, 2, 1);
im.resize(scale).plot();
title('test image');

subplot(2, 2, 2);
imagesc(1 ./ freq);
axis image;
colorbar;
set(gca, 'XTick', [], 'YTick', []);
title('apparent spacing, nm');

subplot(2, 2, 3);
imagesc(magn);
axis image;
set(gca, 'XTick', [], 'YTick', []);
title('modulation strength');

subplot(2, 2, 4);
% we resize the image so the computation is faster
[freq, unc, magn] = fb.get_frequencies(im.resize(scale), 'mode', 'strongest_vote');
% we are only interested in the spacing within the sample mask
[freqs, bins] = histwc(1 ./ freq(imresize(mask, scale)), magn(imresize(mask, scale)), dbins);
bar(bins, freqs);
xlabel('fringe spacing, nm');
ylabel('frequency');

%% fringe analysis
% don't forget to add the thirdparty folder to the Matlab path

% we don't resize because the parameters listed below won't work at half scale
scale = 1;

% algorithm parameters
int_threshold = 0.15;       % intensity threshold (t_bin)
lowpass_sigma = 1;          % lowpass filter scale (sigma_lowpass)
tophat_scale = 5;           % tophat filter radius (r_tophat)
openclose_scale = 3;        % opening/closing radius (r_open, r_close)
rdp_tolerance = 2.0;        % Ramer-Douglas-Peucker tolerance (t_rdp)
o_threshold = 20.0;         % parallelism threshold (t_parallel)

% binarize image
[binary, ~] = fringe.binarize_image(im.resize(scale).Channels, imresize(mask, scale), ...
    nmperpix/scale, ...
    int_threshold, ...
    lowpass_sigma*scale, ...
    round(tophat_scale*scale), ...
    round(openclose_scale*scale), ...
    round(openclose_scale*scale), ...
    0.5);

% measure fringe spacing
[d002, pairs, segments] = fringe.measure_fringe_separation(binary, rdp_tolerance, o_threshold);
dfreqs = histc(d002.*nmperpix/scale, dbins);

% measure length and tortuosity
[L_, T_, n] = fringe.measure_fringes(binary);
Lfreqs = histc(L_ .* nmperpix/scale, Lbins);
Tfreqs = histc(T_, Tbins);

figure('Units', 'normalized', 'Position', [0.1 0.1 0.7 0.8]);

subplot(2, 2, 1);
imshowpair(im.resize(scale).Channels, bwmorph(binary, 'dilate'));
set(gca, 'XTick', [], 'YTick', []);
title('image and detected fringes');

subplot(2, 2, 2);
bar(Lbins, Lfreqs);
xlabel('fringe length, nm');
ylabel('frequency');

subplot(2, 2, 3);
bar(Tbins, Tfreqs);
xlabel('tortuosity');
ylabel('frequency');

subplot(2, 2, 4);
bar(dbins, dfreqs);
xlabel('spacing, nm');
ylabel('frequency');
