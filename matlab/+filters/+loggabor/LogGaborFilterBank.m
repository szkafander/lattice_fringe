classdef LogGaborFilterBank < interfaces.FilterBank
    properties
        Abscissae
        Filters
        FrequencyMultiplier
    end
    
    properties (Dependent)
        Coordinates
        MinFrequency
    end
    
    methods
        function obj = LogGaborFilterBank(filters)
            % there is only a single log-Gabor abscissa: radial frequency.
            % otherwise, two orthogonal frames are used.
            % don't use the constructor to instantiate this class - use the
            % create method instead
            frequencies = sort(cellfun(@(x)x.CenterFrequency, filters));
            frequency_multipliers = zeros(numel(frequencies) - 1, 1);
            for i = 1:numel(frequencies) - 1
                frequency_multipliers(i) = frequencies(i + 1) ...
                    / frequencies(i);
            end
            frequency_multiplier = uniquetol(frequency_multipliers, 1e-5);
            if numel(frequency_multiplier) > 1
                error(['The frequency multiplier cannot be inferred.' ...
                    'Consider using the "create" method to instantiate' ...
                    ' this class.']);
            end
            
            obj.Abscissae = {'center_frequency'};
            obj.Filters = filters;
            obj.FrequencyMultiplier = frequency_multiplier;
        end
        
        function coordinates = get.Coordinates(obj)
            coordinates = cellfun(@(x)x.CenterFrequency, obj.Filters);
        end
        
        function min_frequency = get.MinFrequency(obj)
            min_frequency = min(obj.Coordinates);
        end
        
        function plot(obj, varargin)
            p = inputParser;
            addParameter(p, 'image', [], @(x)isa(x, 'common.Image'));
            parse(p, varargin{:});
            
            image = p.Results.image;
            
            for i = 1:obj.NumFilters
                if i == 1                    
                    obj.Filters{i}.plot('image', image);                    
                else                    
                    obj.Filters{i}.plot('image', image, 'show_image', false);                    
                end
            end
        end
        
        function responses = get_responses(obj, image)
            responses = cellfun( ...
                @(x)x.get_response(image), ...
                obj.Filters, ...
                'UniformOutput', false);
        end
        
        function response = apply(obj, image)
            responses = obj.get_responses(image);
            response = common.Image( ...
                cat(3, responses{:}), ...
                'grid', image.Grid);
        end
        
        function [frequencies, certainty, max_response] = get_frequencies(obj, image, varargin)
            p = inputParser;
            addParameter(p, 'mode', 'strongest_vote', @isstr);
            parse(p, varargin{:});
            mode = p.Results.mode;
            
            responses = obj.get_responses(image);
            responses = cat(3, responses{:});
            center_frequencies = cellfun(@(x)x.CenterFrequency, obj.Filters);
            
            switch mode
                case 'weighted'
                    % according to Westin's thesis
                    % frequency
                    max_response = max(responses, [], 3);
                    term_1 = obj.MinFrequency ...
                        .* (1 ./ sum(responses(:, :, 1:end-1), 3));
                    term_2 = zeros(size(responses, 1), size(responses, 2));
                    for i = 1:size(responses, 3) - 1
                        term_2 = term_2 ...
                            + obj.FrequencyMultiplier ^ ((i - 1) + 0.5) ...
                            * responses(:, :, i + 1);
                    end
                    frequencies = term_1 .* term_2;

                    % certainty measure
                    channels = responses .^ 2;
                    term_1 = 1 ./ sum(channels(:, :, 1:end-1), 3);
                    term_2 = zeros(size(responses, 1), size(responses, 2));
                    for i = 1:size(responses, 3) - 1
                        term_2 = term_2 ...
                            + responses(:, :, i) .^2 ...
                            .* (obj.FrequencyMultiplier ^ ((i - 1) + 0.5) ...
                            * responses(:, :, i + 1) ./ responses(:, :, i) ...
                            - frequencies) .^ 2;
                    end
                    certainty = 1 ./ (1 + term_1 .* term_2);
                case 'strongest_vote'
                    % find maximum response index
                    [max_response, max_ind] = max(responses, [], 3);

                    % find neighbor to compare against
                    neighbor_ind = max_ind + 1;
                    neighbor_ind(neighbor_ind > size(responses, 3)) = max_ind(neighbor_ind > size(responses, 3)) - 1;

                    % calculate mean frequencies
                    this_freqs = center_frequencies(max_ind);
                    neighbor_freqs = center_frequencies(neighbor_ind);
                    mean_freqs = sqrt(this_freqs .* neighbor_freqs);

                    % calculate strongest votes
                    N = size(responses, 1) * size(responses, 2); 
                    idx  = [1:N] + (neighbor_ind(1:N) - 1) * N;
                    neighbor_responses = reshape(responses(idx), size(responses,1), size(responses,2));
                    frequencies = mean_freqs .* max_response ./ neighbor_responses;

                    certainty = max_response;
            end
        end
    end
    
    methods (Static)
        function filter_bank = create(varargin)
           % creates a log-Gabor filter bank. sets up abscissae based on
           % filter bank limits.
           %
           % the following methods can be used to set up the filter bank:
           %
           % 1. pass 'low_frequency', 'high_frequency' and 'num_filters',
           %    optionally pass 'spacing'
           %        this will calculate the relative bandwidths and
           %        populate the filter bank with filters spaced according
           %        to 'spacing'
           p = inputParser;
           addOptional(p, 'low_frequency', 1, @isscalar);
           addOptional(p, 'high_frequency', 5, @isscalar);
           addOptional(p, 'num_filters', 10, @(x)isscalar(x)&&floor(x)==x);
           parse(p, varargin{:});
           
           num_filters = p.Results.num_filters;
           high_frequency = p.Results.high_frequency;
           low_frequency = p.Results.low_frequency;
           
           r_multiplier = (high_frequency / low_frequency) ...
               ^ (1 / (num_filters - 1));
           bandwidth = 2 * sqrt(2 / log(2)) * sqrt(log(r_multiplier));
           
           coordinates = zeros(num_filters, 1);
           for i = 1:num_filters
               coordinates(i) = r_multiplier ^ (i - 1) * low_frequency;
           end
           
           filters_ = arrayfun( ...
               @(x)filters.loggabor.LogGaborFilter(x, bandwidth), ...
               coordinates, ...
               'UniformOutput', false);
           
           filter_bank = filters.loggabor.LogGaborFilterBank(filters_);
        end
    end
end
