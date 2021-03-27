class ApiConnectionError(Exception):
    """Base error for this module"""
    
    pass


class IdError(ApiConnectionError):
    """invalid ID was given"""

    def __init__(self, servise: str, invalid_id: list):
        self.service = servise
        self.invalid_id = invalid_id

    def __repr__(self):
        return f"IDs: {', '.join(self.invalid_id)} are invalid for {self.service} \n"

    __str__ = __repr__


class CreateSpreadSheetError(ApiConnectionError):
    """could't create a spread sheet"""
    
    def __init__(self, menssage=None):
        if menssage is None:
            self.menssage = self.__doc__
        else:
            self.menssage = menssage        

    def __repr__(self):
        return self.menssage

    __str__ = __repr__
