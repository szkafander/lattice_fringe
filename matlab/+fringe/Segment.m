classdef  Segment
    
    properties
        Index
        Endpoints
        A
        B
        Centroid
        Orientation
        Slope
        Parent
        VectorForm
        LineForm
    end
    
    methods
        
        function obj = Segment(index, endpoints, parent)
            obj.Index = index;
            obj.Endpoints = endpoints;
            obj.Parent = parent;
            obj.A = endpoints(1, :);
            obj.B = endpoints(2, :);
            
            obj.VectorForm = obj.Endpoints([1 3 2 4]);
            obj.Orientation = obj.calc_orientation();
            obj.Centroid = obj.calc_centroid();
            obj.Slope = obj.calc_slope();
            obj.LineForm = obj.get_parallel_through('centroid');
        end
        
        function orientation = calc_orientation(obj)
            orientation = utils.get_orientation(obj.Endpoints);
        end
        
        function centroid = calc_centroid(obj)
            centroid = 0.5 * (obj.A + obj.B);
        end
        
        function slope = calc_slope(obj)
            slope = (obj.B(2) - obj.A(2)) / (obj.B(1) - obj.A(1));
        end
        
        function normal = get_normal_through(obj, point)
            % point is 'A', 'B' or 'centroid
            switch point
                case 'A'
                    point = obj.A;
                case 'B'
                    point = obj.B;
                case 'centroid'
                    point = obj.Centroid;
            end
            slope = obj.Slope;
            if slope == 0
                dx = 0;
                dy = 1;
            else
                dx = 1;
                dy = - 1 / slope;
            end
            normal = [point(1) point(2) dx dy];
        end
        
        function line_ = get_parallel_through(obj, point)
            % point is 'A', 'B' or 'centroid
            switch point
                case 'A'
                    point = obj.A;
                case 'B'
                    point = obj.B;
                case 'centroid'
                    point = obj.Centroid;
            end
            slope = obj.Slope;
            if slope == 0
                dx = 1;
                dy = 0;
            elseif isinf(slope)
                dx = 0;
                dy = 1;
            else
                dx = 1;
                dy = slope;
            end
            line_ = [point(1) point(2) dx dy];
        end
        
        function side = which_side_is_point(obj, point)
            side = sign((point(1) - obj.A(1)) * (obj.B(2) - obj.A(2)) ...
                - (point(2) - obj.A(2)) * (obj.B(1) - obj.A(1)));
        end
        
        function is_in_front = is_other_in_front_of_this(obj, segment)
            line_1 = obj.get_normal_through('A');
            line_2 = obj.get_normal_through('B');
            int_1 = intersectLineEdge(line_1, segment.VectorForm);
            int_2 = intersectLineEdge(line_2, segment.VectorForm);
            is_in_front = ~(any(isnan(int_1)) && any(isnan(int_2)));
            is_in_front = is_in_front || ...
                utils.is_point_between_parallel_lines(line_1, line_2, segment.A) ...
                || utils.is_point_between_parallel_lines(line_1, line_2, segment.B);
        end
        
        function distance = distance_from(obj, segment)
            distance = sqrt(sum( (obj.Centroid - segment.Centroid) .^2 ));
        end
        
        function distance = squared_distance_from(obj, segment)
            distance = sum( (obj.Centroid - segment.Centroid) .^2 );
        end
        
        function distance = parallel_distance_from(obj, segment)
            distance = distancePointLine(segment.Centroid, obj.LineForm);
        end
        
        function plot(obj, varargin)
            plot(obj.Endpoints(:,1), obj.Endpoints(:,2), 'ow-', 'LineWidth', 2, varargin{:});
        end
        
    end
    
end
