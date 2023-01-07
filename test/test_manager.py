import unittest

from pynm import NotificationManager
from pynm import Callback

def null_cb():
    pass

cb_hist = list()
def reset_hist():
    cb_hist.clear()

def func_cb(key,*,x="",y=""):
    cb_hist.append(f"{key}:{x}|{y}")

class Accumulator:
    def __init__(self,name=""):
        self.name = name

    def __str__(self):
        return f"Accumulator object with name {self.name}"

    def __call__(self,key,*,x="",y=""):
        cb_hist.append(f"{key}:{self.name}|{x}|{y}")

class Tests(unittest.TestCase):
    def setUp(self):
        reset_hist()

    def assertHistory(self,*args):
        a = 0
        b = None
        for arg in args:
            b = a + len(arg)
            if type(arg) is set:
                self.assertEqual(set(cb_hist[a:b]),arg)
            else:
                self.assertEqual(cb_hist[a:b],arg)
            a = b

    def test_shared(self):
        NotificationManager._shared = None
        nm = NotificationManager.shared
        self.assertIsNotNone(NotificationManager._shared)
        self.assertEqual(nm.name,"shared")
        self.assertEqual(id(nm), id(NotificationManager._shared))
        nm = NotificationManager()
        self.assertNotEqual(id(nm), id(NotificationManager._shared))

    def test_name(self):
        nm = NotificationManager()
        self.assertIsNone(nm.name)
        nm = NotificationManager("test")
        self.assertEqual(nm.name,"test")

    def test_keys(self):
        nm = NotificationManager()
        self.assertEqual(len(nm.keys),0)
        nm.register("<<Test>>",null_cb)
        self.assertEqual(nm.keys,{"<<Test>>"})
        nm.register("<<Test2>>",null_cb,priority=5)
        self.assertEqual(nm.keys,{"<<Test>>","<<Test2>>"})

    def test_reset(self):
        nm = NotificationManager()
        self.assertEqual(len(nm.keys),0)
        nm.register("<<Test>>",null_cb)
        nm.register("<<Test2>>",null_cb,priority=5)
        self.assertGreater(len(nm.keys),0)
        nm.reset()
        self.assertEqual(len(nm.keys),0)

    def test_func_callback_simple(self):
        nm = NotificationManager()
        nm.register("<<Test>>",func_cb)
        nm.notify("<<Test>>")
        self.assertHistory(["<<Test>>:|"])

    def test_func_callback_invalid(self):
        nm = NotificationManager()
        nm.register("<<Test>>",func_cb)

        with self.assertLogs(level="WARNING") as cm:
            nm.notify("<<Test>>",z=5)
            nm.notify("<<Test>>",cow=5)
        self.assertEqual(len(cm.records),2)
        for rec in cm.records:
            self.assertTrue(
                rec.message.startswith(
                    "Exception raised while invoking notification callback"
                )
            )

    def test_multi_pri_callbacks(self):
        nm = NotificationManager()
        seq = (100,200,-100,50,-100)
        for pri in seq:
            nm.register("<<Test>>",func_cb,priority=pri,x=pri)

        nm.notify("<<Test>>")
        self.assertHistory([
            f"<<Test>>:{p}|" for p in sorted(seq,reverse=True)
        ])

    def test_multi_target_callbacks(self):
        nm = NotificationManager()
        a = Accumulator("a")
        b = Accumulator("b")

        # note that the third register replaces the first one
        nm.register("<<Test>>",func_cb)
        nm.register("<<Test>>",a)
        nm.register("<<Test>>",b)
        nm.register("<<Test>>",a,priority=100,x="pri")
        nm.register("<<Test>>",b,x="abc")

        nm.notify("<<Test>>",y=1)
        nm.notify("<<Test>>",y=2)

        self.assertHistory(
            ["<<Test>>:a|pri|1"],
            {"<<Test>>:|1", "<<Test>>:a||1","<<Test>>:b||1","<<Test>>:b|abc|1"},
            ["<<Test>>:a|pri|2"],
            {"<<Test>>:|2","<<Test>>:a||2","<<Test>>:b||2","<<Test>>:b|abc|2"},
        )

    def test_class_callback_callable(self):
        nm = NotificationManager()
        a = Accumulator("a")

        nm.register("<<Test>>",a)
        nm.notify("<<Test>>")
        self.assertHistory(["<<Test>>:a||"])

    def test_class_callback_method(self):
        nm = NotificationManager()
        a = Accumulator("a")

        nm.register("<<Test>>",a)
        nm.notify("<<Test>>")
        self.assertHistory(["<<Test>>:a||"])

    def test_class_callback_invalid(self):
        nm = NotificationManager()
        a = Accumulator("a")

        nm.register("<<Test>>",Accumulator.__call__)
        with self.assertLogs(level="WARNING") as cm:
            nm.notify("<<Test>>")
        self.assertEqual(len(cm.records),1)
        self.assertTrue(
            cm.records[0].message.startswith(
                "Exception raised while invoking notification callback"
            )
        )

    def test_func_callback_args(self):
        nm = NotificationManager()
        nm.register("<<TestXY>>",func_cb,x="hello",y="world")
        nm.register("<<TestX>>",func_cb,x="hello")
        nm.register("<<TestY>>",func_cb,y="world")

        nm.notify("<<TestXY>>")
        nm.notify("<<TestX>>")
        nm.notify("<<TestX>>",y="moon")
        nm.notify("<<TestY>>")
        nm.notify("<<TestY>>",x="goodnight")

        self.assertHistory([
                "<<TestXY>>:hello|world",
                "<<TestX>>:hello|",
                "<<TestX>>:hello|moon",
                "<<TestY>>:|world",
                "<<TestY>>:goodnight|world",
            ]
        )

    def test_func_callback_arg_override(self):
        nm = NotificationManager()
        nm.register("<<TestXY>>",func_cb,x="hello",y="world")
        nm.register("<<TestX>>",func_cb,x="hello")
        nm.register("<<TestY>>",func_cb,y="world")

        nm.notify("<<TestXY>>",x="goodnight",y="moon")
        nm.notify("<<TestXY>>",x="goodnight")
        nm.notify("<<TestXY>>",y="moon")
        nm.notify("<<TestX>>",x="goodnight",y="moon")
        nm.notify("<<TestX>>",x="goodnight")
        nm.notify("<<TestX>>",y="moon")
        nm.notify("<<TestY>>",x="goodnight",y="moon")
        nm.notify("<<TestY>>",x="goodnight")
        nm.notify("<<TestY>>",y="moon")

        self.assertHistory([
            "<<TestXY>>:goodnight|moon",
            "<<TestXY>>:goodnight|world",
            "<<TestXY>>:hello|moon",
            "<<TestX>>:goodnight|moon",
            "<<TestX>>:goodnight|",
            "<<TestX>>:hello|moon",
            "<<TestY>>:goodnight|moon",
            "<<TestY>>:goodnight|world",
            "<<TestY>>:|moon",
        ])

    def test_forget_key(self):
        nm = NotificationManager()
        a = Accumulator("a")
        cb = Callback(func_cb,x="cb")

        nm.register("<<Test1>>",func_cb,x=2,priority=2)
        nm.register("<<Test1>>",func_cb,x=1,priority=1)
        nm.register("<<Test1>>",a,x=1,priority=1)
        nm.register("<<Test1>>",cb,priority=1)
        nm.register("<<Test2>>",func_cb,x=2,priority=2)
        nm.register("<<Test2>>",func_cb,x=1,priority=1)
        nm.register("<<Test2>>",a,x=1,priority=1)
        nm.register("<<Test2>>",cb,priority=1)

        nm.notify("<<Test1>>",y=1)
        nm.notify("<<Test2>>",y=1)
        nm.forget(key="<<Test2>>")
        nm.notify("<<Test1>>",y=2)
        nm.notify("<<Test2>>",y=2)

        self.assertHistory(
            ["<<Test1>>:2|1"],
            {"<<Test1>>:1|1","<<Test1>>:a|1|1","<<Test1>>:cb|1"},
            ["<<Test2>>:2|1"],
            {"<<Test2>>:1|1","<<Test2>>:a|1|1","<<Test2>>:cb|1"},
            # forget
            ["<<Test1>>:2|2"],
            {"<<Test1>>:1|2","<<Test1>>:a|1|2","<<Test1>>:cb|2"},
        )

    def test_forget_priority(self):
        nm = NotificationManager()
        a = Accumulator("a")
        cb = Callback(func_cb,x="cb")

        nm.register("<<Test1>>",func_cb,x=2,priority=2)
        nm.register("<<Test1>>",func_cb,x=1,priority=1)
        nm.register("<<Test1>>",a,x=1,priority=1)
        nm.register("<<Test1>>",cb,priority=1)
        nm.register("<<Test2>>",func_cb,x=2,priority=2)
        nm.register("<<Test2>>",func_cb,x=1,priority=1)
        nm.register("<<Test2>>",a,x=1,priority=1)
        nm.register("<<Test2>>",cb,priority=1)

        nm.notify("<<Test1>>",y=1)
        nm.notify("<<Test2>>",y=1)
        nm.forget(priority=2)
        nm.notify("<<Test1>>",y=2)
        nm.notify("<<Test2>>",y=2)

        self.assertHistory(
            ["<<Test1>>:2|1"],
            {"<<Test1>>:1|1","<<Test1>>:a|1|1","<<Test1>>:cb|1"},
            ["<<Test2>>:2|1"],
            {"<<Test2>>:1|1","<<Test2>>:a|1|1","<<Test2>>:cb|1"},
            # forget
            {"<<Test1>>:1|2","<<Test1>>:a|1|2","<<Test1>>:cb|2"},
            {"<<Test2>>:1|2","<<Test2>>:a|1|2","<<Test2>>:cb|2"},
        )

    def test_forget_callback(self):
        nm = NotificationManager()
        a = Accumulator("a")
        cb = Callback(func_cb,x="cb")

        nm.register("<<Test1>>",func_cb,x=2,priority=2)
        nm.register("<<Test1>>",func_cb,x=1,priority=1)
        nm.register("<<Test1>>",a,x=1,priority=1)
        nm.register("<<Test1>>",cb,priority=1)
        nm.register("<<Test2>>",func_cb,x=2,priority=2)
        nm.register("<<Test2>>",func_cb,x=1,priority=1)
        nm.register("<<Test2>>",a,x=1,priority=1)
        nm.register("<<Test2>>",cb,priority=1)
        nm.notify("<<Test1>>",y=1)
        nm.notify("<<Test2>>",y=1)
        nm.forget(callback=func_cb)
        nm.notify("<<Test1>>",y=2)
        nm.notify("<<Test2>>",y=2)

        self.assertHistory(
            ["<<Test1>>:2|1"],
            {"<<Test1>>:1|1","<<Test1>>:a|1|1","<<Test1>>:cb|1"},
            ["<<Test2>>:2|1"],
            {"<<Test2>>:1|1","<<Test2>>:a|1|1","<<Test2>>:cb|1"},
            # forget
            ["<<Test1>>:a|1|2"],
            ["<<Test2>>:a|1|2"],
        )

    def test_forget_callback_id(self):
        nm = NotificationManager()
        a = Accumulator("a")
        cb = Callback(func_cb,x="cb")

        nm.register("<<Test1>>",func_cb,x=2,priority=2)
        cb_id = nm.register("<<Test1>>",func_cb,x=1,priority=1)
        nm.register("<<Test1>>",a,x=1,priority=1)
        nm.register("<<Test1>>",cb,priority=1)
        nm.register("<<Test2>>",func_cb,x=2,priority=2)
        nm.register("<<Test2>>",func_cb,x=1,priority=1)
        nm.register("<<Test2>>",a,x=1,priority=1)
        nm.register("<<Test2>>",cb,priority=1)

        nm.notify("<<Test1>>",y=1)
        nm.notify("<<Test2>>",y=1)
        nm.forget(cb_id=cb_id)
        nm.notify("<<Test1>>",y=2)
        nm.notify("<<Test2>>",y=2)

        self.assertHistory(
            ["<<Test1>>:2|1"],
            {"<<Test1>>:1|1","<<Test1>>:a|1|1","<<Test1>>:cb|1"},
            ["<<Test2>>:2|1"],
            {"<<Test2>>:1|1","<<Test2>>:a|1|1","<<Test2>>:cb|1"},
            # forget
            ["<<Test1>>:2|2"],
            {"<<Test1>>:a|1|2","<<Test1>>:cb|2"},
            ["<<Test2>>:2|2"],
            {"<<Test2>>:1|2","<<Test2>>:a|1|2","<<Test2>>:cb|2"},
        )

    def test_forget_multikey(self):
        nm = NotificationManager()
        a = Accumulator("a")
        cb = Callback(func_cb,x="cb")

        nm.register("<<Test1>>",func_cb,x=2,priority=2)
        nm.register("<<Test1>>",func_cb,x=1,priority=1)
        nm.register("<<Test1>>",a,x=1,priority=1)
        nm.register("<<Test1>>",cb,priority=1)
        nm.register("<<Test2>>",func_cb,x=2,priority=2)
        nm.register("<<Test2>>",func_cb,x=1,priority=1)
        nm.register("<<Test2>>",a,x=1,priority=1)
        nm.register("<<Test2>>",cb,priority=1)

        nm.notify("<<Test1>>",y=1)
        nm.notify("<<Test2>>",y=1)
        nm.forget(priority=2,key="<<Test2>>")
        nm.notify("<<Test1>>",y=2)
        nm.notify("<<Test2>>",y=2)

        self.assertHistory(
            ["<<Test1>>:2|1"],
            {"<<Test1>>:1|1","<<Test1>>:a|1|1","<<Test1>>:cb|1"},
            ["<<Test2>>:2|1"],
            {"<<Test2>>:1|1","<<Test2>>:a|1|1","<<Test2>>:cb|1"},
            # forget
            ["<<Test1>>:2|2"],
            {"<<Test1>>:1|2","<<Test1>>:a|1|2","<<Test1>>:cb|2"},
            {"<<Test2>>:1|2","<<Test2>>:a|1|2","<<Test2>>:cb|2"},
        )

