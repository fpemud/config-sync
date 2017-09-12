#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
from gi.repository import Gio
sys.path.append('/usr/lib/config-sync')
from vcc_param import VccParam


def get_reflex_list():
    return [
        "config-sync-for-peer",
    ]


def get_reflex_properties(name):
    if name == "config-sync-for-peer":
        return {
            "need-plugin": ["mesh"],
            "protocol": "config-sync",
            "role": "p2p-per-peer",
        }
    else:
        assert False


def get_reflex_object(fullname):
    if fullname.startswith("config-sync-for-peer."):
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def on_init(self):
        self.param = VccParam()
        if not os.path.exists(self.param.dataDir):
            os.makedirs(self.param.dataDir)
        self.repoObj = VccRemoteRepo(self.param, self.param.dataDir, self.peer_info["hostname"], self.peer_info["ip"])

    def on_fini(self):
        self.repoObj.dispose()


