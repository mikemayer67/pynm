# Python Notification Manager

The notification manager registers listeners to receive callbacks if and
when a given notification key is received. 

The power of the notificaiton manager is that it does not require the 
source of the notifcation to know anything about what (if anything) may
be listening for the notification.  This decouples the logic of events
occurring and the logic of how to respond to those events.

## Overview

### Registered callbacks
Each registered callback consists of:
  - the **notification key** for which is should be invoked
    - it is *anticipated* that this will be string or numeric value
    - it *could* theoretically be anything that is hashable (*this has not been tested*)
  - the **function** to be called when the callback is invoked
    - regular functions
    - class methods
      - instance methods (*`self` will be the first argument passed*)
      - class methods (*`cls` will be the first argument passed*)
      - static methods
  - a **priority value**
  - **optional arguments** to be passed to the invoked function
    - positional arguments will be passed immediately after the keyword
    - keyword arguments may be overridden when a notification is posted
  
### Posting a notification

When the notification manager is sent a notificaion key to post, it invokes
all of the callbacks associated with that key. The notification request may
also include additional positional and/or keyword arguments.

If more than one callback is registered with a given key:
  - callbacks with higher priority will be invoked before those with lower priority
  - the order of invocation for callbcks of the same priority is not defined
  
If positional arguments are included with the notification request, they will
be passed to the callback function after the notification key and any positional
argument specified when registering the callback.

If keyword arguments are included with the notificaiton request, they too will
be passed to the callback function.  If any are in conflict with a keyword
argument specified when registering the callback, the value specified when
requesting the notifciation will take precedence.

### Notification Manager Instances

There are two options for using a notificatioon manager:
- create one (or more) using the `NotificationManager` constructor (init) method
- use the shared instance, which will be created on demand

Unless there is a need for multiple notification managers, use of the 
shared instance is recommended.  This avoids the need to thread
references throughout your code to wherever the manager might be needed.

## Usage

### Starting a Notification Manager

The first step in using Python Notificaton Manager is to either construct a `NotificationManager` 
object or to get a reference to the shared `NotifcationManager`.
```
from pynm import NotificationManager
nm = NotificationManager()
```
or
```
from pynm import NotificationManager
nm = NotificationManager.shared
```

Note that the constructor takes an optional name parameter which can later be accessed through the 
`name` property.  This serves no functional purpose.  It exists soley as a way of identifying the
notification manager as needed.
```
from pynm import NotificationManager
nm = NotificationManager("Hermes")

print(f"My notification manager's name is {nm.name}")
```
    
> My notification manager's name is Hermes

### Registering a callback

Callbacks are registered using NotificationManager's register method.  
```
register(self, key, callback, *args, priority=0, **kwargs)
    Registers a new notification callback
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
```

#### Examples
```
from pynm import NotificationManager
from pynm import Callable

def cb_func(key,*args,*kwargs):
    # do something
    return
    
class X:
    def __call__(self,key,*args,**kwargs):
        # do something
        return
        
    def cb_method(self,key,color="blue",flavor="vanilla",weight=None,x=0,y=0,z=0):
        # do something
        return
        
    @classmethod
    def cb_Method(cls,key,*args,**kwargs):
        # do something
        return
    
nm = NotificationManager.shared

event = "<<MyEvent>>"

# Example 1: Simple function callback
nm.register(event, cb_func, 1, 2, 3, x=4, y=5, z=6)

# Example 2: Callable object callback
x = X()
nm.register(event, x, priority=3)

# Example 3: Instance method callback
nm.register(event, x.cb_method, 1, 2, priority=3, x=4, y=5)

# Example 4: Class method callback
nm.register(event, X.cb_Method, 1, 2, 3, x=4, y=5, z=6)

# Example 5: Callback object
cb = Callback(cb_func, 1, z=8)
nm.register(notification_key, cb, priority=10)

# Example 6: Another simple function callback (for a different notification key)
nm.register("<<Junk>>", cb_func, x=100)
```

### Listing notification keys   
A list of all the notification keys which currently have registered callbacks
is available through NotificationManager's key property

#### Example
```
print(nm.keys)
```
will return (*based on the examples above*)
```
("<<MyEvent>>", "<<Junk>>")
```
    
### Posting a notification

Notification are posted using NotificationManager's notify method.
```
notify(self, key, *args, **kwargs)
    Invokes the callbacks associated with the specified key
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
```

#### Example
```
from pynm import NotificationManager
    
nm = NotificationManager.shared

event = "<<MyEvent>>"

# First posting: no additional parameters
nm.notify(event)

# Second posting: additional parameters
nm.notify(event,"hello",y=10,z=20)

# Third posting: the other notification key
nm.notify("<<Junk>>")

# Fourth posting: an unregistered notification key
nm.notify("Christmas",date="12/25")
```
    
