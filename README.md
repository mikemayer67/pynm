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

#### Example 1: Simple function callback

    from pynm import NotificationManager
    
    def cb_func(key,*args,*kwargs):
        # do something
        return
        
    nm = NotificationManager.share
    
    notification_key = "<<MyEvent>>"
    nm.register(notification_key, cb_func, 1, 2, 3, x=4, y=5, z=6)
    
    # when <<MyEvent>> notification is posted, cb_func will be invoked with the following parameters
    #   key will be set to <<MyEvent>>
    #   args will be set to (1,2,3)
    #   kwargs will be set to {"x":4, "y":5, "z":6}
    
#### Example 2: Callable object callback

    from pynm import NotificationManager
    
    class X:
        def __call__(self,key,color="blue",flavor="vanilla",weight=None,x=0,y=0,z=0):
            # do something
            return
        
    nm = NotificationManager.share
    
    notification_key = "<<MyEvent>>"
    x = X()
    nm.register(notification_key, x, 1, 2, priority=3, x=4, y=5)
    
    # when <<MyEvent>> notification is posted, X.__call__ will be invoked with the following parameters
    #   self will be set to x
    #   key will be set to <<MyEvent>>
    #   color will be set to 1
    #   flavor will be set to 2
    #   weight will default to None (unless set when the notification is posted)
    #   x will be set to 4 (unless overridden when the notification is posted)
    #   y will be set to 5 (unless overridden when the notification is posted)
    #   z will default to 0 (unless set when the notification is posted)
    
#### Example 3: Instance method callback

    from pynm import NotificationManager
    
    class X:
        def cb_func(self,key,*args,**kwargs):
            # do something
            return
        
    nm = NotificationManager.share
    
    notification_key = "<<MyEvent>>"
    x = X()
    nm.register(notification_key, x.cb_func)
    
    # when <<MyEvent>> notification is posted, X.cb_func will be invoked with the following parameters
    #   self will be set to x
    #   key will be set to <<MyEvent>>
    #   args will be set to ()
    #   kwargs will be set to {}
    
#### Example 4: Class method callback

    from pynm import NotificationManager
    
    class X:
        @classmethod
        def cb_func(cls,key,*args,**kwargs):
            # do something
            return
        
    nm = NotificationManager.share
    
    notification_key = "<<MyEvent>>"
    x = X()
    nm.register(notification_key, X.cb_func, 1, 2, 3, x=4, y=5, z=6)
    
 
    nm.register(notification_key, x.cb_func)
    
    # when <<MyEvent>> notification is posted, X.cb_func will be invoked with the following parameters
    #   cls will be set to X
    #   key will be set to <<MyEvent>>
    #   args will be set to ()
    #   kwargs will be set to {}
    
#### Example 5: Callback object

    from pynm import NotificationManager
    from pynm import Callback
    
    def cb_func(key,*args,*kwargs):
        # do something
        return
        
    nm = NotificationManager.share
    
    notification_key = "<<MyEvent>>"
    cb = Callback(cb_func,1, 2, 3, x=4, y=5, z=6)
    x = X()
    nm.register(notification_key, cb, priority=10)
    
    # when <<MyEvent>> notification is posted, X.cb_func will be invoked with the following parameters
    #   cls will be set to X
    #   key will be set to <<MyEvent>>
    #   args will be set to (1,2,3)
    #   kwargs will be set to {"x":4, "y":5, "z":6}
    



### Callback
