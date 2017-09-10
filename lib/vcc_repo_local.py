#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys


class VccLocalRepo(VccRepo):

	def __init__(self, param, dataDir):
        self.param = param

        # init repo
		self.targetDir = os.path.join(dataDir, "localhost")
		if not os.path.exists(self.targetDir):
            _callGit(self.targetDir, "init", "stdout")
        super().__init__(self.targetDir)

        # load application data
        self.appDataList = []
        for fn in os.listdir(self.param.libAppsDir):
            if not fn.endswith(".py"):
                continue
            obj = _AppData(os.path.join(self.param.libAppsDir, fn), (os.getuid() == 0))
            self.appDataList.append(obj)

        # monitor cfg files
        pass

        # init target directory if needed
        pass

        # monitor target directory
        pass


class _AppData:

    def __init__(self, filename, systemOrUser):
        assert filename.endswith(".py")
        dn = os.path.dirname(filename)
        bn = os.path.basename(filename)[:-3]

        sys.path.append(dn)
        try:
            if systemOrUser:
                exec("from %s import SystemObject" % (bn))
                obj = eval("SystemObject()")
            else:
                exec("from %s import UserObject" % (bn))
                obj = eval("UserObject()")
        finally:
            sys.path.remove(dn)

        self.appName = bn
        self.cfgPatternList = obj.cfg_pattern_list
        self.ncfsPatternList = obj.ncfs_pattern_list
        self.convertCfgToNcfs = obj.convert_cfg_to_ncfs
        self.convertNcfsToCfg = obj.convert_ncfs_to_cfg
