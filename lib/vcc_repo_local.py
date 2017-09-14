#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
from vcc_util import FileCmp


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
                    obj._cmp_sync_etc_dir = _sys_cmp_etc_dir
                    obj._to_sync_etc_dir = _sys_to_sync_etc_dir
                    obj._from_sync_etc_dir = _sys_from_sync_etc_dir
                    obj._cmp_etc_files = _sys_cmp_etc_files
                    obj._to_sync_etc_files = _sys_to_sync_etc_files
                    obj._from_sync_etc_files = _sys_from_sync_etc_files
                else:
                    obj._cmp_dir_in_home = _usr_cmp_dir_in_home
                    obj._to_sync_dir_in_home = _usr_to_sync_dir_in_home
                    obj._from_sync_dir_in_home = _usr_from_sync_dir_in_home
                    obj._cmp_files_in_home = _usr_cmp_files_in_home
                    obj._to_sync_files_in_home = _usr_to_sync_files_in_home
                    obj._from_sync_files_in_home = _usr_from_sync_files_in_home
                    obj._cmp_dir_in_config = _usr_cmp_dir_in_config
                    obj._to_sync_dir_in_config = _usr_to_sync_dir_in_config
                    obj._from_sync_dir_in_config = _usr_from_sync_dir_in_config
                    obj._cmp_files_in_config = _usr_cmp_files_in_config
                    obj._to_sync_files_in_config = _usr_to_sync_files_in_config
                    obj._from_sync_files_in_config = _usr_from_sync_files_in_config
                self.appObjDict[bn] = obj
            except Exception as e:
                print(e.__class__.__name__)     # fixme
            finally:
                sys.path.remove(self.param.libAppsDir)

    def dispose(self):
        # assert offline
        pass

    def isRepoExists(self):
        return os.path.exists(self.myDataDir)

    def getRepoObj(self):
        return VccRepo(self.myDataDir)

    def bringRepoOnline(self, change_callback):
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


