# -*- coding: UTF-8 -*-

"""Framework-neutral :class:`Singleton` metaclass.

Kept independent from the configuration and the web framework so that the core
domain can use it without importing ``api`` or third-party packages.
"""

from abc import ABCMeta


class Singleton(ABCMeta):
    """Metaclass ensuring a single instance per class."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
