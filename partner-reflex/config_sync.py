#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import json
from gi.repository import Gio
sys.path.append('/usr/lib/config-sync')
from vcc_param import VccParam
from vcc_userlock import VccUserLock


def get_reflex_list():
    return [
        "config-sync",
    ]


def get_reflex_properties(name):
    if name == "config-sync":
        return {
            "need-plugin": ["mesh"],
            "protocol": "config-sync",
            "role": "p2p",
        }
    else:
        assert False


def get_reflex_object(fullname):
    if name == "config-sync":
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def on_init(self):
        self.param = VccParam()

        self.appObjDict = []



        if not os.path.exists(self.param.dataDir):
            os.makedirs(self.param.dataDir)






        self.ulock = VccUserLock(self.param, self.on_user_lock, self.on_user_unlock)

        self.localRepo = VccLocalRepoManager(self.param)
        self.localRepo.bringRepoOnline()

        self.remoteRepoDict = dict()
        for peername in os.listdir(self.param.dataDir):
            self.remoteRepoDict[peername] = VccRemoteRepo(self.param, self.param.dataDir, peername)

    def on_fini(self):
        self.localRepo.bringRepoOffline()
        self.ulock.dispose()

    def on_peer_appear(self, peername, ip, uid):
        pass

    def on_peer_disappear(self, peername):
        pass

    def on_receive_message_from_peer(self, peername, message):
        jsonObj = json.loads(message)

        if "pull-request" in jsonObj:
            if jsonObj["repo-name"] == self.my_hostname:
                repoObj = self.localRepo
            else:
                repoObj = self.remoteRepoDict[jsonObj["repo-name"]]
            repoObj.pull_from(peername, self.peer_info[peername]["ip"], jsonObj["port"])
            return

        assert False

    def on_repo_change(self, repo_name):
        if repo_name == "localhost":
            port = self.localRepo.start_server()                        # fixme, what if the server already started
            repo_name = self.my_hostname
        else:
            port = self.remoteRepoDict[repo_name].start_server()

        jsonObj = {
            "pull-request": {
                "repo-name": repo_name,
                "port": port,
            },
        }
        message = json.dumps(jsonObj)
        for pi in self.peer_info:
            self.send_message_to_peer(pi["hostname"], message)

    def on_user_lock(self):
        pass

    def on_user_unlock(self):
        pass



    def _load_app_data(self):
        for fn in os.listdir(self.param.libAppsDir):
            if not fn.endswith(".py"):
                continue
            bn = os.path.basename(fn)[:-3]
            sys.path.append(self.param.libAppsDir)
            try:
                exec("from %s import %sObject" % (bn, sstr))
                obj = eval("%sObject()" % (sstr))
                if os.getuid() == 0:
                    obj._cmp_sync_etc_dir = _sys_cmp_etc_dir
                    obj._to_sync_etc_dir = _sys_to_sync_etc_dir
                    obj._from_sync_etc_dir = _sys_from_sync_etc_dir
                    obj._cmp_etc_files = _sys_cmp_etc_files
                    obj._to_sync_etc_files = _sys_to_sync_etc_files
                    obj._from_sync_etc_files = _sys_from_sync_etc_files
                else:
                    obj._cmp_dir_in_home = _usr_cmp_dir_in_home
                    obj._to_sync_dir_in_home = _usr_to_sync_dir_in_home
                    obj._from_sync_dir_in_home = _usr_from_sync_dir_in_home
                    obj._cmp_files_in_home = _usr_cmp_files_in_home
                    obj._to_sync_files_in_home = _usr_to_sync_files_in_home
                    obj._from_sync_files_in_home = _usr_from_sync_files_in_home
                    obj._cmp_dir_in_config = _usr_cmp_dir_in_config
                    obj._to_sync_dir_in_config = _usr_to_sync_dir_in_config
                    obj._from_sync_dir_in_config = _usr_from_sync_dir_in_config
                    obj._cmp_files_in_config = _usr_cmp_files_in_config
                    obj._to_sync_files_in_config = _usr_to_sync_files_in_config
                    obj._from_sync_files_in_config = _usr_from_sync_files_in_config
                self.appObjDict[bn] = obj
            except Exception as e:
                print(e.__class__.__name__)     # fixme
            finally:
                sys.path.remove(self.param.libAppsDir)
