'''Test idlelib.textview.

Since all methods and functions create (or destroy) a TextViewer, which
is a widget containing multiple widgets, all tests must be gui tests.
Using mock Text would not change this.  Other mocks are used to retrieve
information about calls.

Coverage: 94%.
'''
from idlelib import textview as tv
from test.support import requires, findfile
requires('gui')

import unittest
import os
from tkinter import Tk, Button
from idlelib.idle_test.mock_idle import Func
from idlelib.idle_test.mock_tk import Mbox_func

def setUpModule():
    global root
    root = Tk()
    root.withdraw()

def tearDownModule():
    global root
    root.update_idletasks()
    root.destroy()  # Pyflakes falsely sees root as undefined.
    del root


class TV(tv.TextViewer):  # Used in TextViewTest.
    transient = Func()
    grab_set = Func()
    wait_window = Func()

class TextViewTest(unittest.TestCase):

    def setUp(self):
        TV.transient.__init__()
        TV.grab_set.__init__()
        TV.wait_window.__init__()

    def test_init_modal(self):
        view = TV(root, 'Title', 'test text')
        self.assertTrue(TV.transient.called)
        self.assertTrue(TV.grab_set.called)
        self.assertTrue(TV.wait_window.called)
        view.Ok()

    def test_init_nonmodal(self):
        view = TV(root, 'Title', 'test text', modal=False)
        self.assertFalse(TV.transient.called)
        self.assertFalse(TV.grab_set.called)
        self.assertFalse(TV.wait_window.called)
        view.Ok()

    def test_ok(self):
        view = TV(root, 'Title', 'test text', modal=False)
        view.destroy = Func()
        view.Ok()
        self.assertTrue(view.destroy.called)
        del view.destroy  # Unmask real function.
        view.destroy()


class ViewFunctionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.orig_error = tv.showerror
        tv.showerror = Mbox_func()

    @classmethod
    def tearDownClass(cls):
        tv.showerror = cls.orig_error
        del cls.orig_error

    def test_view_text(self):
        # If modal True, get tk error 'can't invoke "event" command'.
        view = tv.view_text(root, 'Title', 'test text', modal=False)
        self.assertIsInstance(view, tv.TextViewer)
        view.Ok()

    def test_view_file(self):
        test_dir = os.path.dirname(__file__)
        testfile = os.path.join(test_dir, 'test_textview.py')
        view = tv.view_file(root, 'Title', testfile, modal=False)
        self.assertIsInstance(view, tv.TextViewer)
        self.assertIn('Test', view.textView.get('1.0', '1.end'))
        view.Ok()

        # Mock showerror will be used; view_file will return None.
        testfile = os.path.join(test_dir, '../notthere.py')
        view = tv.view_file(root, 'Title', testfile, modal=False)
        self.assertIsNone(view)


class ButtonClickTextViewTest(unittest.TestCase):
    _utest = True

    def setUp(self):
        self.view = None
        self.called = False

    def tearDown(self):
        if self.view:
            self.view.destroy()

    def test_view_text_bind_with_button(self):
        def _command():
            self.called = True
            self.view = tv.view_text(root, 'TITLE_TEXT', 'COMMAND', _utest=self._utest)
        button = Button(root, text='BUTTON', command=_command)
        button.invoke()

        self.assertEqual(self.called, True)
        self.assertEqual(self.view.title(), 'TITLE_TEXT')
        self.assertEqual(self.view.textView.get('1.0', '1.end'), 'COMMAND')

    def test_view_file_bind_with_button(self):
        def _command():
            fn = findfile('CREDITS.txt', 'idlelib')
            self.called = True
            self.view = tv.view_file(root, 'TITLE_FILE', fn, _utest=self._utest)
        button = Button(root, text='BUTTON', command=_command)
        button.invoke()

        self.assertEqual(self.called, True)
        self.assertEqual(self.view.title(), 'TITLE_FILE')
        self.assertEqual(self.view.textView.get('1.0', '1.end'),
                         'Guido van Rossum, as well as being the creator of the '
                         'Python language, is the')


if __name__ == '__main__':
    unittest.main(verbosity=2)
