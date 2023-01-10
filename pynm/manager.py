from .exceptions import NotificationKeyError
from .exceptions import RegistrationError
from .exceptions import CallbackFailed
from .callback import Callback

import logging

def id_generator():
    x = 0
    while True:
        x += 1
        yield x

class NotificationManager:
    """Manages invocation of callback functions in response to a notification

    The notification manager registers listeners to receive callbacks if and
    when a given notification key is received. 

    The power of the notificaiton manager is that it does not require the 
    source of the notifcation to know anything about what (if anything) may
    be listening for the notification.  This decouples the logic of events
    occurring and the logic of how to respond to those events.

    A registered callback consists of:
      - the function to be invoked
      - a priority value (default of 0)

    Mutiple callbacks may be registered for a given notification key.

    If more than one callback is registered with a given key:
      - They are invoked in order of decreasing priority.
      - The default priority is 0.
      - The callback order is not defined for callbacks of equal priority.

    When the callback is invoked, it will be passed the notification key
    as the sole positional argument.  All other arguments are passed
    by keyword.  The keyword arguments may be specified:
        - when the callback is first registered
        - when the notification is posted
        - in case of conflict, the latter takes precedence

    There is a shared notificaition manager that can be created on demand.
    Alternatively, notification manager instances can be created as desired.
    """
    _shared = None
    _ids = id_generator()

    def __init__(self,name=None):
        self._name = name
        self._queues = dict()

    @classmethod
    @property
    def shared(cls):
        """Returns the default (shared) NotificationManager instance"""
        if not cls._shared:
            cls._shared = NotificationManager("shared")
        return cls._shared

    @property
    def name(self):
        return self._name

    @property
    def keys(self):
        """Returns a set of all the currently registered notification keys"""
        return set(self._queues.keys())

    def register(self, key, callback, *args, priority=0, **kwargs):
        """Registers a new notification callback
        Args:
            key (str): notification key
            callback (Callback or callable): see below
            priority (float): used to determine order of callback invocation
            args (list): positional arguments passed to callback (optional)
            kwargs (dict): keyword arguments passed to callback (optional)

            The callback may be specified either as a Callback instance
            or as any callable function or method (bound or unbound).

        Returns:
            registration_id (int): unique id for each registered callback

        Raises: AssertionError if callback
            - is not callable
            - is an instance of Callable and args or kwargs are specified

        Any positional arguments specified here will be passed to the callback
        function immediately after the notification key.  They will appear 
        before any positional arguments specifed when the notification is
        invoked.

        Any keyword arguments specified here will be passed to the callback
        function, but may be overridden by any keyword arguments with the same 
        keyword specified when the notification is invoked.
        """
        if isinstance(callback,Callback):
            if args:
                raise RegistrationError("Cannot specify both Callback and args")
            if kwargs:
                raise RegistrationError("Cannot specify both Callback and kwargs")
        else:
            if not callable(callback):
                raise RegistrationError("callback must be callable")
            callback = Callback(callback,*args,**kwargs)

        try:
            priority = float(priority)
        except ValueError:
            raise RegistrationError(f"priority must be a float, not {priority}")

        try:
            queue = self._queues[key]
        except KeyError:
            queue = dict()
            self._queues[key] = queue

        try:
            pri_queue = queue[priority]
        except KeyError:
            pri_queue = dict()
            queue[priority] = pri_queue

        cb_id = next(self._ids)
        pri_queue[cb_id] = callback

        return cb_id


    def notify(self,key,*args,**kwargs):
        """Invokes the callbacks associated with the specified key
        Args:
            key(str): notification key
            args (list): positional arguments passed to callback (optional)
            kwargs (dict): keyword arguments passed to callback (optional)

        Raises: nothing
            If any of the invoked callbacks raise an exception, the
            exception will be logged, but otherwise ignored.

        Any positional arguments specified here will be passed to the callback
        function immediately after the notification key and any positional
        arguments specified when the callback was registered.

        Any keyword arguments specified here will be passed to the callback
        function. They will override any keyword arguments with the same
        keyword specified when the callback was registered.

        If there are no callbacks registered for the specified notification
        key, this method simply returns without doing anything else.
        """
        try:
            queue = self._queues[key]
        except KeyError:
            return

        for priority in sorted(queue.keys(),reverse=True):
            for cb_id,cb in queue[priority].items():
                try:
                    cb(*args,key=key,**kwargs)
                except CallbackFailed as e:
                    logging.warning(
                        "Exception raised while invoking notification callback\n"
                        + f"  key: {key}\n"
                        + f"  priority: {priority}\n"
                        + f"  callback: {cb_id}\n"
                        + f"  function: {e.callback}\n"
                        + f"  reason: {e.reason}"
                    )

    def reset(self):
        """Forgets ALL registered callbacks immediately"""
        self._queues = dict()


    def forget(self, key=None, priority=None, cb_id=None, callback=None):
        """Forgets the specified callbacks that match the specified criteria
        Args:
            key (str): notification key
            priority (float): used to determine order of callback invocation
            cb_id (int): callback id returned when it was registered
            callback (Callback or callable): registered callback

        Raises: 
            AssertionError if both cb_id and callback are specified 

        If no criteria are specified, this has the same effect
        as calling `reset` but is not as efficient.
        """
        assert cb_id is None or callback is None, (
            "Cannot specify both cb_id and callback"
        )

        keys = [key] if key is not None else list(self._queues.keys())
        for key in keys:
            self._forget_key(key,priority, cb_id, callback)

    def _forget_key(self,key, priority=None, cb_id=None, callback=None):
        """Internal method to support `forget`"""
        try:
            queue = self._queues[key]
        except KeyError:
            return

        priorities = [priority] if priority is not None else list(queue.keys())
        for priority in priorities:
            self._forget_priority(key,priority,cb_id,callback)

        if not self._queues[key]:
            del self._queues[key]

    def _forget_priority(self,key,priority,cb_id,callback):
        """Internal method to support `forget`"""
        if cb_id:
            self._forget_cb_id(key,priority,cb_id)
        elif callback:
            self._forget_callback(key,priority,callback)
        else:
            self._queues[key][priority].clear()

        if not self._queues[key][priority]:
            del self._queues[key][priority]

    def _forget_callback(self,key,priority,callback):
        """Internal method to support `forget`"""
        self._queues[key][priority] = {
            k:v
            for k,v in self._queues[key][priority].items()
            if id(v.func) != id(callback)
        }

    def _forget_cb_id(self,key,priority,cb_id):
        """Internal method to support `forget`"""
        try:
            del self._queues[key][priority][cb_id]
        except KeyError:
            pass

