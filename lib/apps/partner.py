#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class SystemObject:
    
    @property
    def cfg_pattern_list(self):
        return [
            "/etc/partner",
        ]

    @property
    def ncfs_pattern_list(self):
        return [
            "etc/partner",
        ]

    def convert_to(self, dataDir):
        self._to_sync_etc_dir("/etc/partner", dataDir)

    def convert_from(self, dataDir):
        self._from_sync_etc_dir("/etc/partner", dataDir)


class UserObject:

    @property
    def cfg_pattern_list(self):
        return [
            ".config/partner",
        ]

    def ncfs_pattern_list(self):
        self.ncfs_pattern_list = [
            "_config/partner"
        ]

    def convert_to(self, homeDir, dataDir):
        self._to_sync_dir_in_config(homeDir, ".config/partner", dataDir)

    def convert_from(self, homeDir, dataDir):
        self._from_sync_dir_in_config(homeDir, ".config/partner", dataDir)
