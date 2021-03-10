classdef (Abstract) FilterBank
    
    properties (Abstract)
        
        Filters
        Abscissae
    
    end
    
    properties (Dependent)
        
        NumFilters
    
    end
    
    methods (Abstract)
        
        apply(obj)
    
    end
    
    methods (Static, Abstract)
        
        create(obj)
        
    end
    
    methods
        
        function num_filters = get.NumFilters(obj)
            
            num_filters = numel(obj.Filters);
            
        end
        
    end
    
end
