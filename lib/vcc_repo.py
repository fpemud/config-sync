#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
from vcc_util import VccUtil


class VccRepo:

	def __init__(self, name, dir_name, change_callback, pull_complete_callback):
		assert os.path.exists(dir_name)
		self.name = name
		self.dirName = dir_name
		self.changeCallback = change_callback
		self.pullCompleteCallback = pull_complete_callback

		self.serverProc = None
		self.pullTaskRunner = TaskRunner(None, None, self._onPullTaskRun, self._onPullTaskRunnerGoIdle)

	def dispose(self):
		assert self.serverProc is None
		self.pullTaskRunner.stop()
		self.pullTaskRunner = None

	def pull_from(self, peer_name, ip, port):
		self.pullThread.add_task(peer_name, ip, port)

	def start_server(self):
		port = getFreeSocketPort("tcp")

        cmd = "/usr/bin/git"
		cmd += " --export-all"        self.bStop = False

		cmd += " --strict-paths"
		cmd += " --export-all"
		# cmd += " --listen=%s"				# fixme, should only listen on one address
		cmd += " --port=%d" % (port)
		cmd += " --base-path=%s" % (self.dirName)
		cmd += " \"%s\"" % (self.dirName)
        self.serverProc = subprocess.Popenpull_complete_callback(cmd)
		
		return port

	def stop_server(self):
		self.serverProc.terminate()
		self.serverProc.wait()
		self.serverProc = None

    def start_monitor(self, change_callback):
        pass

    def stop_monitor(self):
        pass

	def _onPullTaskRun(self, dummy, peer_name, ip, port):
		_callGit(self.dir_name, "remote add peer git://%s:%d" % (ip, port), "stdout")
		while True:
			rc, out = _callGit(self.repoObj.dir_name, "pull peer master", "retcode+stdout")
			if rc == 0:
				break
			print(out)			# fixme
			time.sleep(10)
		_callGit(self.repoObj.dir_name, "remote remove peer", "stdout")

	def _onPullTaskRunnerGoIdle(self, dummy):
		if self.pullCompleteCallback is not None:
			self.pullCompleteCallback()

	def _onChange(self, monitor, file, other_file, event_type):
		if self.pullTaskRunner.is_running():
			return
        if event_type not in _validEvent():
			return
		_callGit(self.dirName, "add .", "stdout")
		_callGit(self.dirName, "commit -a -m \"%s\"" % ("none"), "stdout")
		self.change_callback()


class _PullThread(threading.Thread):

	def __init__(self, repoObj):
		self.repoObj = repoObj
		self.pullQueue = queue.Queue()
		self.pullStop = False
		self.pullCompleteIdleHandler = None

	def add(peer_name, ip, port):
		self.pullQueue.put((peer_name, ip, port))

	def stop(self):
		self.pullQueue.put(None)
		self.pullStop = None

	def run(self):
		while not self.repoObj.pullStop:
			data = self.pullQueue.get()
			if data is None:
				break
			peer_name, ip, port = data

			try:
			finally:
				self.pullQueue.task_done()
				if len(self.pullQueue) == 0 and self.repoObj.pullCompleteIdleHandler is None:
					self.repoObj.pullCompleteIdleHandler = GLib.idle_add(self._pullCompleteIdleCallback)

	def _pullCompleteIdleCallback(self):
		if self.repoObj.pullCompleteCallback is not None:
			self.repoObj.pullCompleteCallback(self.repoObj.name)



		self.repoObj.pullCompleteIdleHandler = None
		return False


def _callGit(dir_name, command, shellMode=""):
    gitDir = os.path.join(dir_name, ".git")
    cmdStr = "/bin/git --git-dir=\"%s\" --work-tree=\"%s\" %s"%(gitDir, dir_name, command)
    return VccUtil.shell(cmdStr, shellMode)

def _validEvent():
	return [
		Gio.FileMonitorEvent.CHANGES_DONE_HINT,
		Gio.FileMonitorEvent.DELETED,
		Gio.FileMonitorEvent.CREATED,
		Gio.FileMonitorEvent.ATTRIBUTE_CHANGED
	]













class VccRepo:

	STATUS_CLEAN = 0
	STATUS_CONFLICT = 1
	STATUS_DIRTY = 2
	STATUS_METADATA_DIRTY = 3

	@staticmethod
	def create_repo(dir_name):
		assert os.path.isabs(dir_name)
		assert os.path.isdir(dir_name)
		assert VccUtil.isDirEmpty(dir_name)

		VccRepo._callGit(dir_name, "init", "stdout")
		VccUtil.touchFile(os.path.join(dir_name, ".metadata"))
		VccRepo._callGit(dir_name, "add .", "stdout")
		VccRepo._callGit(dir_name, "commit -a -STATUS_CONFLICTm \"first commit of %s\" "%(dir_name), "stdout")
		VccRepo._git2vcc(dir_name)

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
				return self.STATUS_DIRTYSTATUS_CONFLICT
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
			self._callGit(self.dirName, "statuSTATUS_CONFLICTs")
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
		remotedir_name = None
		try:
			VccRepo._vcc2git(self.dirName)
			remotedir_name = self._getRemoteDir()
			VccRepo._vcc2git(remotedir_name)

			self._callGit(self.dirName, "pull --no-commit", "retcode+stdout")
			self._applyMetaData()
		finally:
			if remotedir_name is not None:
				VccRepo._git2vcc(remotedir_name)
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
					pdir = os.path.dir_name(f)
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

	def _storeMetaDataImpl(self, dir_name, pdir_name, ignoreList, cfgObj):
		"""dir_name is absolute path of directory, pdir_name is relative path of directory"""

		for fb in sorted(os.listdir(dir_name)):
			f = os.path.join(dir_name, fb)
			fr = os.path.join(pdir_name, fb)
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
