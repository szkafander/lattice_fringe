function ind = find_last_unique(array)

% assume that the index will be close to size(array, 1) / 2
s = size(array, 1);
ind = floor(s / 2 - s / 10);

for i = 1 : s - ind

    [B, ~, ib] = unique(p, 'rows');
numoccurences = accumarray(ib, 1);
indices = accumarray(ib, find(ib), [], @(rows){rows});