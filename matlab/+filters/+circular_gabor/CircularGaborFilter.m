classdef CircularGaborFilter < interfaces.Filter
    properties
        CenterFrequency
        Sigma
        Cache
    end
    
    methods
        function obj = CircularGaborFilter(center_frequency, sigma)
            obj.CenterFrequency = center_frequency;
            obj.Sigma = sigma;
            obj.Cache = struct('grid', [], 'kernel_right', [], ...
                'kernel_down', []);
        end
        
        function [kernel_right, kernel_down] = get_kernels(obj, varargin)
            p = inputParser;
            addOptional(p, 'image', [], @(x)isa(x, 'common.Image'));
            addParameter(p, 'grid', [], @(x)isa(x, 'common.Grid'));
            parse(p, varargin{:});
            
            image = p.Results.image;
            grid = p.Results.grid;
            
            if ~isempty(image)
                grid = image.Grid;
            elseif isempty(grid)
                r = obj.CenterFrequency * 2;
                [x, y] = meshgrid( ...
                    linspace(-r, r, 100), ...
                    linspace(-r, r, 100));
                grid = common.Grid(x, y, 'domain', common.Domain.Frequency);
            end
            
            % is the grid in the cache? if yes, assume that the kernels are
            % already created and can be pulled from the cache
            if grid == obj.Cache.grid
                kernel_right = obj.Cache.kernel_right;
                kernel_down = obj.Cache.kernel_down;
            % otherwise create the kernel and store in cache
            else
                kernel_right = filters.circular_gabor.circular_gabor_frequency( ...
                    grid.XGrid, ...
                    grid.YGrid, ...
                    obj.CenterFrequency, ...
                    obj.Sigma, ...
                    0);
                kernel_down = filters.circular_gabor.circular_gabor_frequency( ...
                    grid.XGrid, ...
                    grid.YGrid, ...
                    obj.CenterFrequency, ...
                    obj.Sigma, ...
                    pi/2);
                obj.Cache.kernel_right = kernel_right;
                obj.Cache.kernel_down = kernel_down;
                obj.Cache.grid = grid;
            end
        end
        
        function response = get_response(obj, image)
            if image.Domain == common.Domain.Spatial
                image = image.ft();
            end
            [kernel_right, kernel_down] = obj.get_kernels(image);
            % filter the image and produce directional response
            response_right = abs(ifft2(fftshift(image.Channels ...
                .* kernel_right)));
            response_down = abs(ifft2(fftshift(image.Channels ...
                .* kernel_down)));
            response = response_right + response_down;
        end
        
        function response = apply(obj, image)
            % applies the directional quadrature filter and produces
            % a spatial response magnitude.

            % have we seen the grid before?
            % if the image if spatial, transform it
            if image.Domain == common.Domain.Spatial
                image = image.ft();
                grid_spatial = image.Grid;
            else
                grid_spatial = image.Grid.ift();
            end
            
            [kernel_right, kernel_down] = obj.get_kernels(image);
            
            % filter the image and produce directional response
            response_right = abs(ifft2(fftshift(image.Channels ...
                .* kernel_right)));
            response_down = abs(ifft2(fftshift(image.Channels ...
                .* kernel_down)));
            response = common.Image( ...
                response_right + response_down, ...
                'grid', grid_spatial);
        end
        
        function plot(obj, varargin)
            p = inputParser;
            addParameter(p, 'mode', 'image', @isstr);
            addParameter(p, 'image', [], @(x)isa(x, 'common.Image'));
            addParameter(p, 'size', [], @ismatrix);
            addParameter(p, 'show_image', true, @islogical);
            parse(p, varargin{:});
            
            image = p.Results.image;
            
            if ~isempty(image)
                if image.Domain == common.Domain.Spatial
                    image = image.ft();
                end
                if p.Results.show_image
                    image.plot();
                    hold on;
                end
                [kernel_right, kernel_down] = obj.get_kernels(image);
            else
                [kernel_right, kernel_down] = obj.get_kernels();
            end
            
            contour( ...
                obj.Cache.grid.XGrid, ...
                obj.Cache.grid.YGrid, ...
                kernel_right + kernel_down);
        end
    end
end
