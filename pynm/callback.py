from .exceptions import CallbackFuncError
from .exceptions import CallbackFailed

class Callback:
    """Simple class for for defining and invoking a callback function/method"""
    def __init__(self,func,*args,**kwargs):
        """Callback constructor
        Args:
            func (callable): The function (or method) to be invoked
            args (list): Positional arguments passed to the callback function
            kwargs (dict): Keyword arguments passed to the callback function

        The postitional arguments specified here will be passed to the callback
        function prior to any positional arguments specified when the callback
        instance is invoked.

        The keyword arguments specified here will be overridden by any
        keyword argument of the same name that are specified when the callback
        is invoked.
        """
        if not callable(func):
            raise CallbackFuncError(func)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self,key,*args,**kwargs):
        """Invokes the callback function
        Args:
            key (str): The notificaiton key which triggered the callback
            args (list): Positional arguments passed to the callback function
            kwargs (dict): Keyword arguments passed to the callback function

        The postitional arguments specified here will be passed to the callback
        function after any positional arguments specified when the callback
        instance was created.

        The keyword arguments specified here will be overridden by any
        keyword argument of the same name that are specified when the callback
        is invoked.
        """
        try:
            cb_args = self.args + args
            cb_kwargs = self.kwargs.copy()
            cb_kwargs.update(kwargs)
            self.func(key,*cb_args,**cb_kwargs)
        except Exception as e:
            raise CallbackFailed(self,e)


