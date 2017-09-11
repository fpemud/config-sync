#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-




class VccRemoteRepoManager:

    def __init__(self, param):
        self.param = param

    def isRepoExists(self):
        return os.path.exists(self.myDataDir)

	def createRepo(self, peer_name, ip, port, is_encrypt, complete_callback, error_callback):
		pass

	def (self):
