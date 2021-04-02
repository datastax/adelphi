class SelectionException(Exception):
    pass


class KeyspaceSelectionException(SelectionException):
    """Exception indicinating an error in the selection of keyspaces"""
    pass


class TableSelectionException(SelectionException):
    """Exception indicinating an error in the selection of tables"""
    pass


class ExportException(Exception):
    pass
