#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys


class VccLocalRepo(VccRepo):

	def __init__(self, param, dataDir):
        self.param = param

        # init repo
		targetDir = os.path.join(dataDir, "localhost")
		if not os.path.exists(targetDir):
            _callGit(targetDir, "init", "stdout")
        super().__init__(targetDir)

        # load application data
        self.appObjDict = []
        if True:
            if os.getuid() == 0:
                sstr = "System"
            else:
                sstr = "User"
            for fn in os.listdir(self.param.libAppsDir):
                if not fn.endswith(".py"):
                    continue
                bn = os.path.basename(fn)[:-3]
                sys.path.append(self.param.libAppsDir)
                try:
                    exec("from %s import %sObject" % (bn, sstr))
                    obj = eval("%sObject()" % (sstr))
                    if os.getuid() == 0:
                        obj._to_sync_etc_dir = _to_sync_etc_dir
                        obj._from_sync_etc_dir = _from_sync_etc_dir
                        obj._to_sync_etc_files = _to_sync_etc_files
                        obj._from_sync_etc_files = _from_sync_etc_files
                    else:
                        pass
                    self.appObjDict[bn] = obj
                except Exception as e:
                    print(e.__class__.__name__)     # fixme
                finally:
                    sys.path.remove(self.param.libAppsDir)

        # monitor cfg files
        pass

        # init target directory if needed
        for obj in self.appObjDict.values():
            obj.convertCfgToNcfs()


        pass

        # monitor target directory
        pass






def _to_sync_etc_dir(obj, dirname, dataDir):
    dataEtcDir = os.path.join(dataDir, "etc")
    dataEtcTargetDir = dirname.replace("/etc/", "")

    if os.path.exists(dirname):
        VccUtil.forceDelete(dataEtcTargetDir)
        VccUtil.ensureDir(dataEtcDir)
        subprocess.check_call(["/bin/cp", "-r", dirname, dataEtcDir])
    else:
        VccUtil.forceDelete(dataEtcTargetDir)
        VccUtil.deleteDirIfEmpty(dataEtcDir)


def _from_sync_etc_dir(obj, dirname, dataDir):
    dataEtcDir = os.path.join(dataDir, "etc")
    dataEtcTargetDir = dirname.replace("/etc/", "")

    if os.path.exists(dataEtcTargetDir):
        subprocess.check_call(["/bin/cp", "-r", dataEtcTargetDir, "/etc"])
    else:
        VccUtil.forceDelete(dirname)


def _to_sync_etc_files(obj, file_pattern, dataDir):
    pass

def _from_sync_etc_files(obj, file_pattern, dataDir):
    pass

