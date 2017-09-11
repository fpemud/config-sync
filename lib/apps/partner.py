#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

class SystemObject:
    
    def cfg_pattern_list(self):
        return [
            "/etc/partner",
        ]

    def ncfs_pattern_list(self):
        return [
            "etc/partner",
        ]

    def convert_to(self, dataDir):
        self._to_sync_etc_dir("/etc/partner", dataDir)

    def convert_from(self, dataDir):
        self._from_sync_etc_dir("/etc/partner", dataDir)





class UserObject:
        self.cfg_pattern_list = [
            ".config/partner"
        ]
        self.ncfs_pattern_list = [
            "partner"
        ]

