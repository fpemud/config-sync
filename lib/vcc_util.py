#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import re
import pwd
import grp
import stat
import time
import shutil
import fnmatch
import subprocess
import pyinotify
import ConfigParser
from StringIO import StringIO


class VccUtil:

    @staticmethod
    def getFreeSocketPort(portType):
        if portType == "tcp":
            stlist = [socket.SOCK_STREAM]
        elif portType == "udp":
            stlist = [socket.SOCK_DGRAM]
        elif portType == "tcp+udp":
            stlist = [socket.SOCK_STREAM, socket.SOCK_DGRAM]
        else:
            assert False

        for port in range(10000, 65536):
            bFound = True
            for sType in stlist:
                s = socket.socket(socket.AF_INET, sType)
                try:
                    s.bind((('', port)))
                except socket.error:
                    bFound = False
                finally:
                    s.close()
            if bFound:
                return port

        raise Exception("no valid port")

    @staticmethod
    def getLogicalCwd():
        return VccUtil.shell("/usr/bin/pwd -L", "stdout").rstrip("\n")

    @staticmethod
    def copyToFile(srcFilename, dstFilename, mode=None):
        """Copy file to specified filename, and set file mode if required"""

        if not os.path.isdir(os.path.dirname(dstFilename)):
            os.makedirs(os.path.dirname(dstFilename))
        shutil.copy(srcFilename, dstFilename)
        if mode is not None:
            VccUtil.shell("/bin/chmod " + mode + " \"" + dstFilename + "\"")

    @staticmethod
    def touchFile(filename):
        assert not os.path.exists(filename)
        f = open(filename, 'w')
        f.close()

    @staticmethod
    def forceDelete(filename):
        if os.path.islink(filename):
            os.remove(filename)
        elif os.path.isfile(filename):
            os.remove(filename)
        elif os.path.isdir(filename):
            shutil.rmtree(filename)

    @staticmethod
    def ensureDir(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    @staticmethod
    def deleteDirIfEmpty(dirname):
        if os.listdir(dirname) == []:
            os.rmdir(dirname)

    @staticmethod
    def mkDirAndClear(dirname):
        VccUtil.forceDelete(dirname)
        os.mkdir(dirname)

    @staticmethod
    def isMountPoint(pathname):
        buf = VccUtil.shell("/bin/mount", "stdout")
        found = False
        for line in buf.split("\n"):
            m = re.match("^(.*) on (.*) type ", line)
            if m is None:
                continue
            if m.group(2) == pathname:
                found = True
                break
        return found

    @staticmethod
    def shell(cmd, flags=""):
        """Execute shell command"""

        assert cmd.startswith("/")

        # Execute shell command, throws exception when failed
        if flags == "":
            retcode = subprocess.Popen(cmd, shell = True).wait()
            if retcode != 0:
                raise Exception("Executing shell command \"%s\" failed, return code %d"%(cmd, retcode))
            return

        # Execute shell command, throws exception when failed, returns stdout+stderr
        if flags == "stdout":
            proc = subprocess.Popen(cmd,
                                    shell = True,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.STDOUT)
            out = proc.communicate()[0]
            if proc.returncode != 0:
                raise Exception("Executing shell command \"%s\" failed, return code %d, output %s"%(cmd, proc.returncode, out))
            return out

        # Execute shell command, returns (returncode,stdout+stderr)
        if flags == "retcode+stdout":
            proc = subprocess.Popen(cmd,
                                    shell = True,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.STDOUT)
            out = proc.communicate()[0]
            return (proc.returncode, out)

        assert False

    @staticmethod
    def isTrivalDir(filename):
        return (os.path.isdir(filename) and not os.path.islink(filename))

    @staticmethod
    def isTrivalFile(filename):
        """symlink is viewed as file"""

        if os.path.islink(filename):
            return True
        elif os.path.isdir(filename):
            return False
        elif stat.S_ISCHR(os.stat(filename).st_mode):
            return False
        elif stat.S_ISBLK(os.stat(filename).st_mode):
            return False
        elif stat.S_ISFIFO(os.stat(filename).st_mode):
            return False
        elif stat.S_ISSOCK(os.stat(filename).st_mode):
            return False
        else:
            return True

    @staticmethod
    def isTrival(filename):
        return VccUtil.isTrivalDir(filename) or VccUtil.isTrivalFile(filename)

    @staticmethod
    def getAbsPathList(dirname, pathList):
        pathList2 = []
        for i in range(0, len(pathList)):
            assert not os.path.isabs(pathList[i])
            pathList2.append(os.path.join(dirname, pathList[i]))
        return pathList2

    @staticmethod
    def isDirEmpty(dirName):
        return len(os.listdir(dirName)) == 0

#    @staticmethod
#    def getFileList(dirName, level, typeList):
#        """typeList is a string, value range is "d,f,l,a"
#           returns basename"""
#
#        ret = []
#        for fbasename in os.listdir(dirName):
#            fname = os.path.join(dirName, fbasename)
#
#            if os.path.isdir(fname) and level - 1 > 0:
#                for i in VccUtil.getFileList(fname, level - 1, typeList):
#                    ret.append(os.path.join(fbasename, i))
#                continue
#
#            appended = False
#            if not appended and ("a" in typeList or "d" in typeList) and os.path.isdir(fname):        # directory
#                ret.append(fbasename)
#            if not appended and ("a" in typeList or "f" in typeList) and os.path.isfile(fname):        # file
#                ret.append(fbasename)
#            if not appended and ("a" in typeList or "l" in typeList) and os.path.islink(fname):        # soft-link
#                ret.append(fbasename)
#
#        return ret

    @staticmethod
    def setFileMtime(filename, mtime):
        tstr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        VccUtil.shell("/bin/touch -h --date=\"%s\" \"%s\""%(tstr, filename), "stdout")

    @staticmethod
    def copyFile(srcFile, dstFile):
        """Copy srcFile to dstFile, meta-data is also copied
           dstFile will be overwritten if it already exists
           View symlink as file"""

        assert os.path.isabs(srcFile) and os.path.isabs(dstFile)
        assert VccUtil.isTrivalFile(srcFile)

        if os.path.islink(srcFile):
            if os.path.exists(dstFile):
                assert VccUtil.isTrivalFile(dstFile)
                os.remove(dstFile)
            os.symlink(os.readlink(srcFile), dstFile)
            os.lchown(dstFile, os.lstat(srcFile).st_uid, os.lstat(srcFile).st_gid)
            VccUtil.setFileMtime(dstFile, os.lstat(srcFile).st_mtime)
        elif os.path.isfile(srcFile):
            if os.path.exists(dstFile):
                assert VccUtil.isTrivalFile(dstFile)
            shutil.copy2(srcFile, dstFile)
            os.chown(dstFile, os.stat(srcFile).st_uid, os.stat(srcFile).st_gid)
        else:
            assert False

    @staticmethod
    def copyFileWithDir(srcDir, srcFile, dstDir):
        """For example, copyFileWithDir("/home/a", "var/log/a.log", "/home/b") will
           copy /home/a/var/log/a.log to /home/b/var/log/a.log and create all the related directories.
           The target file will be overwritten if it already exists
           meta-data of the file and related directories are also copied
           View symlink as file, don't support directory symlinks"""

        assert os.path.isabs(srcDir) and not os.path.isabs(srcFile) and os.path.isabs(dstDir)
        assert os.path.isdir(dstDir)

        # copy parent directories
        of = srcDir
        nf = dstDir
        for p in srcFile.split("/")[:-1]:
            of = os.path.join(of, p)
            nf = os.path.join(nf, p)
            assert VccUtil.isTrivalDir(of)
            if not os.path.exists(nf):
                os.mkdir(nf)
            else:
                assert VccUtil.isTrivalDir(nf)
            os.chown(nf, os.stat(of).st_uid, os.stat(of).st_gid)

        # copy file
        of = os.path.join(srcDir, srcFile)
        nf = os.path.join(dstDir, srcFile)
        VccUtil.copyFile(of, nf)

        # put "shutil.copystat" at end because mkdir/file-copy will change its parent dir's mtime
        of = srcDir
        nf = dstDir
        for p in srcFile.split("/")[:-1]:
            of = os.path.join(of, p)
            nf = os.path.join(nf, p)
            shutil.copystat(of, nf)

    @staticmethod
    def copyDir(srcDir, dstDir, ignoreList=[]):
        """Copy srcDir to dstDir, meta-data is also copied
           dstDir will be removed first if it already exists
           View symlink as file
           Elements in ignoreList are glob patterns"""

        assert os.path.isabs(srcDir) and os.path.isabs(dstDir)
        assert VccUtil.isTrivalDir(srcDir)

        ignoreList = VccUtil.getAbsPathList(srcDir, ignoreList)
        if os.path.exists(dstDir):
            assert VccUtil.isTrivalDir(dstDir)
            shutil.rmtree(dstDir)
        VccUtil._copyDirImpl(srcDir, dstDir, ignoreList)

    @staticmethod
    def _copyDirImpl(srcDir, dstDir, ignoreList):
        if os.path.islink(srcDir):
            VccUtil.copyFile(srcDir, dstDir)
        else:
            os.mkdir(dstDir)
            os.chown(dstDir, os.stat(srcDir).st_uid, os.stat(srcDir).st_gid)

            for fb in os.listdir(srcDir):
                sf = os.path.join(srcDir, fb)
                df = os.path.join(dstDir, fb)
                if any(x for x in ignoreList if fnmatch.fnmatch(sf, x)):
                    continue
                if VccUtil.isTrivalDir(sf):
                    VccUtil._copyDirImpl(sf, df, ignoreList)
                elif VccUtil.isTrivalFile(sf):
                    VccUtil.copyFile(sf, df)
                else:
                    assert False

            shutil.copystat(srcDir, dstDir)        # "shutil.copystat" at end because file-copy will change its parent dir's mtime
    
    @staticmethod
    def updateDir(oriDir, newDir, keepList=[]):
        """Update oriDir content by newDir content, meta-data is also updated
           Elements in keepList are glob patterns, and they should not appear in newDir
           View symlink as file
           newDir is at right side"""

        assert os.path.isabs(oriDir) and os.path.isabs(newDir)
        assert VccUtil.isTrivalDir(oriDir) and VccUtil.isTrivalDir(newDir)

        keepList = VccUtil.getAbsPathList(oriDir, keepList)
        VccUtil._updateDirImpl(oriDir, newDir, keepList)

    @staticmethod
    def _updateDirImpl(oriDir, newDir, keepAbsList):
        # fixme: should consider acl, sparse file, the above is same

        oset = set(os.listdir(oriDir))
        nset = set(os.listdir(newDir))

        right_dirs = []
        right_files = []
        left_dirs = []
        left_files = []
        common_dirs = []
        common_files = []
        for fb in (nset - oset):
            nf = os.path.join(newDir, fb)
            if VccUtil.isTrivalDir(nf):
                right_dirs.append(fb)
            elif VccUtil.isTrivalFile(nf):
                right_files.append(fb)
            else:
                assert False
        for fb in (oset - nset):
            of = os.path.join(oriDir, fb)
            if VccUtil.isTrivalDir(of):
                left_dirs.append(fb)
            elif VccUtil.isTrivalFile(of):
                left_files.append(fb)
            else:
                assert False
        for fb in (oset & nset):
            of = os.path.join(oriDir, fb)
            nf = os.path.join(newDir, fb)
            if VccUtil.isTrivalDir(of):
                assert VccUtil.isTrivalDir(nf)
                common_dirs.append(fb)
            elif VccUtil.isTrivalFile(of):
                assert VccUtil.isTrivalFile(nf)
                common_files.append(fb)
            else:
                assert False

        # delete files
        for fb in left_files:
            of = os.path.join(oriDir, fb)
            if any(x for x in keepAbsList if fnmatch.fnmatch(of, x)):
                continue
            os.remove(of)

        # delete dirs
        for fb in left_dirs:
            of = os.path.join(oriDir, fb)
            if any(x for x in keepAbsList if fnmatch.fnmatch(of, x)):
                continue
            shutil.rmtree(of)

        # add new files
        for fb in right_files:
            of = os.path.join(oriDir, fb)
            nf = os.path.join(newDir, fb)
            assert not any(x for x in keepAbsList if fnmatch.fnmatch(nf, x))
            VccUtil.copyFile(nf, of)

        # add new dirs
        for fb in right_dirs:
            of = os.path.join(oriDir, fb)
            nf = os.path.join(newDir, fb)
            assert not any(x for x in keepAbsList if fnmatch.fnmatch(nf, x))
            VccUtil.copyDir(nf, of)

        # copy common files
        for fb in common_files:
            of = os.path.join(oriDir, fb)
            nf = os.path.join(newDir, fb)
            assert not any(x for x in keepAbsList if fnmatch.fnmatch(nf, x))
            VccUtil.copyFile(nf, of)

        # recurisive into common dirs
        for fb in common_dirs:
            of = os.path.join(oriDir, fb)
            nf = os.path.join(newDir, fb)
            assert not any(x for x in keepAbsList if fnmatch.fnmatch(nf, x))
            VccUtil._updateDirImpl(of, nf, keepAbsList)

        # copy stat for myself, must be at end because file-copy will change parent dir's mtime
        os.chown(oriDir, os.stat(newDir).st_uid, os.stat(newDir).st_gid)
        shutil.copystat(newDir, oriDir)

    @staticmethod
    def removeDirContent(dirname, ignoreList=[]):
        assert os.path.isabs(dirname)
        assert VccUtil.isTrivalDir(dirname)

        ignoreList = VccUtil.getAbsPathList(dirname, ignoreList)
        VccUtil._removeDirContentImpl(dirname, ignoreList, True)

    @staticmethod
    def _removeDirContentImpl(dirname, ignoreAbsList, isRoot):
        mtime = os.path.getmtime(dirname)
        for fb in os.listdir(dirname):
            f = os.path.join(dirname, fb)
            if any(x for x in ignoreAbsList if fnmatch.fnmatch(f, x)):
                continue
            if VccUtil.isTrivalDir(f):
                VccUtil._removeDirContentImpl(f, ignoreAbsList, False)
            elif VccUtil.isTrivalFile(f):
                os.remove(f)
            else:
                assert False
        if not isRoot and len(os.listdir(dirname)) == 0:
            os.rmdir(dirname)
        else:
            VccUtil.setFileMtime(dirname, mtime)

    @staticmethod
    def getDirUidGidSet(dirname, ignoreList=[]):
        assert os.path.isabs(dirname)
        assert VccUtil.isTrivalDir(dirname)

        uidSet = set()
        gidSet = set()
        ignoreList = VccUtil.getAbsPathList(dirname, ignoreList)
        VccUtil._getDirUidGidSetImpl(dirname, uidSet, gidSet, ignoreList)
        return (uidSet, gidSet)

    @staticmethod
    def _getDirUidGidSetImpl(dirname, uidSet, gidSet, ignoreAbsList):
        for fb in os.listdir(dirname):
            f = os.path.join(dirname, fb)
            if any(x for x in ignoreAbsList if fnmatch.fnmatch(f, x)):
                continue
            if VccUtil.isTrivalDir(f):
                VccUtil._getDirUidGidSetImpl(f, uidSet, gidSet, ignoreAbsList)
            elif VccUtil.isTrivalFile(f):
                pass
            else:
                assert False
            uidSet.add(os.lstat(f).st_uid)
            gidSet.add(os.lstat(f).st_gid)

    @staticmethod
    def replaceDirUidGid(dirname, uidDict, gidDict, ignoreList=[]):
        assert os.path.isabs(dirname)
        assert VccUtil.isTrivalDir(dirname)

        ignoreList = VccUtil.getAbsPathList(dirname, ignoreList)
        VccUtil._replaceDirUidGidImpl(dirname, uidDict, gidDict, ignoreList)

    @staticmethod
    def _replaceDirUidGidImpl(dirname, uidDict, gidDict, ignoreAbsList):
        for fb in os.listdir(dirname):
            f = os.path.join(dirname, fb)
            if any(x for x in ignoreAbsList if fnmatch.fnmatch(f, x)):
                continue
            if VccUtil.isTrivalDir(f):
                VccUtil._replaceDirUidGidImpl(f, uidDict, gidDict, ignoreAbsList)
            elif VccUtil.isTrivalFile(f):
                pass
            else:
                assert False
            userId = os.lstat(f).st_uid
            groupId = os.lstat(f).st_gid
            userId = uidDict.get(userId, userId)
            groupId = gidDict.get(groupId, groupId)
            os.lchown(f, userId, groupId)


class TaskRunner(threading.Thread):

	def __init__(self, logger, process_callback, complete_callback):
        self.logger = logger
        self.process_callback = process_callback
        self.complete_callback = complete_callback

		self.taskQueue = queue.Queue()
        self.retList = []
        self.lock = threading.Lock()
		self.bStop = False
		self.completeIdleHandler = None

        self.start()

    def is_running(self):
        self.lock.acquire()
        ret = len(self.taskQueue) > 0 or self.completeIdleHandler is not None
        self.lock.release()
        return ret

	def add_task(*args):
        self.taskQueue.put(args)

	def stop(self):
		self.bStop = True
		self.taskQueue.put(None)
        self.join()
        if self.completeIdleHandler is not None:
            GLib.source_remove(self.completeIdleHandler)
            self.completeIdleHandler = None

	def run(self):
		while not self.bStop:
			try:
                args = self.taskQueue.get()
                if args is None:
                    break
                ret = self.process_callback(*args)
                self.lock.acquire()
                retList.append(ret)
                self.lock.release()
            except:
                if self.logger is not None:
                    self.logger.error("Error occured in task runner.", exc_info=True)
			finally:
                self.lock.acquire()
				self.taskQueue.task_done()
				if len(self.taskQueue) == 0 and self.completeIdleHandler is None:
					self.completeIdleHandler = GLib.idle_add(self._pullCompleteIdleCallback, self.retList)
                    self.retList = []
                self.lock.release()

	def _pullCompleteIdleCallback(self, retList):
        self.lock.acquire()
        try:
            if self.complete_callback is not None:
                self.complete_callback(self.retList)
        finally:
            if len(self.retList) > 0:
                self.completeIdleHandler = GLib.idle_add(self._pullCompleteIdleCallback, self.retList)
                self.retList = []
            else:
                self.completeIdleHandler = None
            self.lock.release()
            return False


class FileMonitor:

    def __init__(self, pattern_list, change_callback):
        for pattern in pattern_list:
            bFound = False
            for fn in glob.glob(pattern):
                assert self._isTrival(fn)
                bFound = True
            assert bFound

        self.change_callback = change_callback
        self.monitorList = []
        for pattern in pattern_list:
            self._monitorPattern(pattern)

    def _monitorPattern(self, pattern):
        for fn in glob.glob(pattern):
            if os.path.islink(fn) or os.path.isfile(fn):
                monitor = Gio.File.new_for_path(fn).monitor_file(0, None)
                monitor.connect("changed", self._onChange)
                self.monitorList.append(monitor)
            else:
                monitor = Gio.File.new_for_path(fn).monitor_directory(0, None)
                monitor.connect("changed", self._onChange)
                self.monitorList.append(monitor)
                for dirpath, dirnames, filenames in os.walk(fn):
                    for dn in dirnames:
                        monitor = Gio.File.new_for_path(dn).monitor_directory(0, None)
                        monitor.connect("changed", self._onChange)
                        self.monitorList.append(monitor)

    def _onChange(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CREATED:
            fn = file.get_path()
            if os.path.isdir(fn):
                monitor = Gio.File.new_for_path(fn).monitor_directory(0, None)
                monitor.connect("changed", self._onChange)
                self.monitorList.append(monitor)
            self.change_callback(fn)
            return

        if event_type == Gio.FileMonitorEvent.DELETED:
            fn = file.get_path()
            self.monitorList.remove(monitor)
            self.change_callback(fn)
            return

        if event_type in [Gio.FileMonitorEvent.CHANGES_DONE_HINT, Gio.FileMonitorEvent.ATTRIBUTE_CHANGED]:
            fn = file.get_path()
            self.change_callback(fn)
            return

    def dispose(self):
        for monitor in self.monitorList.values():
            monitor.cancel()

    def _isTrival(self, pathname):
        """symlink is viewed as file"""

        if os.path.islink(pathname):
            return True
        elif os.path.isdir(pathname):
            return (not os.path.islink(pathname))
        elif stat.S_ISCHR(os.stat(pathname).st_mode):
            return False
        elif stat.S_ISBLK(os.stat(pathname).st_mode):
            return False
        elif stat.S_ISFIFO(os.stat(pathname).st_mode):
            return False
        elif stat.S_ISSOCK(os.stat(pathname).st_mode):
            return False
        else:
            return True


class FileComparer:

    def __init__(self, pathname1, pathname2):
        # compare symlink
        if os.path.islink(pathname1):
            if not os.path.islink(pathname2):
                return False
            if os.path.readlink(pathname1) != os.path.readlink(pathname2):
                return False
            return True
        else:
            if os.path.islink(pathname2):
                return False

        # compare directory
        if os.path.isdir(pathname1):
            if not os.path.isdir(pathname2):
                return False
            if not self._cmpStat(pathname1, pathname2):
                return False
            return self._cmpDir(filecmp.dircmp(pathname1, pathname2))
        else:
            if os.path.isdir(pathname2):
                return False

        # compare file
        if not self._cmpStat(pathname1, pathname2):
            return False
        return filecmp.cmp(pathname1, pathname2)

    def _cmpDir(self, obj):
        if obj.left_only != []:
            return False
        if obj.right_only != []:
            return False
        if obj.diff_files != []:
            return False
        if obj.funny_files != []:
            return False
        for fn in obj.common:
            if not self._cmpStat(os.path.join(obj.left, fn), os.path.join(obj.right, fn)):
                return False
        for obj2 in obj.values():
            if not self._cmpDir(obj2):
                return False
        return True

    def _cmpStat(self, fn1, fn2):
        stat1 = os.stat(fn1)
        stat2 = os.stat(fn2)
        if stat1.st_mode != stat2.st_mode:
            return False
        if stat1.st_uid != stat2.st_uid:
            return False
        if stat1.st_gid != stat2.st_gid:
            return False
        return True









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

    def commit(self, message):
        try:
            VccRepo._vcc2git(self.dirName)
            assert self._compareMetaData()
            self._callGit(self.dirName, "add .", "stdout")
            self._callGit(self.dirName, "commit -a -m \"%s\""%(message), "stdout")
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
            if any(x for x in ignoreLis
class VccDirMonitor:

    def __init__(self, dirname, changeFunc):
        assert VccUtil.isTrivalDir(dirname)

        event_mask = pyinotify.IN_ATTRIB | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE
        event_aux = pyinotify.IN_DONT_FOLLOW

        self.dirname = dirname
        self.wm = pyinotify.WatchManager()

#        retDict = self.wm.add_watch(dirname, mask, rec = True)
#        for path, wd in retDict.items():
#            assert wd > 0

    def dispose(self):
class VccDirMonitor:

    def __init__(self, dirname, changeFunc):
        assert VccUtil.isTrivalDir(dirname)

        event_mask = pyinotify.IN_ATTRIB | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE
        event_aux = pyinotify.IN_DONT_FOLLOW

        self.dirname = dirname
        self.wm = pyinotify.WatchManager()

#        retDict = self.wm.add_watch(dirname, mask, rec = True)
#        for path, wd in retDict.items():
#            assert wd > 0

    def dispose(self):
        pass
#        retDict = self.wm.rm_watch(self.wm.get_wd(self.dirname), rec = True)
#        for wd, ret in retDict.items():
#            assert ret

    def _procFunc(self, event):
        pass


class VccFileMonitor:

    def __init__(self, filename, changeFunc):
        assert VccUtil.isTrivalFile(filename)

        pass

    def dispose(self):
        pass



        pass
#        retDict = self.wm.rm_watch(self.wm.get_wd(self.dirname), rec = True)
#        for wd, ret in retDict.items():
#            assert ret

    def _procFunc(self, event):
        pass


class VccFileMonitor:

    def __init__(self, filename, changeFunc):
        assert VccUtil.isTrivalFile(filename)

        pass

    def dispose(self):
        pass


t if fnmatch.fnmatch(f, x)):
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

    @staticmethod
    def _callGit(dirName, command, shellMode=""):
        gitDir = os.path.join(dirName, ".git")
        cmdStr = "/bin/git --git-dir=\"%s\" --work-tree=\"%s\" %s"%(gitDir, dirName, command)
        return VccUtil.shell(cmdStr, shellMode)

    @staticmethod
    def _vcc2git(dirName):
        os.rename(os.path.join(dirName, ".vcc"), os.path.join(dirName, ".git"))

    @staticmethod
    def _git2vcc(dirName):
        if not os.path.exists(os.path.join(dirName, ".git")):
            return
        os.rename(os.path.join(dirName, ".git"), os.path.join(dirName, ".vcc"))

class VccError(Exception):
    def __init__(self, message):
        super(VccError).__init__(self, message)

