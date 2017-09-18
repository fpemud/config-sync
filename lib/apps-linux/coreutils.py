#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class SystemObject:
    
    @property
    def cfg_pattern_list(self):
        return [
            "/etc/DIR_COLORS",
        ]

    @property
    def ncfs_pattern_list(self):
        return [
            "etc/DIR_COLORS",
        ]

    def compare(self):
        pass

    def convert_to(self):
        self._to_sync_etc_files("/etc/DIR_COLORS")

    def convert_from(self):
        self._from_sync_etc_files("/etc/DIR_COLORS")

