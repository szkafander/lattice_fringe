classdef Grid
    
    properties

        % coordinates as {X, Y}, both are meshgrid-type
        % the two arrays must have the same size
        XGrid
        YGrid
        
        % vectors of x and y
        XAxis
        YAxis
        
        % coordinate extents as [[x_min, x_max], [y_min, y_max]]
        XExtent
        YExtent
        
        % the step size along the two axes as [dx, dy]
        XDelta
        YDelta
        
        % size of both coordinate arrays as [r, c]
        % the two arrays must have the same size
        Size
        
        % names of axes
        XName
        YName
        
        % units, str or 2-cellstr
        XUnit
        YUnit
        
        Domain
        
    end
    
    methods
        
        function obj = Grid(varargin)
            % ways to instantiate a grid:
            %
            % 1. pass XGrid and YGrid:
            %   - origin, extents, deltas, size and axes are inferred
            %   - optionally pass units
            %
            % 2. pass XAxis and YAxis:
            %   - coordinates, origin, extents, deltas, size are inferred
            %   - optionally pass units
            
            p = inputParser;
            
            addOptional(p, 'x_grid', [], @(x)ismatrix(x) && isnumeric(x));
            addOptional(p, 'y_grid', [], @(x)ismatrix(x) && isnumeric(x));
            addParameter(p, 'x_axis', [], @isvector);
            addParameter(p, 'y_axis', [], @isvector);
            addParameter(p, 'x_name', 'x', @isstr);
            addParameter(p, 'y_name', 'y', @isstr);
            addParameter(p, 'x_unit', '', @isstr);
            addParameter(p, 'y_unit', '', @isstr);
            addParameter(p, 'domain', common.Domain.Spatial, ...
                @(x)isa(x, 'common.Domain'));
            
            parse(p, varargin{:});
            
            x_grid = p.Results.x_grid;
            y_grid = p.Results.y_grid;
            
            % method 1
            % coordinates provided
            % extents, deltas, size and abscissae are inferred
            % units are optional
            if ~isempty(x_grid) && ~isempty(y_grid)
                
                if any(cellfun(@(x)~isempty(p.Results.(x)), ...
                        {'x_axis', 'y_axis'}))
                    error('If grids are passed, axes must not be.');
                end
            
            % method 2
            % axes provided
            % grids, extents, deltas and size are inferred
            % units are optional
            elseif ~isempty(p.Results.x_axis) && ~isempty(p.Results.y_axis)
                
                if any(cellfun(@(x)~isempty(p.Results.(x)), ...
                        {'x_grid', 'y_grid'}))
                    error('If axes are passed, grids must not be.');
                end
                
                % create grid
                [x_grid, y_grid] = meshgrid( ...
                    p.Results.x_axis, ...
                    p.Results.y_axis);
                
            else
                
                error(['There are two ways to instantiate a grid: 1. ' ...
                    'pass x_grid and y_grid (optional arguments) or 2.' ...
                    ' pass x_axis and y_axis (key-value pairs). The ' ...
                    'passed arguments did not match either pattern.']);
                
            end
            
            [x_extent, y_extent, x_delta, y_delta, coord_size] = ...
                obj.infer_props(x_grid, y_grid);
            
            obj.XGrid = x_grid;
            obj.YGrid = y_grid;
            obj.XAxis = x_grid(1, :);
            obj.YAxis = y_grid(:, 1);
            obj.XExtent = x_extent;
            obj.YExtent = y_extent;
            obj.XDelta = x_delta;
            obj.YDelta = y_delta;
            obj.Size = coord_size;
            obj.XName = p.Results.x_name;
            obj.YName = p.Results.y_name;
            obj.XUnit = p.Results.x_unit;
            obj.YUnit = p.Results.y_unit;
            obj.Domain = p.Results.domain;
            
        end
        
        function frequency_grid = ft(obj)
            % returns a Grid that is the Fourier transform of the parent
            
            % xr = obj.XExtent(2) - obj.XExtent(1);
            % yr = obj.YExtent(2) - obj.YExtent(1);
            
            n_x = numel(obj.XAxis);
            n_y = numel(obj.YAxis);
            
            frequency_grid = common.Grid( ...
                'x_axis', ( - n_x / 2 : n_x / 2 - 1) ./ obj.XDelta ./ n_x, ...
                'y_axis', ( - n_y / 2 : n_y / 2 - 1) ./ obj.YDelta ./ n_y, ...
                'x_name', ['f' obj.XName], ...
                'y_name', ['f' obj.YName], ...
                'x_unit', ['1/' obj.XUnit], ...
                'y_unit', ['1/' obj.YUnit], ...
                'domain', common.Domain.Frequency);
            
        end
        
        function spatial_grid = ift(obj)
            % returns a Grid that is the Fourier transform of the parent
            
            xr = obj.XExtent(2) - obj.XExtent(1);
            yr = obj.YExtent(2) - obj.YExtent(1);
            
            x_name = obj.XName;
            y_name = obj.YName;
            x_unit = obj.XUnit;
            y_unit = obj.YUnit;
            
            if strcmp(x_name(1), 'f')
                x_name = x_name(2:end);
            end
            if strcmp(y_name(1), 'f')
                y_name = y_name(2:end);
            end
            
            if strcmp(x_unit(1:2), '1/')
                x_unit = x_unit(3:end);
            end
            if strcmp(y_unit(1:2), '1/')
                y_unit = y_unit(3:end);
            end
            
            spatial_grid = common.Grid( ...
                'x_axis', linspace(0, xr, numel(obj.XAxis)), ...
                'y_axis', linspace(0, yr, numel(obj.YAxis)), ...
                'x_name', x_name, ...
                'y_name', y_name, ...
                'x_unit', x_unit, ...
                'y_unit', y_unit);
            
        end
        
        function resized = resize(obj, scale)
            
            n_x = ceil(numel(obj.XAxis) * scale);
            n_y = ceil(numel(obj.YAxis) * scale);
            x_axis = linspace(obj.XExtent(1), obj.XExtent(2), n_x);
            y_axis = linspace(obj.YExtent(1), obj.YExtent(2), n_y)';
            resized = common.Grid('x_axis', x_axis, 'y_axis', y_axis, ...
                'x_name', obj.XName, 'y_name', obj.YName, ...
                'x_unit', obj.XUnit, 'y_unit', obj.YUnit, ...
                'domain', obj.Domain);
            
        end

        function plot(obj)
            % draws the unit vectors and sets the axis limits
            
            composite = zeros(obj.Size(1), obj.Size(2), 3);
            xx = obj.XGrid ./ max(abs(obj.XGrid(:)));
            yy = obj.YGrid ./ max(abs(obj.YGrid(:)));
            c = xx;
            m = -xx;
            y = yy;
            composite(:, :, 1) = (1 - c);
            composite(:, :, 2) = (1 - m);
            composite(:, :, 3) = (1 - y);
            
            imagesc(obj.XAxis, obj.YAxis, composite ./ max(composite(:)));
            
            if isempty(obj.XUnit)
                x_unit = '';
            else
                x_unit = [', ' obj.XUnit];
            end
            if isempty(obj.YUnit)
                y_unit = '';
            else
                y_unit = [', ' obj.YUnit];
            end
            
            xlabel([obj.XName x_unit]);
            ylabel([obj.YName y_unit]);
            
        end
        
        function is_equal = eq(obj, other)
            
            if isempty(other)
                
                is_equal = false;
                
            else
            
                domains_equal = obj.Domain == other.Domain;

                try
                    x_grid_equal = obj.XGrid == other.XGrid;
                    y_grid_equal = obj.YGrid == other.YGrid;
                    grids_equal = all(x_grid_equal(:)) && all(y_grid_equal(:));
                catch
                    grids_equal = false;
                end

                units_equal = strcmp(obj.XUnit, other.XUnit) ...
                    && strcmp(obj.YUnit, other.YUnit);

                is_equal = domains_equal && grids_equal && units_equal;
                
            end
            
        end
    end
    
    methods (Static)
        
        function [x_extent, y_extent, x_delta, y_delta, coord_size] = ...
                infer_props(x_grid, y_grid)
            
            % check grid dimensions
            x_dims = ndims(x_grid);
            y_dims = ndims(y_grid);
            if x_dims ~= 2
                error('x_grid must be a 2D array.');
            end
            if y_dims ~= 2
                error('y_grid must be a 2D array.');
            end
            
            % check grid sizes
            if ~all(size(x_grid) == size(y_grid))
                error(['The sizes of x_grid and y_grid (passed or ' ...
                    'inferred) must be the same.']);
            end
            
            % check grid regularity
            x_delta = diff(x_grid, 1, 2);
            y_delta = diff(y_grid, 1, 1);
            x_delta = uniquetol(x_delta, mean(x_delta(:)) * 1e-7);
            y_delta = uniquetol(y_delta, mean(y_delta(:)) * 1e-7);
            if numel(x_delta) ~= 1
                error(['x_grid must be regular, i.e., diff(x_grid, ' ...
                    '1, 2) must have a single unique value.']);
            end
            if numel(y_delta) ~= 1
                error(['y_grid must be regular, i.e., diff(y_grid, ' ...
                    '1, 2) must have a single unique value.']);
            end
            
            % set extents
            x_extent = [min(x_grid(:)) max(x_grid(:))];
            y_extent = [min(y_grid(:)) max(y_grid(:))];
            
            % set size
            coord_size = size(x_grid);
            
        end
        
    end
    
end
