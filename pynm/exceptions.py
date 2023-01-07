class NotificationKeyError(Exception):
    def __init__(self,key):
        self.key = key
    def __repr__(self):
        return f"Unregistered notification key: {self.key}"

class RegistrationError(Exception):
    def __init__(self,reason):
        self.reason = reason
    def __repr__(self):
        return f"Failed to register callback: {reason}"

class CallbackFuncError(Exception):
    def __init__(self,func):
        self.func = func
    def __repr__(self):
        return f"Invalid callback function: {func} is not callable"

class CallbackFailed(Exception):
    def __init__(self,callback,reason):
        self.callback = callback
        self.reason = reason

