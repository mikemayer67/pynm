import unittest

from pynm import Callback

from pynm.exceptions import CallbackFuncError
from pynm.exceptions import CallbackFailed

result = dict()
def func_cb(key,*args,**kwargs):
    result['key'] = key
    result['args'] = args
    result['kwargs'] = kwargs

def bad_cb(key,*args,**kwargs):
    assert False, "Just die already"

class ClassCB:
    def __init__(self):
        self.result = dict()

    def __call__(self,key,*args,**kwargs):
        self.result["invoked"] = "__call__"
        self.result['key'] = key
        self.result['args'] = args
        self.result['kwargs'] = kwargs

    def func(self,key,*args,**kwargs):
        self.result["invoked"] = "func"
        self.result['key'] = key
        self.result['args'] = args
        self.result['kwargs'] = kwargs

    def reset(self):
        self.result.clear()


class Tests(unittest.TestCase):

    def test_function_callback(self):
        result.clear()
        cb = Callback(func_cb)
        cb("<<Test>>")
        self.assertEqual( result, {
            'key':"<<Test>>",
            'args':(),
            'kwargs':{},
        })

    def test_callable_object(self):
        a = ClassCB()
        cb = Callback(a,1,2,x=1,y=2)
        cb("<<Test>>",3,4,y=3,z=4)
        self.assertEqual(a.result, {
            'invoked':'__call__',
            'key':"<<Test>>",
            'args':(1,2,3,4),
            'kwargs':{'x':1,'y':3,'z':4},
        })

    def test_instance_method(self):
        a = ClassCB()
        cb = Callback(a.func,1,2,x=1,y=2)
        cb("<<Test>>",3,4,y=3,z=4)
        self.assertEqual(a.result, {
            'invoked':'func',
            'key':"<<Test>>",
            'args':(1,2,3,4),
            'kwargs':{'x':1,'y':3,'z':4},
        })


    def test_callback_args(self):
        result.clear()
        cb = Callback(func_cb,1,2)
        cb("<<Test>>",3,4)
        self.assertEqual( result, {
            'key':"<<Test>>",
            'args':(1,2,3,4),
            'kwargs':{},
        })

    def test_callback_kwargs(self):
        result.clear()
        cb = Callback(func_cb,x=1,y=2)
        cb("<<Test>>",y=3,z=4)
        self.assertEqual( result, {
            'key':"<<Test>>",
            'args':(),
            'kwargs':{'x':1, 'y':3, 'z':4},
        })

    def test_invalid_func(self):
        result.clear()
        with self.assertRaises(CallbackFuncError) as cm:
            cb = Callback(1,2,3)
        with self.assertRaises(CallbackFuncError) as cm:
            cb = Callback("this")

    def test_callback_exception(self):
        result.clear()
        with self.assertRaises(CallbackFailed) as cm:
            cb = Callback(bad_cb)
            cb('<<Test>>')




