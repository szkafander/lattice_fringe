classdef Image
    
    properties
        
        Grid
        Channels
        Width
        Height
        NumChannels
        
    end
    
    properties (Dependent)
        
        Domain
        
    end
    
    methods
        
        function obj = Image(channels, varargin)
            
            p = inputParser;
            addOptional(p, 'grid', [], @(x)isa(x, 'common.Grid'));
            parse(p, varargin{:});
            
            grid = p.Results.grid;
            channels_size = size(channels);
            n_dims = numel(channels_size);
            
            if n_dims < 2 || n_dims > 3
                error('Channels must be a 2D or 3D array.');
            end
            
            if n_dims == 2
                num_channels = 1;
            else
                num_channels = channels_size(3);
            end
            
            obj.Width = channels_size(2);
            obj.Height = channels_size(1);
            obj.NumChannels = num_channels;
            
            % if grid is not passed, infer it
            if isempty(grid)
                [x_grid, y_grid] = meshgrid( ...
                    1:obj.Height, ...
                    1:obj.Width);
                grid = common.Grid( ...
                    x_grid, ...
                    y_grid, ...
                    'x_unit', 'pix', ...
                    'y_unit', 'pix');
            else
                % check grid-channels consistency
                obj.check_grid_channels_consistency(grid, channels);
            end
            
            obj.Grid = grid;
            obj.Channels = channels;
            
        end
        
        function image = get_channel(obj, channel_inds)
            
            image = common.Image( ...
                obj.Channels(:, :, channel_inds), ...
                obj.Grid);
            
        end
        
        function domain = get.Domain(obj)
            
            domain = obj.Grid.Domain;
            
        end
        
        function plot(obj, varargin)
            % displays the image
            %
            % supported image types:
            %   - grayscale spatial images (spatial, 1-channel, real)
            %   - color spatial images (spatial, 3-channel, real)
            %   - hyperspectral spatial images (spatial, n-channel, real)
            %   - frequency spectra (frequency, 1-channel, complex)
            %   - filtered spectra (frequency, n-channel, complex)
            %   - filtered images (spatial, n-channel, complex)
            
            p = inputParser;
            addParameter(p, 'log', true, @islogical);
            parse(p, varargin{:});
            
            log_ = p.Results.log;
            
            switch obj.NumChannels
                
                case 1
                    
                    % 1-channel, real -> grayscale
                    if isreal(obj.Channels)
                        
                        imagesc( ...
                            obj.Grid.XAxis, ...
                            obj.Grid.YAxis, ...
                            mat2gray(obj.Channels));
                        colormap gray;
                        
                    else
                        
                        % frequency, 1-channel, complex -> spectrum
                        if obj.Domain == common.Domain.Frequency
                            
                            re = abs(real(obj.Channels));
                            im = abs(imag(obj.Channels));
                            if log_
                                re = log(re);
                                im = log(im);
                            end
                            mag = log(real(obj.Channels).^2 ...
                                + imag(obj.Channels).^2);
                            
                            re(isinf(re)) = mean(re(~isinf(re)));
                            im(isinf(im)) = mean(im(~isinf(im)));
                            mag(isinf(mag)) = mean(mag(~isinf(mag)));
                            
                            re = re - min(re(:));
                            im = im - min(im(:));
                            max_comp = max(max(re(:)), max(im(:)));
                            
                            re = re ./ max_comp;
                            im = im ./ max_comp;
                            mag = mat2gray(mag);
                            
                            composite = zeros(obj.Height, obj.Width, 3);
                            composite(:, :, 1) = re;
                            composite(:, :, 2) = im;
                            composite(:, :, 3) = mag;
                            
                            imagesc( ...
                                obj.Grid.XAxis - obj.Grid.XDelta / 2, ...
                                obj.Grid.YAxis - obj.Grid.YDelta / 2, ...
                                composite);
                            
                        % spatial, 1-channel, complex -> filter response
                        else
                            
                            re = real(obj.Channels);
                            im = imag(obj.Channels);
                            mag = sqrt(re.^2 + im.^2);
                            
                            re = re - min(re(:));
                            im = im - min(im(:));
                            max_comp = max(max(re(:)), max(im(:)));
                            
                            re = re ./ max_comp;
                            im = im ./ max_comp;
                            mag = mat2gray(mag);
                            
                            composite = zeros(obj.Height, obj.Width, 3);
                            composite(:, :, 1) = re;
                            composite(:, :, 2) = im;
                            composite(:, :, 3) = mag;
                            
                            imagesc( ...
                                obj.Grid.XAxis - obj.Grid.XDelta / 2, ...
                                obj.Grid.YAxis - obj.Grid.YDelta / 2, ...
                                composite);
                            
                        end
                        
                    end
                    
                case 2
                    
                    % if real, just show as two-color image
                    if isreal(obj.Channels)
                        
                        composite = zeros(size(obj.Height, obj.Width, 3));
                        composite(:, :, 1:2) = obj.Channels;
                        
                        composite = composite - min(composite(:));
                        
                        imagesc( ...
                            obj.Grid.XAxis, ...
                            obj.Grid.YAxis, ...
                            composite ./ max(composite(:)));
                        
                    % if complex, assume that it's two filter responses
                    % show only the magnitudes
                    else
                        
                        response_1 = abs(obj.Channels(:,:,1));
                        response_2 = abs(obj.Channels(:,:,2));
                        
                        response_1 = response_1 - min(response_1(:));
                        response_2 = response_2 - min(response_2(:));
                        
                        max_comp = max(max(response_1(:)), ...
                            max(response_2(:)));
                        
                        composite = zeros(obj.Height, obj.Width, 3);
                        composite(:,:,1) = response_1 ./ max_comp;
                        composite(:,:,2) = response_2 ./ max_comp;
                        
                        imagesc( ...
                            obj.Grid.XAxis - obj.Grid.XDelta / 2, ...
                            obj.Grid.YAxis - obj.Grid.YDelta / 2, ...
                            composite);
                        
                    end
                    
                case 3
                    
                    % if real, show as RGB image
                    if isreal(obj.Channels)
                        
                        imagesc( ...
                            obj.Grid.XAxis, ...
                            obj.Grid.YAxis, ...
                            double(obj.Channels) ...
                                ./ max(double(obj.Channels(:))));
                        
                    % if complex
                    else
                        
                        % if complex and frequency domain, plot as spectrum
                        if obj.Domain == common.Domain.Spatial
                            
                            response_1 = abs(obj.Channels(:,:,1));
                            response_2 = abs(obj.Channels(:,:,2));

                            response_1 = response_1 - min(response_1(:));
                            response_2 = response_2 - min(response_2(:));

                            max_comp = max(max(response_1(:)), ...
                                max(response_2(:)));

                            composite = zeros(obj.Height, obj.Width, 3);
                            composite(:,:,1) = response_1 ./ max_comp;
                            composite(:,:,2) = response_2 ./ max_comp;

                            imagesc( ...
                                obj.Grid.XAxis - obj.Grid.XDelta / 2, ...
                                obj.Grid.YAxis - obj.Grid.YDelta / 2, ...
                                composite);
                        
                        % otherwise plot as response magnitude
                        else

                            mag_1 = log(abs(obj.Channels(:,:,1)));
                            mag_2 = log(abs(obj.Channels(:,:,2)));
                            mag_3 = log(abs(obj.Channels(:,:,3)));
                            
                            mag_1(isinf(mag_1)) = ...
                                mean(mag_1(~isinf(mag_1)));
                            mag_2(isinf(mag_2)) = ...
                                mean(mag_2(~isinf(mag_2)));
                            mag_3(isinf(mag_3)) = ...
                                mean(mag_3(~isinf(mag_3)));
                            
                            max_comp = max([ ...
                                max(mag_1(:)) ...
                                max(mag_2(:)) ...
                                max(mag_3(:))]);
                            
                            composite = zeros(obj.Height, obj.Width, 3);
                            composite(:,:,1) = mag_1 ./ max_comp;
                            composite(:,:,2) = mag_2 ./ max_comp;
                            composite(:,:,3) = mag_3 ./ max_comp;
                            
                            imagesc( ...
                                obj.Grid.XAxis - obj.Grid.XDelta / 2, ...
                                obj.Grid.YAxis - obj.Grid.YDelta / 2, ...
                                composite);
                            
                        end
                        
                    end
                    
            end
            
            if isempty(obj.Grid.XUnit)
                x_unit = '';
            else
                x_unit = [', ' obj.Grid.XUnit];
            end
            if isempty(obj.Grid.YUnit)
                y_unit = '';
            else
                y_unit = [', ' obj.Grid.YUnit];
            end
            axis image;
            xlabel([obj.Grid.XName x_unit]);
            ylabel([obj.Grid.YName y_unit]);
            
        end
        
        function resized = resize(obj, scale)
            
            if scale == 1
                resized = obj;
            else
                resized_channels = imresize(obj.Channels, scale);
                resized_grid = obj.Grid.resize(scale);
                resized = common.Image(resized_channels, 'grid', resized_grid);
            end
            
        end
        
        function frequency_image = ft(obj)
            
            if obj.Domain == common.Domain.Frequency
                warning(['The image is already in the frequency ' ...
                    'domain. Fourier transformation might not produce ' ...
                    'the desired result.']);
            end
            
            if obj.NumChannels == 1
                
                transformed = fftshift(fft2(double(obj.Channels)));
                
            else
                
                transformed = zeros( ...
                    obj.Height, ...
                    obj.Width, ...
                    obj.NumChannels);
                
                for i = 1:obj.NumChannels
                    transformed(:,:,i) = ...
                        fftshift(fft2(double(obj.Channels(:,:,i))));
                end
                
            end
            
            frequency_image = common.Image( ...
                transformed, ...
                'grid', obj.Grid.ft());
            
        end
        
        function spatial_image = ift(obj)
            
            if obj.Domain == common.Domain.Spatial
                warning(['The image is already in the spatial ' ...
                    'domain. Inverse Fourier transformation might not ' ...
                    'produce the desired result.']);
            end
            
            if obj.NumChannels == 1
                
                transformed = ifft2(fftshift(obj.Channels));
            
            else
                
                transformed = zeros( ...
                    obj.Height, ...
                    obj.Width, ...
                    obj.NumChannels);
                
                for i = 1:obj.NumChannels
                    transformed(:,:,i) = ...
                        ifft2(fftshift(obj.Channels(:,:,i)));
                end
                
            end
            
            spatial_image = common.Image( ...
                transformed, ...
                'grid', obj.Grid.ift());
            
        end
        
        function filtered_image = filter(obj, filter_bank)
            
            filtered_image = filter_bank.apply(obj);
            
        end
        
    end
    
    methods (Static)
        
        function check_grid_channels_consistency(grid, channels)
            
        end
        
        function image = from_bitmap(path, varargin)
            % instantiates an image object by reading a bitmap
            %
            % depending on the passed key-value pairs, the image grid can
            % be created in multiple ways.
            %
            % 1. if 'scale' is passed
            %   - both axes will have the same scale. do not pass 'x_scale'
            %     and 'y_scale'.
            %
            % 2. if 'x_scale' and/or 'y_scale' are passed
            %   - one or both of the axes will have the corresponding
            %     scale. if one is missing, 'scale' will be used to
            %     determine the missing scale.
            %
            % 3. if 'origin' is passed
            %   - the grid origin will become the passed value. if not
            %     passed, the origin will be at [1 1].
            %
            % 4. if 'grayscale' is passed
            %   - if set to true (this is the default), the image will be
            %     converted to grayscale and will have a single channel. if
            %     set to false, all read channels will be kept.
            
            p = inputParser;
            addParameter(p, 'scale', 1.0, @isscalar);
            addParameter(p, 'x_scale', [], @isscalar);
            addParameter(p, 'y_scale', [], @isscalar);
            addParameter(p, 'origin', [1 1], @(x)isvector(x)&numel(x)==2);
            addParameter(p, 'unit', 'pix', @isstr);
            addParameter(p, 'x_unit', '', @isstr);
            addParameter(p, 'y_unit', '', @isstr);
            addParameter(p, 'grayscale', true, @islogical);
            parse(p, varargin{:});
            
            % read image and determine size
            channels = imread(path);
            channels_size = size(channels);
            num_dims = numel(channels_size);
            
            % check if an actual image was read
            if num_dims > 3 || num_dims < 2
                error(['Multi-dimensional images and scalar series are' ...
                    ' not supported. The number of dimensions was ' ...
                    num2str(num_dims) '.']);
            end
            
            if num_dims == 2
                num_channels = 1;
            else
                num_channels = channels_size(3);
            end
            
            if p.Results.grayscale
                
                % if grayscale but has 3 channels, keep only first channel
                if num_channels == 3
                    if all(all(channels(:,:,1) == channels(:,:,2))) ...
                            && all(all(channels(:,:,2) == channels(:,:,3)))
                        channels = rgb2gray(channels);
                    end
                end
                
                if size(channels, 3) ~= 1
                    channels = rgb2gray(channels);
                end
                
            end
            
            % infer grid
            height = channels_size(1);
            width = channels_size(2);
            
            [x_grid, y_grid] = meshgrid(1:width, 1:height);
            
            % subtract origin
            x_grid = x_grid - p.Results.origin(1);
            y_grid = y_grid - p.Results.origin(2);
            
            % scale grid
            if ~isempty(p.Results.x_scale)
                x_grid = x_grid .* p.Results.x_scale;
            else
                x_grid = x_grid .* p.Results.scale;
            end
            
            if ~isempty(p.Results.y_scale)
                y_grid = y_grid .* p.Results.y_scale;
            else
                y_grid = y_grid .* p.Results.scale;
            end
            
            % add units
            if isempty(p.Results.x_unit)
                x_unit = p.Results.unit;
            else
                x_unit = p.Results.x_unit;
            end
            
            if isempty(p.Results.y_unit)
                y_unit = p.Results.unit;
            else
                y_unit = p.Results.y_unit;
            end
            
            grid = common.Grid( ...
                x_grid, ...
                y_grid, ...
                'x_unit', x_unit, ...
                'y_unit', y_unit);
            
            image = common.Image(channels, grid);
            
        end
        
    end
    
end
