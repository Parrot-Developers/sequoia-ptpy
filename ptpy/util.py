'''This module holds general utilities'''
from threading import enumerate as threading_enumerate


def _main_thread_alive():
    return any(
        (i.name == "MainThread") and i.is_alive() for i in
        threading_enumerate())
