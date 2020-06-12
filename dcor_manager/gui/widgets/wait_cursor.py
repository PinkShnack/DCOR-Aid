import functools

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt


class ShowWaitCursor(object):
    def __enter__(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QApplication.processEvents()
        return self

    def __exit__(self, type, value, traceback):
        QApplication.restoreOverrideCursor()


def show_wait_cursor(func):
    """A decorator that starts and stops a wait cursor for a function call

    https://doc.qt.io/qt-5/qguiapplication.html#setOverrideCursor
    Every setOverrideCursor() must eventually be followed by a
    corresponding restoreOverrideCursor(), otherwise the stack
    will never be emptied.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with ShowWaitCursor():
            ret = func(*args, **kwargs)
        return ret
    return wrapper
