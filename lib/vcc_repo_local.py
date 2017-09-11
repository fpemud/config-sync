#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys


class VccLocalRepoManager:

    def __init__(self, param):
        self.param = param
        self.myDataDir = os.path.join(self.param.dataDir, "localhost")

        if os.getuid() != 0:
            sstr = "System"
            userDir = None
        else:
            sstr = "User"
            userDir = os.path.join("/home", pwd.getpwuid(os.getuid())[0])

        # load application data
        self.appObjDict = []
        for fn in os.listdir(self.param.libAppsDir):
            if not fn.endswith(".py"):
                continue
            bn = os.path.basename(fn)[:-3]
            sys.path.append(self.param.libAppsDir)
            try:
                exec("from %s import %sObject" % (bn, sstr))
                obj = eval("%sObject()" % (sstr))
                if os.getuid() == 0:
                    obj._to_sync_etc_dir = _sys_to_sync_etc_dir
                    obj._from_sync_etc_dir = _sys_from_sync_etc_dir
                    obj._to_sync_etc_files = _sys_to_sync_etc_files
                    obj._from_sync_etc_files = _sys_from_sync_etc_files
                else:
                    obj._to_sync_dir_in_home = _usr_to_sync_dir_in_home
                    obj._from_sync_dir_in_home = _usr_from_sync_dir_in_home
                    obj._to_sync_files_in_home = _usr_to_sync_files_in_home
                    obj._from_sync_files_in_home = _usr_from_sync_files_in_home
                    obj._to_sync_dir_in_config = _usr_to_sync_dir_in_config
                    obj._from_sync_dir_in_config = _usr_from_sync_dir_in_config
                    obj._to_sync_files_in_config = _usr_to_sync_files_in_config
                    obj._from_sync_files_in_config = _usr_from_sync_files_in_config
                self.appObjDict[bn] = obj
            except Exception as e:
                print(e.__class__.__name__)     # fixme
            finally:
                sys.path.remove(self.param.libAppsDir)

    def isRepoExists(self):self.
        return os.path.exists(self.myDataDir)

    def bringRepoOnline(self):
        # monitor cfg files
        pass

        # create repo if not exists
        if not os.path.exists(self.myDataDir):
            os.makedirs(self.myDataDir)
            _callGit(self.myDataDir, "init", "stdout")

        # flush repo
        for obj in self.appObjDict.values():
            if userDir is None:
                obj.convert_to(self.myDataDir)
            else:
                obj.convert_to(userDir, self.myDataDir)

        # monitor target directory
        pass

    def bringRepoOffline(self):
        pass

    def on_change(self):
        assert False






def _sys_to_sync_etc_dir(obj, dirname, dataDir):
    dataEtcDir = os.path.join(dataDir, "etc")
    dataEtcTargetDir = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

    if os.path.exists(dirname):
        VccUtil.forceDelete(dataEtcTargetDir)
        VccUtil.ensureDir(dataEtcDir)
        subprocess.check_call(["/bin/cp", "-r", dirname, dataEtcDir])
    else:
        VccUtil.forceDelete(dataEtcTargetDir)
        VccUtil.deleteDirIfEmpty(dataEtcDir)


def _sys_from_sync_etc_dir(obj, dirname, dataDir):
    dataEtcDir = os.path.join(dataDir, "etc")
    dataEtcTargetDir = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

    if os.path.exists(dataEtcTargetDir):
        VccUtil.ensureDir("/etc")
        subprocess.check_call(["/bin/cp", "-r", dataEtcTargetDir, "/etc"])
    else:
        VccUtil.forceDelete(dirname)


def _sys_to_sync_etc_files(obj, file_pattern, dataDir):
    # fixme: pattern is not supported yet
    dataEtcDir = os.path.join(dataDir, "etc")
    dataEtcTargetFile = os.path.join(dataEtcDir, file_pattern.replace("/etc/", ""))

    if os.path.exists(file_pattern):
        VccUtil.forceDelete(dataEtcTargetFile)
        VccUtil.ensureDir(dataEtcDir)
        subprocess.check_call(["/bin/cp", file_pattern, dataEtcDir])
    else:
        VccUtil.forceDelete(dataEtcTargetFile)
        VccUtil.deleteDirIfEmpty(dataEtcDir)


def _sys_from_sync_etc_files(obj, file_pattern, dataDir):
    # fixme: pattern is not supported yet
    dataEtcDir = os.path.join(dataDir, "etc")
    dataEtcTargetFile = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

    if os.path.exists(dataEtcTargetFile):
        VccUtil.ensureDir("/etc")
        subprocess.check_call(["/bin/cp", dataEtcTargetFile, "/etc"])
    else:
        VccUtil.forceDelete(dirname)


def _usr_to_sync_dir_in_home(obj, homeDir, dirname, dataDir):
    pass


def _usr_from_sync_dir_in_home(obj, homeDir, dirname, dataDir):
    pass


def _usr_to_sync_files_in_home(obj, homeDir, file_pattern, dataDir):
    pass


def _usr_from_sync_files_in_home(obj, homeDir, file_pattern, dataDir):
    pass


def _usr_to_sync_dir_in_config(obj, homeDir, dirname, dataDir):
    cfgDir = os.path.join(dataDir, "_config")
    targetDir = os.path.join(cfgDir, dirname.replace(".config", "_config"))
    dirname = os.path.join(homeDir, dirname)"/etc"

    if os.path.exists(dirname):
        VccUtil.forceDelete(targetDir)
        VccUtil.ensureDir(cfgDir)
        subprocess.check_call(["/bin/cp", "-r", dirname, cfgDir])
    else:
        VccUtil.forceDelete(targetDir)
        VccUtil.deleteDirIfEmpty(cfgDir)


def _usr_from_sync_dir_in_config(obj, homeDir, dirname, dataDir):
    ocfgDir = os.path.join(homeDir, ".config")
    cfgDir = os.path.join(dataDir, "_config")
    targetDir = os.path.join(cfgDir, dirname.replace(".config", "_config"))
    dirname = os.path.join(homeDir, dirname)

    if os.path.exists(targetDir):
        VccUtil.ensureDir(ocfgDir)
        subprocess.check_call(["/bin/cp", "-r", targetDir, ocfgDir])
    else:
        VccUtil.forceDelete(dirname)


def _usr_to_sync_files_in_config(obj, homeDir, file_pattern, dataDir):
    pass


def _usr_from_sync_files_in_config(obj, homeDir, file_pattern, dataDir):
    pass
