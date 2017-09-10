#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class VccRemoteRepo(VccRepo):

	def __init__(self, dataDir, peerName, peerIp):
		self.dirName = os.path.join(dataDir, peerName)

