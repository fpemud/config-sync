#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
from gi.repository import Gio
sys.path.append('/usr/lib/config-sync')
from vcc_param import VccParam
from vcc_repo_local import VccLocalRepoManager
from vcc_userlock import VccUserLock


def get_reflex_list():
    return [
        "config-sync",
    ]


def get_reflex_properties(name):
    if name == "config-sync":
        return dict()
    else:
        assert False


def get_reflex_object(fullname):
    if fullname.startswith("config-sync"):
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def on_init(self):
        self.param = VccParam()

        if not os.path.exists(self.param.dataDir):
            os.makedirs(self.param.dataDir)

        self.ulock = VccUserLock(self.param, self.on_user_lock, self.on_user_unlock)

        self.mobj = VccLocalRepoManager(self.param)
        self.mobj.bringRepoOnline()

    def on_fini(self):
        self.mobj.bringRepoOffline()
        self.ulock.dispose()

    def on_user_lock(self):
        pass

    def on_user_unlock(self):
        pass

