#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
from gi.repository import Gio


def get_reflex_list():
    return [
        "fpemud-vcc",
    ]


def get_reflex_properties(name):
    if name == "fpemud-vcc":
        return {
            "need-plugin": ["mesh"],
            "protocol": "fpemud-vcc",
            "role": "p2p-endpoint",
        }
    else:
        assert False


def get_reflex_object(fullname):
    if fullname == "fpemud-vcc":
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def __init__(self):
        if os.getuid() == 0:
            self.watchPathList = {
                "/etc": [
                    "skel",					# directories
                    "ssl/certs",
                    "mtab",					# files
                    "UTC",
                ]
                "/var/lib/portage/world",
            }
            self.dataDir = "/var/cache/fpemud-vcc"
        else:
            self.watchPathList = {
                
            }
            self.dataDir = "~/.cache/fpemud-vcc"

        self.monitor = None
        self.submDict = dict()

    def on_init(self):
		self._sendToServer()
		self._addMonitors()

    def on_fini(self):
		if len(self.monitors) > 0:
			self._removeMonitors()
		if self.sendTimer is not None:
			GLib.source_remove(self.sendTimer)
			self.sendTimer = None

    def on_receive_message_from_peer(self, message):
        obj = json.loads(message)

	def _sendToServer(self):
		tmpDir = self.getTmpDir()
		try:
			VccUtil.copyDir("/etc", os.path.join(tmpDir, "etc"), self.etcIgnoreList)
			VccUtil.copyFileWithDir("/", "var/lib/portage/world", tmpDir)

			# compress to tar object
			sf = StringIO()
			with tarfile.open(mode='w:bz2', fileobj=sf) as f:
				f.add(os.path.join(tmpDir, "etc"), "etc")
				f.add(os.path.join(tmpDir, "var"), "var")

			# get uid gid info
			uidDict = dict()
			gidDict = dict()
			if True:
				uidSet, gidSet = VccUtil.getDirUidGidSet(tmpDir)
				for uid in uidSet:
					uidDict[uid] = pwd.getpwuid(uid)[0]
				for gid in gidSet:
					gidDict[gid] = grp.getgrgid(gid)[0]

			obj = _FpssClientCfgObject()
			obj.content = sf.getvalue()
			obj.uidDict = uidDict
			obj.gidDict = gidDict
			self.sendObject(obj)
		finally:
			VccUtil.removeDirContent(tmpDir)

	def _addMonitors(self):
		assert len(self.monitors) == 0
		self.monitors["etc"] = VccDirMonitor("/etc", self._monitorEvent)
		self.monitors["world"] = VccFileMonitor("/var/lib/portage/world", self._monitorEvent)
