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
    - lambda functions
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
  
If positionl arguments are included with the notification request, they will
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
