#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
from gi.repository import Gio
sys.path.append('/usr/lib/config-sync')
from vcc_param import VccParam


def get_reflex_list():
    return [
        "config-sync",
    ]


def get_reflex_properties(name):
    if name == "config-sync":
        return {
            "need-plugin": ["mesh"],
            "protocol": "config-sync",
            "role": "p2p-endpoint",
        }
    else:
        assert False


def get_reflex_object(fullname):
    if fullname.startswith("config-sync."):
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def __init__(self):
        self.param = VccParam()

        self.monitor = None
        self.submDict = dict()

    def on_init(self):
		if not os.path.exists(self.param.dataDir):
			os.makedirs(self.param.dataDir)



		self._sendToServer()
		self._addMonitors()

    def on_fini(self):
		if len(self.monitors) > 0:
			self._removeMonitors()
		if self.sendTimer is not None:
			GLib.source_remove(self.sendTimer)
			self.sendTimer = None

	def _ensureLocalDir(self):
		localDir = os.path.join(self.param.dataDir, "localhost"):
		if not os.path.exists(self.param.localDir):
			VccRepo.create_repo(localDir)












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
