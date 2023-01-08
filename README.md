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

    from pynm import NotificationManager
    nm = NotificationManager()

or

    from pynm import NotificationManager
    nm = NotificationManager.shared

Note that the constructor takes an optional name parameter which can later be accessed through the 
`name` property.  This serves no functional purpose.  It exists soley as a way of identifying the
notification manager as needed.

    from pynm import NotificationManager
    nm = NotificationManager("Hermes")
    
    print(f"My notification manager's name is {nm.name}")
    
> My notification manager's name is Hermes

### Registering a callback

Callbacks are registered using NotificationManager's `regsister` method.  There are only two requied
positional parameters:

- key (str): the notification key
- callback: either a Callback object or any other *callable* python entitity
  - *the Callback class is described below* 

In addition, there is one optional keyword parameter:

- priority (float): used to determine order of callback invocation  (*see above*)

Any other positional arguments will become part of the callback itself and will be passed to the
callback function when it is invoked.  They will appear immediately following the notification key.

Similarly, any keyword arguments (*other than priority*) will become part of the callback and will
be passed to the callback function when it is invoked, unless overridden when the notification 
is posted (*see below*)

#### Example callback registrations

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
        
    nm = NotificationManager.share
    
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
    
### Posting a notification

Notification are posted using NotificationManager's `notify` method.  There is only one requied
positional parameter:

- key (str): the notification key

Any other positional arguments will be passed to the callback function when it is invoked.  
They will appear immediately following the notification key and any position parameters
specified when registering the callback.

Similarly, any keyword argument will be passed to the callback function when it is invoked.
If any are in conflict with keyword arguments specfified when registering the callback, the
values specified here will take precedence.

#### Example notification postings

    from pynm import NotificationManager
        
    nm = NotificationManager.share
    
    event = "<<MyEvent>>"
    
    # First posting: no additional parameters
    nm.notify(event)
    
    # Second posting: additional parameters
    nm.notify(event,"hello",y=10,z=20)
    
    # Third posting: the other notification key
    nm.notify("<<Junk>>")
    
    # Fourth posting: an unregistered notification key
    nm.notify("Christmas",date="12/25")
    
This will yield the following callback invocation  (*note the order resulting from the priority settings*)

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

### Forgetting (unregistering) a callback

### Callback
