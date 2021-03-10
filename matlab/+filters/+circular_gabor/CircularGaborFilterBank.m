classdef CircularGaborFilterBank < interfaces.FilterBank
    
    properties
        
        Abscissae
        Filters
        Selectivity
    
    end
    
    properties (Dependent)
        
        Coordinates
        MinFrequency
        MaxFrequency
    
    end
    
    methods
        
        function obj = CircularGaborFilterBank(filters)
            
            obj.Abscissae = {'center_frequency'};
            obj.Filters = filters;
        
        end
        
        function coordinates = get.Coordinates(obj)
            
            coordinates = cellfun(@(x)x.CenterFrequency, obj.Filters);
            
        end
        
        function min_frequency = get.MinFrequency(obj)
            
            min_frequency = min(obj.Coordinates);
            
        end
        
        function max_frequency = get.MaxFrequency(obj)
            
            max_frequency = max(obj.Coordinates);
            
        end
        
        function plot(obj, varargin)
            
            p = inputParser;
            addParameter(p, 'mode', 'image', @isstr);
            addParameter(p, 'image', [], @(x)isa(x, 'common.Image'));
            parse(p, varargin{:});
            
            mode = p.Results.mode;
            image = p.Results.image;
            
            if strcmp(mode, 'image')
                
                for i = 1:obj.NumFilters

                    if i == 1                    
                        obj.Filters{i}.plot('image', image);                    
                    else
                        obj.Filters{i}.plot('image', image, 'show_image', false);                    
                    end

                end
                
            elseif strcmp(mode, '1d')
                
                f = linspace(obj.MinFrequency, obj.MaxFrequency, 1000);
                for i = 1:obj.NumFilters
                    plot(f, exp( - ((f - obj.Filters{i}.CenterFrequency) / obj.Filters{i}.Sigma) .^ 2)); hold on;
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
        
        function [frequencies, certainty, q_1] = get_frequencies(obj, image, varargin)
            
            p = inputParser;
            addParameter(p, 'mode', 'strongest_vote', @isstr);
            parse(p, varargin{:});
            mode = p.Results.mode;
            
            responses = obj.get_responses(image);
            responses = cat(3, responses{:});
            center_frequencies = cellfun(@(x)x.CenterFrequency, obj.Filters);
            sigmas = cellfun(@(x)x.Sigma, obj.Filters);
            
            switch mode
                
                case 'strongest_vote'

                    % find maximum response index
                    [q_1, max_ind] = max(responses, [], 3);

                    % find neighbor to compare against
                    neighbor_ind = max_ind + 1;
                    neighbor_ind(neighbor_ind > size(responses, 3)) = max_ind(neighbor_ind > size(responses, 3)) - 1;

                    % calculate mean frequencies
                    mu_1 = center_frequencies(max_ind);
                    mu_2 = center_frequencies(neighbor_ind);
                    sigma_1 = sigmas(max_ind);
                    sigma_2 = sigmas(neighbor_ind);

                    % calculate strongest votes
                    N = size(responses, 1) * size(responses, 2); 
                    idx  = (1:N) + (neighbor_ind(1:N) - 1) * N;
                    q_2 = reshape(responses(idx), size(responses,1), size(responses,2));

                    % calculate frequencies
                    s = sign(mu_1 - mu_2);
                    frequencies = (mu_2 .* sigma_1.^2 + s.*sigma_2 ...
                        .* ( -s.*mu_1 .* sigma_2 + sigma_1 .* sqrt( ...
                        (mu_1 - mu_2).^2 + (sigma_1 - sigma_2) .* (sigma_1 + sigma_2) .* log(q_1 ./ q_2) ) ) ) ...
                        ./ ((sigma_1 - sigma_2) .* (sigma_1 + sigma_2));

                    certainty = q_1;
                    
                case 'weighted'
                    
                    votes = zeros(size(responses,1), size(responses,2), size(responses,3) - 1);
                    weights = votes;
                    
                    for i = 1:size(responses,3) - 1
                        
                        mu_1 = center_frequencies(i);
                        mu_2 = center_frequencies(i + 1);
                        sigma_1 = sigmas(i);
                        sigma_2 = sigmas(i + 1);
                        q_1 = responses(:,:,i);
                        q_2 = responses(:,:,i+1);
                        
                        s = sign(mu_1 - mu_2);
                        votes(:,:,i) = (mu_2 .* sigma_1.^2 + s.*sigma_2 ...
                            .* ( -s.*mu_1 .* sigma_2 + sigma_1 .* sqrt( ...
                            max(0, ...
                            (mu_1 - mu_2).^2 + (sigma_1 - sigma_2) .* (sigma_1 + sigma_2) .* log(q_1 ./ q_2) ) ) ) ) ...
                            ./ ((sigma_1 - sigma_2) .* (sigma_1 + sigma_2));
                        
                        weights(:,:,i) = q_1;
                        
                    end
                    
                    frequencies = sum(votes .* weights, 3) ./ sum(weights, 3);
                    certainty = max(weights, [], 3);

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
           addOptional(p, 'selectivity', 0.5, @isscalar);
           addParameter(p, 'spacing', 'hyperbolic', @isstr);
           parse(p, varargin{:});
           
           num_filters = p.Results.num_filters;
           high_frequency = p.Results.high_frequency;
           low_frequency = p.Results.low_frequency;
           selectivity = p.Results.selectivity;
           spacing = p.Results.spacing;
           
           switch spacing
               
               case 'hyperbolic'
                   
                   % create center frequencies so that filters are linearly spaced in wavelength-space
                   min_wavelength = 1 / high_frequency;
                   max_wavelength = 1 / low_frequency;
                   wavelengths = linspace(min_wavelength, max_wavelength, num_filters);
                   coordinates = sort(1 ./ wavelengths);
                   
                   % create similarly spaced intersection frequencies
                   d_wavelengths = (wavelengths(2) - wavelengths(1));
                   intersection_wavelengths = wavelengths - d_wavelengths / 2;
                   intersection_frequencies = sort(1 ./ intersection_wavelengths);
                   
               case 'exponential'
                   
                   r_multiplier = (high_frequency / low_frequency) ...
                       ^ (1 / (num_filters - 1));

                   coordinates = zeros(num_filters, 1);
                   intersection_frequencies = zeros(num_filters, 1);
                   for i = 1:num_filters
                       coordinates(i) = r_multiplier ^ (i - 1) * low_frequency;
                       intersection_frequencies(i) = r_multiplier ^ (i - 1 + 0.5) * low_frequency;
                   end
                   
               case 'linear'
                   
                   coordinates = linspace(low_frequency, high_frequency, num_filters);
                   intersection_frequencies = coordinates + (coordinates(2)-coordinates(1)) / 2;
                   
           end
           
           % calculate sigmas
           k = 1 - selectivity;
           slk = sqrt(log(1/k));
           sigmas = zeros(size(coordinates));
           for i = 1:numel(coordinates)
               sigmas(i) = (intersection_frequencies(i) - coordinates(i)) / slk;
           end
           
           filters_ = cell(num_filters, 1);
           for i = 1:num_filters
               filters_{i} = filters.circular_gabor.CircularGaborFilter(coordinates(i), sigmas(i));
           end
           
           filter_bank = filters.circular_gabor.CircularGaborFilterBank(filters_);
           
        end
        
    end
    
end
            