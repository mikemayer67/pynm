# Python Notification Manager

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
