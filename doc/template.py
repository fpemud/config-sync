#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class SystemObject:
    
    @property
    def cfg_pattern_list(self):
        # absolute path
        assert False

    @property
    def ncfs_pattern_list(self):
        # relative path based on ncfs data directory
        assert False

    def compare(self):
        # returns True when equal
        assert False

    def convert_to(self):
        # system-configuration -> ncfs
        assert False

    def convert_from(self):
        # ncfs -> system-configuration
        assert False

    ## conveninent functions for you ##########################################

    @property
    def _data_dir(self):
        pass

    def _cmp_etc_dir(self, dirname):
        # dirname is absolute path
        pass

    def _to_sync_etc_dir(self, dirname):
        # dirname is absolute path
        pass

    def _from_sync_etc_dir(self, dirname):
        # dirname is absolute path
        pass

    def _cmp_etc_files(self, file_pattern):
        # file_pattern is absolute path
        pass

    def _to_sync_etc_files(self, file_pattern):
        # file_pattern is absolute path
        pass

    def _from_sync_etc_files(self, file_pattern):
        # file_pattern is absolute path
        pass


class UserObject:
    
    @property
    def cfg_pattern_list(self):
        # relative path based on "~"
        assert False

    @property
    def ncfs_pattern_list(self):
        # relative path based on ncfs data directory
        assert False

    def compare(self):
        # returns True when equal
        assert False

    def convert_to(self):
        # user-configuration -> ncfs
        assert False

    def convert_from(self):
        # ncfs -> user-configuration
        assert False

    ## conveninent functions for you ##########################################

    @property
    def _home_dir(self):
        pass

    @property
    def _data_dir(self):
        pass

    def _cmp_dir_in_home(self, dirname):
        # dirname is relative path based on "~"
        pass

    def _to_sync_dir_in_home(self, dirname):
        # dirname is relative path based on "~"
        pass

    def _from_sync_dir_in_home(self, dirname):
        # dirname is relative path based on "~"
        pass

    def _cmp_files_in_home(self, file_pattern):
        # file_pattern is relative path based on "~"
        pass

    def _to_sync_files_in_home(self, file_pattern):
        # file_pattern is relative path based on "~"
        pass

    def _from_sync_files_in_home(self, file_pattern):
        # file_pattern is relative path based on "~"
        pass

    def _cmp_dir_in_config(self, dirname):
        # dirname is relative path based on "~", prefixed with "~/.config"
        pass

    def _to_sync_dir_in_config(self, dirname):
        # dirname is relative path based on "~", prefixed with "~/.config"
        pass

    def _from_sync_dir_in_config(self, dirname):
        # dirname is relative path based on "~", prefixed with "~/.config"
        pass

    def _cmp_files_in_config(self, file_pattern):
        # file_pattern is relative path based on "~", prefixed with "~/.config"
        pass

    def _to_sync_files_in_config(self, file_pattern):
        # file_pattern is relative path based on "~", prefixed with "~/.config"
        pass

    def _from_sync_files_in_config(self, file_pattern):
        # file_pattern is relative path based on "~", prefixed with "~/.config"
        pass
