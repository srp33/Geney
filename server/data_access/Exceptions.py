
class ServerError(Exception):
    def __init__(self, message, code=500):
        super().__init__(message)
        self.__code = code
        self.__message = message
    
    @property
    def code(self):
        return self.__code

    @property
    def message(self):
        return self.__message

class RequestError(Exception):
    def __init__(self, message, code=400):
        super().__init__(message)
        self.__code = code
    
    @property
    def code(self):
        return self.__code 

    @property
    def message(self):
        return self.__message