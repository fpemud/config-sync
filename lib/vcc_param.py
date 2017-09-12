#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import pwd


class VccParam:

	def __init__(self):
        self.libDir = "/usr/lib/config-sync"
        self.libAppsDir = os.path.join(self.libDir, "apps-linux")

		if os.getuid() == 0:
			self.dataDir = "/var/cache/config-sync"
		else:
			self.dataDir = "/home/%s/.cache/config-sync" % (pwd.getpwuid(os.getuid())[0]))
