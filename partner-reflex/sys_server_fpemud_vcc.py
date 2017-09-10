#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import pwd
import grp
import tarfile
import lockfile
from datetime import datetime
from StringIO import StringIO
from gi.repository import GLib
from sn_module import SnModule
from sn_module import SnModuleInstance
from sn_module import SnRejectException
sys.path.append('/usr/lib/fpemud-vcc')
from vcc_util import VccUtil
from vcc_util import VccRepo
from vcc_param import VccParam

class ModuleInstanceObject(SnModuleInstance):

	def onInit(self):
		param = VccParam()
		param.loadConfig()

		# check fpemud-vcc configuration
		if param.ncfsDir is None:
			raise Exception("invalid fpemud-vcc configuration file")
		if not os.path.exists(param.ncfsDir):
			raise Exception("NCFS directory does not exist")
		if not os.path.exists(param.runDir):
			os.mkdir(param.runDir)

		# define global variables
		self.ncfsDir = param.ncfsDir
		self.realPath = os.path.join(self.ncfsDir, self.getPeerName())
		self.tmpPath = os.path.join(self.ncfsDir, ".%s"%(self.getPeerName()))
		self.ncfsCommitPipeFile = os.path.join(param.runDir, "%s.fifo"%(self.getPeerName()))
		self.ncfsCommitPipe = _NcfsCommitPipe(self.ncfsCommitPipeFile, self.onNcfsCommit)

	def onActive(self):
		bCreateReal = False
		bCreateTmp = False

		# lock operation
		lock = lockfile.LockFile(self.ncfsDir)
		lock.acquire()
		try:
			# create real-path and tmp-path
			if not os.path.exists(self.realPath) or not VccRepo.is_repo(self.realPath):
				VccUtil.mkDirAndClear(self.realPath)
				VccRepo.create_repo(self.realPath)
				bCreateReal = True
			if bCreateReal or not os.path.exists(self.tmpPath) or not VccRepo.is_repo(self.tmpPath):
				VccUtil.mkDirAndClear(self.tmpPath)
				VccRepo.create_repo(self.tmpPath)
				bCreateTmp = True

			# bind to each other
			if bCreateReal:
				repo = VccRepo(self.realPath)
				repo.bind_to(self.tmpPath)
			if bCreateTmp:
				repo = VccRepo(self.tmpPath)
				repo.bind_to(self.realPath)

			# add commit pipe
			self.ncfsCommitPipe.init()
		finally:
			lock.release()

	def onInactive(self):
		self.ncfsCommitPipe.dispose()
		self.ncfsCommitPipe = None

	def onRecv(self, dataObj):
		if dataObj.__class__.__name__ == "_FpssClientCfgObject":
			# lock operation
			lock = lockfile.LockFile(self.ncfsDir)
			lock.acquire()
			try:
				repoReal = VccRepo(self.realPath)
				repoTmp = VccRepo(self.tmpPath)

				# create extra user & group
				for uname in dataObj.uidDict.values():
					try:
						pwd.getpwnam(uname)
					except KeyError:
						print "**** debug u " + uname
						assert False									# fixme, craate user
				for gname in dataObj.gidDict.values():
					try:
						grp.getgrnam(gname)
					except KeyError:
						print "**** debug g " + gname
						assert False									# fixme, craate group

				# extract client files to tmp-path
				VccUtil.removeDirContent(self.tmpPath, VccRepo.get_ignore_list())
				sf = StringIO(dataObj.content)
				with tarfile.open(mode="r:bz2", fileobj=sf) as f:
					f.extractall(self.tmpPath)

				# transform uid & gid
				uidMap = dict()
				gidMap = dict()
				for uid, uname in dataObj.uidDict.items():
					uidMap[uid] = pwd.getpwnam(uname).pw_uid
				for gid, gname in dataObj.gidDict.items():
					gidMap[gid] = grp.getgrnam(gname).gr_gid
				VccUtil.replaceDirUidGid(self.tmpPath, uidMap, gidMap)

				# commit
				repoTmp.metadata_store()
				if repoTmp.is_dirty():
					repoTmp.commit("Commit at %s"%(datetime.now()))

				# push to real-path
				if repoReal.is_dirty():
					return
				repoReal.pull()

				# send to client
				self._sendToClient()
			finally:
				lock.release()
		else:
			assert False

	def onNcfsCommit(self):
		assert not VccRepo(self.realPath).is_dirty()
		self._sendToClient()
		return True

	def _sendToClient(self):
		repoReal = VccRepo(self.realPath)
		repoTmp = VccRepo(self.tmpPath)

		# check if real-path is dirty
		if repoReal.is_dirty():
			return

		# pull from real-path
		repoTmp.pull()
		assert not repoTmp.is_dirty()		# tmp-path should never be in dirty/conflict state

		# compress to tar file
		sf = StringIO()
		with tarfile.open(mode='w:bz2', fileobj=sf) as f:
			f.add(os.path.join(self.tmpPath, "etc"), "etc")
			f.add(os.path.join(self.tmpPath, "var"), "var")

		# get uid gid info
		uidDict = dict()
		gidDict = dict()
		if True:
			uidSet, gidSet = VccUtil.getDirUidGidSet(self.tmpPath, VccRepo.get_ignore_list())
			for uid in uidSet:
				uidDict[uid] = pwd.getpwuid(uid)[0]
			for gid in gidSet:
				gidDict[gid] = grp.getgrgid(gid)[0]

		# send to client
		obj = _FpssServerCfgObject()
		obj.content = sf.getvalue()
		obj.uidDict = uidDict
		obj.gidDict = gidDict
		self.sendObject(obj)

class _NcfsCommitPipe:

	def __init__(self, pipeFile, commitFunc):
		self.pipeFile = pipeFile
		self.commitFunc = commitFunc
		self.inf = None
		self.inh = None

	def init(self):
		os.mkfifo(self.pipeFile)
		self.inf = open(self.pipeFile, "rb")
		self.inh = GLib.io_add_watch(self.inf, GLib.IO_IN | _flagError, myRecvFunc)

	def dispose(self):
		GLib.source_remove(self.inh)
		self.inf.close()

	def _recvFunc(self, source, cb_condition):
		assert (cb_condition & _flagError) == 0
		source.read(1)		# consume 1 byte
		self.commitFunc()
		return True

class _FpssServerCfgObject:
	content = None				# str
	uidDict = None				# dict<int,str>
	gidDict = None				# dict<int,str>

_flagError = GLib.IO_PRI | GLib.IO_ERR | GLib.IO_HUP | GLib.IO_NVAL

