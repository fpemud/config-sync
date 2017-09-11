#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class SystemObject:
    
    @property
    def cfg_pattern_list(self):
        return [
            "/etc/portage",
        ]

    @property
    def ncfs_pattern_list(self):
        return [
            "etc/portage",
        ]

    def convert_to(self, dataDir):
        self._to_sync_etc_dir("/etc/portage", dataDir)

    def convert_from(self, dataDir):
        self._from_sync_etc_dir("/etc/portage", dataDir)

