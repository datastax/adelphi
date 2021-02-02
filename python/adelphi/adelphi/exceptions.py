class TooManyKeyspacesException(Exception):
    """Exception indicinating that too many keyspaces were passed to the exporter"""
    pass

class TooManyTablesException(Exception):
    """Exception indicinating that too many tables were passed to the exporter"""
    pass
