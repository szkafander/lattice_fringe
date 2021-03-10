function [d002, pairs, segments] = measure_fringe_separation(binary, rdp_tolerance, o_threshold)
% d002 must still be filtered in post-processing for invalid distances
% this procedure should be reasonably straightforward - for each fringe, it
% attempts to find the closest fringe that is parallel enough. applies
% Ramer-Douglas-Peucker simplification to the fringe objects before
% spacing estimation. for details, see:
% @article{ramer1972iterative,
%   title={An iterative procedure for the polygonal approximation of plane curves},
%   author={Ramer, Urs},
%   journal={Computer Graphics and Image Processing},
%   volume={1},
%   number={3},
%   pages={244--256},
%   year={1972},
%   publisher={Elsevier}
% }
% TODO - may still skip a match and pair an indirect neighbor
% if the direct neighbor is not detected.

% segment tracing
s = regionprops(binary, 'Image', 'BoundingBox');
segments = cell(1, 1);
segment_parent_inds = zeros(size(segments));
k = 0;
for i = 1:numel(s)
    im = s(i).Image;
    eps = bwmorph(im, 'endpoints');
    [ex, ey] = find(eps);
    if numel(ex) == 2
        trace = bwtraceboundary(im, [ex(1) ey(1)], 'N');
        ind_mid = find(trace(:,1) == ex(2) & trace(:,2) == ey(2));
        trace = trace(1 : ind_mid, :);
        trace = fringe.ramer_douglas_peucker(trace, rdp_tolerance);
        for j = 2:size(trace, 1)
            k = k + 1;
            segment_parent_inds(k) = i;
            endpoints = [trace(j-1, 2)+s(i).BoundingBox(1)-0.5 trace(j-1, 1)+s(i).BoundingBox(2)-0.5; ...
                trace(j, 2)+s(i).BoundingBox(1)-0.5 trace(j, 1)+s(i).BoundingBox(2)-0.5];
            segments{k, 1} = fringe.Segment(k, endpoints, i);
        end
    end
end

% rangesearch on centroids
centroids = cellfun(@(x)x.Centroid, segments, 'UniformOutput', false);
centroids = vertcat(centroids{:});
rs = rangesearch(centroids, centroids, 50);

% match pairs of segments
dists_matched = [];
inds_matched = [];

for i = 1:numel(segments)

    neighbors = rs{i};
    s1 = segments{i};
    parent = s1.Parent;

    % given i, get segments sf that are in front
    neighbor_segments = segments(neighbors);
    sf = cell(1, 1);
    k = 0;
    for j = 1:numel(neighbor_segments)
        if neighbors(j) ~= i
            s2 = neighbor_segments{j};
            if s2.Parent ~= parent
                if s1.is_other_in_front_of_this(s2)
                    k = k + 1;
                    sf{k, 1} = s2;
                end
            end
        end
    end

    % given sf, get segments sfp that are parallel enough
    if ~isempty(sf{1})
        delta_o = cellfun(@(x)utils.difference_of_angles(x.Orientation, s1.Orientation), sf);
        sfp = sf(delta_o < o_threshold);
        delta_o = delta_o(delta_o < o_threshold);

        % given sfp, get closest segments on each side sfpc
        if ~isempty(sfp)

            distances = cellfun(@(x)s1.parallel_distance_from(x), sfp);
            sides = cellfun(@(x)s1.which_side_is_point(x.Centroid), sfp);

            % closest each side
            left = sides < 0;
            if any(left)
                dists = distances;
                dists(~left) = Inf;
                [~, ind_left] = min(dists);
            else
                ind_left = [];
            end
            right = sides > 0;
            if any(right)
                dists = distances;
                dists(~right) = Inf;
                [~, ind_right] = min(dists);
            else
                ind_right = [];
            end

            % indices in sfp that have been picked as best
            inds = [ind_left ind_right];

            % check if there is a better fit on both sides
            parents = cellfun(@(x)x.Parent, sfp);
            for l = 1:numel(inds)
                ind_current = inds(l);
                % indices in sfp that are from the same parent as ind_current
                inds_same_parent = find(parents == parents(ind_current));
                if numel(inds_same_parent) > 1
                    % pick the one that is the most parallel
                    delta_o_same = delta_o(inds_same_parent);
                    [~, ind_min_delta_o] = min(delta_o_same);
                    inds(l) = inds_same_parent(ind_min_delta_o);
                end
            end

            % collect distances
            distances_matched_ = distances(inds);
            dists_matched = [dists_matched; distances_matched_(:)];
            inds_matched_ = cellfun(@(x)x.Index, sfp(inds));
            inds_matched = [inds_matched; [ones(numel(inds_matched_), 1).*i inds_matched_(:)]];

        end
    end
    
end

% get rid of nonunique pairs
[pairs, inds_unique] = unique(inds_matched, 'rows');
d002 = dists_matched(inds_unique);
