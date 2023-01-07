# Python Notification Manager

The notification manager registers listeners to receive callbacks if and
when a given notification key is received. 

The power of the notificaiton manager is that it does not require the 
source of the notifcation to know anything about what (if anything) may
be listening for the notification.  This decouples the logic of events
occurring and the logic of how to respond to those events.

## Registered callbacks
### Each registered callback consists of:
  - the **notification key** for which is should be invoked
    - it is *anticipated* that this will be string or numeric value
    - it *could* theoretically be anything that is hashable (*this has not been tested*)
  - the **function** to be called when the callback is invoked
    - regular functions
    - lambda functions
    - class methods
      - instance methods (*`self` will be the first argument passed*)
      - class methods (*`cls` will be the first argument passed*)
      - static methods
    
  - a **priority value** (*callbacks with higher priority are invoked those with lower priority*)
  - **optional arguments** to be passed to the invoked function
    - positional arguments will be passed immediately after the keyword
    - keyword arguments may be overridden when a notification is posted
  
### Mutiple callbacks may be registered for a given notification key.

If more than one callback is registered with a given key:
  - callbacks are invoked in order of decreasing priority
  - The callback order is not defined for callbacks of equal priority.

When the callback is invoked, it will be passed the notification key
as the sole positional argument.  All other arguments are passed
by keyword.  The keyword arguments may be specified:
    - when the callback is first registered
    - when the notification is posted
    - in case of conflict, the latter takes precedence

There is a shared notificaition manager that can be created on demand.
Alternatively, notification manager instances can be created as desired.
