#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
from vcc_util import VccUtil


class VccRepo:

	def __init__(self, dirName):
		assert os.path.isabs(dirName)
		self.dirName = dirName

	def commit(self):
		_callGit(self.dirName, "add .", "stdout")
		_callGit(self.dirName, "commit -a -m \"%s\""%(message), "stdout")







def _callGit(dirName, command, shellMode=""):
    gitDir = os.path.join(dirName, ".git")
    cmdStr = "/bin/git --git-dir=\"%s\" --work-tree=\"%s\" %s"%(gitDir, dirName, command)
    return VccUtil.shell(cmdStr, shellMode)

def _vcc2git(dirName):
    os.rename(os.path.join(dirName, ".vcc"), os.path.join(dirName, ".git"))

def _git2vcc(dirName):
    if not os.path.exists(os.path.join(dirName, ".git")):
        return
    os.rename(os.path.join(dirName, ".git"), os.path.join(dirName, ".vcc"))



class VccRepo:

	STATUS_CLEAN = 0
	STATUS_CONFLICT = 1
	STATUS_DIRTY = 2
	STATUS_METADATA_DIRTY = 3

	@staticmethod
	def create_repo(dirName):
		assert os.path.isabs(dirName)
		assert os.path.isdir(dirName)
		assert VccUtil.isDirEmpty(dirName)

		VccRepo._callGit(dirName, "init", "stdout")
		VccUtil.touchFile(os.path.join(dirName, ".metadata"))
		VccRepo._callGit(dirName, "add .", "stdout")
		VccRepo._callGit(dirName, "commit -a -m \"first commit of %s\" "%(dirName), "stdout")
		VccRepo._git2vcc(dirName)

	@staticmethod
	def is_repo(dirName):
		assert os.path.isabs(dirName)
		assert os.path.isdir(dirName)

		if not os.path.isdir(os.path.join(dirName, ".vcc")):
			return False
		if not os.path.exists(os.path.join(dirName, ".metadata")):
			return False
		return True

	@staticmethod
	def get_ignore_list():
		return [ ".vcc", ".metadata" ]

	def __init__(self, dirName):
		assert os.path.isabs(dirName)
		assert VccRepo.is_repo(dirName)
		self.dirName = dirName

	def bind_to(self, remoteDirName):
		assert os.path.isabs(remoteDirName)
		assert VccRepo.is_repo(remoteDirName)

		try:
			VccRepo._vcc2git(self.dirName)
			VccRepo._vcc2git(remoteDirName)

			self._callGit(self.dirName, "remote add origin \"%s\""%(remoteDirName), "stdout")
			self._callGit(self.dirName, "fetch", "stdout")
			self._callGit(self.dirName, "branch --set-upstream-to=origin/master master", "stdout")
			self._callGit(self.dirName, "pull --no-edit", "stdout")
		finally:
			VccRepo._git2vcc(remoteDirName)
			VccRepo._git2vcc(self.dirName)

	def get_status(self):
		try:
			VccRepo._vcc2git(self.dirName)

			if not self._compareMetaData():
				return self.STATUS_METADATA_DIRTY

			ret = self._callGit(self.dirName, "status", "stdout")
			if re.search("^You have unmerged paths.$", ret, re.M) is not None:
				return self.STATUS_CONFLICT
			if re.search("^Changes to be committed:$", ret, re.M) is not None:
				return self.STATUS_DIRTY
			if re.search("^Untracked files:$", ret, re.M) is not None:
				return self.STATUS_DIRTY
			if re.search("^Changes not staged for commit:$", ret, re.M) is not None:
				return self.STATUS_DIRTY
			if re.search("^All conflicts fixed but you are still merging.$", ret, re.M) is not None:
				return self.STATUS_DIRTY

			return self.STATUS_CLEAN
		finally:
			VccRepo._git2vcc(self.dirName)

	def has_conflict(self):
		return self.get_status() in [ self.STATUS_CONFLICT ]

	def is_dirty(self):
		return self.get_status() in [ self.STATUS_CONFLICT, self.STATUS_DIRTY, self.STATUS_METADATA_DIRTY ]

	def status(self):
		try:
			VccRepo._vcc2git(self.dirName)
			assert self._compareMetaData()
			self._callGit(self.dirName, "add .", "stdout")
			self._callGit(self.dirName, "status")
		finally:
			VccRepo._git2vcc(self.dirName)

	def diff(self):
		try:
			VccRepo._vcc2git(self.dirName)
			assert self._compareMetaData()
			self._callGit(self.dirName, "add .", "stdout")
			self._callGit(self.dirName, "diff")
		finally:
			VccRepo._git2vcc(self.dirName)

	def pull(self):
		remoteDirName = None
		try:
			VccRepo._vcc2git(self.dirName)
			remoteDirName = self._getRemoteDir()
			VccRepo._vcc2git(remoteDirName)

			self._callGit(self.dirName, "pull --no-commit", "retcode+stdout")
			self._applyMetaData()
		finally:
			if remoteDirName is not None:
				VccRepo._git2vcc(remoteDirName)
			VccRepo._git2vcc(self.dirName)

	def reset(self):
		try:
			VccRepo._vcc2git(self.dirName)
			VccUtil.removeDirContent(self.dirName, [".git"])
			self._callGit(self.dirName, "reset --hard", "stdout")
		finally:
			VccRepo._git2vcc(self.dirName)

	def metadata_store(self):
		try:
			VccRepo._vcc2git(self.dirName)
			self._storeMetaData()
		finally:
			VccRepo._git2vcc(self.dirName)

	def metadata_apply(self):
		try:
			VccRepo._vcc2git(self.dirName)
			self._applyMetaData()
		finally:
			VccRepo._git2vcc(self.dirName)

	def _getRemoteDir(self):
		with open(os.path.join(self.dirName, ".git", "config")) as f:
			inSection = False
			for line in f:
				if line == "[remote \"origin\"]\n":
					inSection = True
				elif inSection and line.startswith("["):
					inSection = False
				elif inSection:
					m = re.match("^\turl = (.*)\n$", line)
					if m is not None:
						return m.group(1)
		assert False

	def _storeMetaData(self):
		"""Won't follow symbolic links"""

		ignoreList = self._internal_ignore_list()

		cfgObj = ConfigParser.RawConfigParser()
		self._storeMetaDataImpl(self.dirName, "", ignoreList, cfgObj)

		metadataFile = os.path.join(self.dirName, ".metadata")
		with open(metadataFile, "w") as f:
			cfgObj.write(f)

	def _applyMetaData(self):
		"""Won't follow symbolic links"""

		ignoreList = self._internal_ignore_list()

		metadataFile = os.path.join(self.dirName, ".metadata")
		cfgObj = ConfigParser.RawConfigParser()
		cfgObj.read(metadataFile)

		for fr in cfgObj.sections():
			f = os.path.join(self.dirName, fr)
			if any(x for x in ignoreList if fnmatch.fnmatch(f, x)):
				continue

			tname = cfgObj.get(fr, "tname")
			mode = cfgObj.get(fr, "mode")
			owner = cfgObj.get(fr, "owner")

			if tname == "symlink":
				assert VccUtil.isTrival(f) and os.path.islink(f)
			elif tname == "dir":
				if not os.path.exists(f):
					# create directory, but don't modify mtime of parent directory
					pdir = os.path.dirname(f)
					if pdir != self.dirName:
						tmtime = os.path.getmtime(pdir)
					os.mkdir(f)
					if pdir != self.dirName:
						VccUtil.setFileMtime(pdir, tmtime)
				else:
					assert VccUtil.isTrival(f) and os.path.isdir(f) and not os.path.islink(f)
			elif tname == "file":
				assert VccUtil.isTrival(f) and os.path.isfile(f) and not os.path.islink(f)
			else:
				assert False
			if not os.path.islink(f):
				VccUtil.shell("/bin/chmod %s \"%s\""%(mode, f))
			VccUtil.shell("/bin/chown -h %s \"%s\""%(owner, f))

	def _compareMetaData(self):
		"""Returns True means equal"""

		ignoreList = self._internal_ignore_list()

		cfgObj = ConfigParser.RawConfigParser()
		self._storeMetaDataImpl(self.dirName, "", ignoreList, cfgObj)

		metadataFile = os.path.join(self.dirName, ".metadata")
		if not os.path.exists(metadataFile):
			return False

		with open(metadataFile, "r") as f:
			sf = StringIO()
			cfgObj.write(sf)
			return f.read() == sf.getvalue()

	def _storeMetaDataImpl(self, dirName, pdirName, ignoreList, cfgObj):
		"""dirName is absolute path of directory, pdirName is relative path of directory"""

		for fb in sorted(os.listdir(dirName)):
			f = os.path.join(dirName, fb)
			fr = os.path.join(pdirName, fb)
			if any(x for x in ignoreList if fnmatch.fnmatch(f, x)):
				continue
			assert VccUtil.isTrival(f)

			tname = "dir" if (os.path.isdir(f) and not os.path.islink(f)) else "file"

			if os.path.islink(f):
				tname = "symlink"
			elif os.path.isdir(f):
				tname = "dir"
			elif os.path.isfile(f):
				tname = "file"
			else:
				assert False
			mode = oct(os.lstat(f).st_mode & 0777)
			username = pwd.getpwuid(os.lstat(f).st_uid)[0]
			grouppname = grp.getgrgid(os.lstat(f).st_gid)[0]

			cfgObj.add_section(fr)
			cfgObj.set(fr, "tname", tname)
			cfgObj.set(fr, "mode", mode)
			cfgObj.set(fr, "owner", "%s:%s"%(username, grouppname))
			#cfgObj.set(fr, "mtime", "")
			#cfgObj.set(fr, "xattr", "")

			if os.path.isdir(f) and not os.path.islink(f):
				self._storeMetaDataImpl(f, fr, ignoreList, cfgObj)

	def _internal_ignore_list(self):
		return [
			os.path.join(self.dirName, ".git"),
			os.path.join(self.dirName, ".metadata"),
		]