This will yield the following callback invocations  (*note the order resulting from the priority settings*)
```
cb_func("<<MyEvent>>",1,z=8)                    # from posting 1, example 5 (pri=10)
X.__call__(x,"<<MyEvent>>")                     # from posting 1, example 2 (pri=3)
X.cb_method(x,"<<MyEvent>>",1,2,x=4,y=5)        # from posting 1, example 3 (pri=3)
cb_func("<<MyEvent>>",1,2,3,x=4,y=5,z=6)        # from posting 1, example 1 (pri=0)
X.cb_Method(X,"<<MyEvent>>",1,2,3,x=4,y=5,z=6)  # from posting 1, example 4 (pri=0)
    
cb_func("<<MyEvent>>",1,"hello",y=10,z=20)                # from posting 2, example 5 (pri=10)
X.__call__(x,"<<MyEvent>>","hello",y=10,z=20)             # from posting 2, example 2 (pri=3)
X.cb_method(x,"<<MyEvent>>",1,2,"hello",x=4,y=10,z=20)    # from posting 2, example 3 (pri=3)
cb_func("<<MyEvent>>",1,2,3,"hello",x=4,y=10,z=20)        # from posting 2, example 1 (pri=0)
X.cb_Method(X,"<<MyEvent>>",1,2,3,"hello",x=4,y=10,z=20)  # from posting 2, example 4 (pri=0)
  
cb_func("<<Junk>>",x=100)    # from posting 3, example 6
  
# (*nothing* from posting 4)
```

### Unregistering a callback
Callback registrations can be removed using NotificationManager's forget method
```
forget(self, key=None, priority=None, cb_id=None, callback=None)
    Forgets the specified callbacks that match the specified criteria
    Args:
        key (str): notification key
        priority (float): used to determine order of callback invocation
        cb_id (int): callback id returned when it was registered
        callback (Callback or callable): registered callback

    Raises:
        AssertionError if both cb_id and callback are specified

    If no criteria are specified, this has the same effect
    as calling `reset` but is not as efficient.
```

To remove **all** callbacks at once, NotificationManager's reset method is
more efficient as it does not need to traverse its internal dictionary
removing each callback individually.

#### Examples
```
from pynm import NotificationManager

nm = NotificationManager.shared

# Forget all <<Junk>> callbacks
nm.forget(key="<<Junk>>")

# Forget all priority 3 callbacks
nm.forget(priority=3)

# Forget all callbacks which invoke cb_func
nm.forget(callback=cb_func)

# Forget all "<<MyEvent>> callbacks which invoke cb_func
nm.forget(callback=cb_func, key="<<MyEvent>>"

# Forget all callbacks (*the inefficient way*)
nm.forget()

# Forget all callbacks (*the efficient way*)
nm.reset()
```

### Creating a Callback instance

The Callback class provides a means of creating a simple reusable callback.
It provides only two methods:
```
__init__(self, func, *args, **kwargs)
    Callback constructor
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
```
and
```
__call__(self, *args, key=None, **kwargs)
    Invokes the callback function
    Args:
        key (str): (optional) keyword to be passed to the callback function
        args (list): Positional arguments passed to the callback function
        kwargs (dict): Keyword arguments passed to the callback function
    
    If the keyword is specified, it will be passed as the very first 
    argument to the callback function.
    
    The postitional arguments specified here will be passed to the callback
    function after any positional arguments specified when the callback
    instance was created.
    
    The keyword arguments specified here will be overridden by any
    keyword argument of the same name that are specified when the callback
    is invoked.
```
#### Examples
```
from pynm import NotificationManager
from pynm import Callback

def cb_func(key,*args,*kwargs):
    # do something
    return

cb = Callback(cb_func,1,2,x=4,y=5)
NotificationManager.shared("<<MyEvent>>",cb)

# Somewhere else in the code
# This will invoke cb_func("<<MyEvent>>",1,2,3,x=4,y=5,z=6)
NotificationManager.notify("<<MyEvent>>",3,z=6)
```

While Callback is intended to support NotificationManager it could be used
on its own. 
```
from pynm import NotificationManager
from pynm import Callback

def cb_func(*args,*kwargs):
    # do something
    return

cb = Callback(cb_func,1,2,x=4,y=5)

# Somewhere else in the code
# This will invoke cb_func(1,2,3,x=4,y=5,z=6)
cb(3,z=6)

# Similarly, but also provding the invocation key
# This will invoke cb_func("my_key",1,2,3,x=4,y=5,z=6)
cb(3,z=6,key="my_key")

```
