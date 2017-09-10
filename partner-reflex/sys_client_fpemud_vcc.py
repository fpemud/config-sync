#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import pwd
import grp
import tarfile
from StringIO import StringIO
from gi.repository import GLib
from sn_module import SnModule
from sn_module import SnModuleInstance
from sn_module import SnRejectException
sys.path.append('/usr/lib/fpemud-vcc')
from vcc_util import VccUtil
from vcc_util import VccDirMonitor
from vcc_util import VccFileMonitor

class ModuleInstanceObject(SnModuleInstance):

	def onInit(self):
		self.monitors = dict()
		self.sendTimer = None

	def onActive(self):
		self._sendToServer()
		self._addMonitors()

	def onInactive(self):
		if len(self.monitors) > 0:
			self._removeMonitors()
		if self.sendTimer is not None:
			GLib.source_remove(self.sendTimer)
			self.sendTimer = None

	def onRecv(self, dataObj):
		if dataObj.__class__.__name__ == "_FpssServerCfgObject":
			if self.sendTimer is None:
				self._removeMonitors()
				self._recvFromServer(dataObj)
				self._addMonitors()
			else:
				pass	# local modification takes priority
		else:
			raise SnRejectException("invalid server data received")

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

	def _recvFromServer(self, dataObj):
		tmpDir = self.getTmpDir()
		try:
			# extract tar file
			sf = StringIO(dataObj.content)
			with tarfile.open(mode="r:bz2", fileobj=sf) as f:
				f.extractall(tmpDir)

			# check files
			if not os.path.isdir(os.path.join(tmpDir, "etc")):
				raise SnRejectException("directory \"/etc\" not in FpssServerCfgObject")
			if not os.path.exists(os.path.join(tmpDir, "var/lib/portage/world")):
				raise SnRejectException("file \"/var/lib/portage/world\" not in FpssServerCfgObject")
			for uname in dataObj.uidDict.values():
				try:
					pwd.getpwnam(uname)
				except KeyError:
					raise SnRejectException("extra username \"%s\"encountered"%(uname))
			for gname in dataObj.gidDict.values():
				try:
					grp.getgrnam(gname)
				except KeyError:
					raise SnRejectException("extra groupname \"%s\"encountered"%(gname))

			# transform uid & gid
			uidMap = dict()
			gidMap = dict()
			for uid, uname in dataObj.uidDict.items():
				uidMap[uid] = pwd.getpwnam(uname).pw_uid
			for gid, gname in dataObj.gidDict.items():
				gidMap[gid] = grp.getgrnam(gname).gr_gid
			VccUtil.replaceDirUidGid(tmpDir, uidMap, gidMap)

			# update files
			VccUtil.updateDir("/etc", os.path.join(tmpDir, "etc"), self.etcIgnoreList)
			VccUtil.copyFileWithDir(tmpDir, "var/lib/portage/world", "/")
		finally:
			VccUtil.removeDirContent(tmpDir)

	def _addMonitors(self):
		assert len(self.monitors) == 0
		self.monitors["etc"] = VccDirMonitor("/etc", self._monitorEvent)
		self.monitors["world"] = VccFileMonitor("/var/lib/portage/world", self._monitorEvent)

	def _removeMonitors(self):
		assert len(self.monitors) > 0
		for v in self.monitors.values():
			v.dispose()
		self.monitors.clear()

	def _monitorEvent(self):
		assert self.sendTimer is None
		self.sendTimer = GObject.timeout_add_seconds(60, _timerEvent)

	def _timerEvent(self):
		self._sendToServer()
		self.sendTimer = None
		return False

class _FpssClientCfgObject:
	content = None				# str
	uidDict = None				# dict<int,str>
	gidDict = None				# dict<int,str>

