from config import SearchParameters, SearchMode, SearchType


class QueryBuilder:
    """Builds search queries based on parameters."""
    
    @staticmethod
    def build_search_query(params: SearchParameters) -> str:
        """Build search query based on search parameters."""
        query = params.query
        
        if params.mode == SearchMode.DATE_RANGE:
            if params.start_date:
                query += f" since:{params.start_date}"
            if params.end_date:
                query += f" until:{params.end_date}"
        
        return query
    
    @staticmethod
    def get_search_type(params: SearchParameters) -> SearchType:
        """Get search type based on search mode."""
        if params.mode == SearchMode.LATEST:
            return SearchType.LATEST
        else:  # Both DATE_RANGE and POPULAR use TOP
            return SearchType.TOP