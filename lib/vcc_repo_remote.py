#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-




class VccRemoteRepoManager:

    def __init__(self, param):
        self.param = param

    def dispose(self):
        # assert offline
        pass

    def isRepoExists(self, peer_name):
        return os.path.exists(self.myDataDir)

	def createRepo(self, peer_name, ip, port, is_encrypt, complete_callback, error_callback):
		pass

    def getRepoObj(self, peer_name):
        return VccRepo(os.path.join(self.param.dataDir, peer_name))

    def bringRepoOnline(self, peer_name, change_callback):
        # monitor target directory
        pass

    def bridgeRepoOffline(self, peer_name):
        pass