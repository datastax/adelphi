class SelectionException(Exception):
    pass

class KeyspaceSelectionException(SelectionException):
    """Exception indicinating an error in the selection of keyspaces"""
    def __init__(self, msg):
        super(KeyspaceSelectionException, self).__init__(msg)

class TableSelectionException(SelectionException):
    """Exception indicinating an error in the selection of tables"""
    def __init__(self, msg):
        super(TableSelectionException, self).__init__(msg)
