#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
from gi.repository import Gio


class VccUserLock:

    def __init__(self, param, lock_callback, unlock_callback):
        self.param = param
        self.lock_callback = lock_callback
        self.unlock_callback = unlock_callback

        lockfile = os.path.join(self.param.dataDir, "userlock")
        self.monitor = Gio.File.new_for_path(lockfile).monitor_file(0, None)
        self.monitor.connect("changed", self._on_change)

        self.locked = os.path.exists(lockfile)

    def get_value(self):
        self.locked

    def dispose(self):
        self.monitor.cancel()

    def _on_change(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CREATED:
            self.locked = True
            self.lock_callback()
            return

        if event_type == Gio.FileMonitorEvent.DELETED:
            self.locked = False
            self.unlock_callback()
            return

        assert False
