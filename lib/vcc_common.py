#!/usr/bin/python2
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import pwd
import subprocess
from vcc_util import VccUtil
from vcc_util import FileCmp




class VccUserLock:

    def __init__(self, param, lock_callback, unlock_callback):
        self.param = param
        self.lock_callback = lock_callback
        self.unlock_callback = unlock_callback





    def get_value(self):
        self.locked

    def dispose(self):
        self.monitor.cancel()

    def _on_change(self, monitor, file, other_file, event_type):
        if event_type == Gio.FileMonitorEvent.CREATED:
            self.locked = True
            self.lock_callback()
            return

        if event_type == Gio.FileMonitorEvent.DELETED:
            self.locked = False
            self.unlock_callback()
            return

        assert False


class VccAppDict(dict):

    def __init__(self, param):
        self.param = param

        if os.getuid() != 0:
            sstr = "System"
        else:
            sstr = "User"
        for fn in os.listdir(self.param.libAppsDir):
            if not fn.endswith(".py"):
                continue
            bn = os.path.basename(fn)[:-3]
            sys.path.append(self.param.libAppsDir)
            try:
                exec("from %s import %sObject" % (bn, sstr))
                obj = eval("%sObject()" % (sstr))
                obj._data_dir = self.param.dataDir
                if os.getuid() == 0:
                    obj._cmp_sync_etc_dir = self._sys_cmp_etc_dir
                    obj._to_sync_etc_dir = self._sys_to_sync_etc_dir
                    obj._from_sync_etc_dir = self._sys_from_sync_etc_dir
                    obj._cmp_etc_files = self._sys_cmp_etc_files
                    obj._to_sync_etc_files = self._sys_to_sync_etc_files
                    obj._from_sync_etc_files = self._sys_from_sync_etc_files
                else:
                    obj._home_dir = "/home/%s" % (pwd.getpwuid(os.getuid())[0])
                    obj._cmp_dir_in_home = self._usr_cmp_dir_in_home
                    obj._to_sync_dir_in_home = self._usr_to_sync_dir_in_home
                    obj._from_sync_dir_in_home = self._usr_from_sync_dir_in_home
                    obj._cmp_files_in_home = self._usr_cmp_files_in_home
                    obj._to_sync_files_in_home = self._usr_to_sync_files_in_home
                    obj._from_sync_files_in_home = self._usr_from_sync_files_in_home
                    obj._cmp_dir_in_config = self._usr_cmp_dir_in_config
                    obj._to_sync_dir_in_config = self._usr_to_sync_dir_in_config
                    obj._from_sync_dir_in_config = self._usr_from_sync_dir_in_config
                    obj._cmp_files_in_config = self._usr_cmp_files_in_config
                    obj._to_sync_files_in_config = self._usr_to_sync_files_in_config
                    obj._from_sync_files_in_config = self._usr_from_sync_files_in_config
                self[bn] = obj
            except Exception as e:
                print(e.__class__.__name__)     # fixme
            finally:
                sys.path.remove(self.param.libAppsDir)

    @staticmethod
    def _sys_cmp_etc_dir(obj, dirname):
        dataEtcDir = os.path.join(obj._data_dir, "etc")
        dataEtcTargetDir = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

        if os.path.exists(dirname):
            if not os.path.exists(dataEtcTargetDir):
                return False
            return FileCmp.compare(dirname, dataEtcTargetDir)
        else:
            if os.path.exists(dataEtcTargetDir):
                return False
            if os.path.exists(dataEtcDir) and os.listdir(dataEtcDir) == []:
                return False
            return True

    @staticmethod
    def _sys_to_sync_etc_dir(obj, dirname):
        dataEtcDir = os.path.join(obj._data_dir, "etc")
        dataEtcTargetDir = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

        if os.path.exists(dirname):
            VccUtil.forceDelete(dataEtcTargetDir)
            VccUtil.ensureDir(dataEtcDir)
            subprocess.check_call(["/bin/cp", "-r", dirname, dataEtcDir])
        else:
            VccUtil.forceDelete(dataEtcTargetDir)
            VccUtil.deleteDirIfEmpty(dataEtcDir)

    @staticmethod
    def _sys_from_sync_etc_dir(obj, dirname):
        dataEtcDir = os.path.join(obj._data_dir, "etc")
        dataEtcTargetDir = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

        if os.path.exists(dataEtcTargetDir):
            VccUtil.ensureDir("/etc")
            subprocess.check_call(["/bin/cp", "-r", dataEtcTargetDir, "/etc"])
        else:
            VccUtil.forceDelete(dirname)

    @staticmethod
    def _sys_cmp_etc_files(obj, file_pattern):
        # fixme: pattern is not supported yet
        dataEtcDir = os.path.join(obj._data_dir, "etc")
        dataEtcTargetFile = os.path.join(dataEtcDir, file_pattern.replace("/etc/", ""))

        if os.path.exists(file_pattern):
            if not os.path.exists(dataEtcTargetFile):
                return False
            return FileCmp.compare(file_pattern, dataEtcTargetFile)
        else:
            if os.path.exists(dataEtcTargetFile):
                return False
            if os.path.exists(dataEtcDir) and os.listdir(dataEtcDir) == []:
                return False
            return True

    @staticmethod
    def _sys_to_sync_etc_files(obj, file_pattern):
        # fixme: pattern is not supported yet
        dataEtcDir = os.path.join(obj._data_dir, "etc")
        dataEtcTargetFile = os.path.join(dataEtcDir, file_pattern.replace("/etc/", ""))

        if os.path.exists(file_pattern):
            VccUtil.forceDelete(dataEtcTargetFile)
            VccUtil.ensureDir(dataEtcDir)
            subprocess.check_call(["/bin/cp", file_pattern, dataEtcDir])
        else:
            VccUtil.forceDelete(dataEtcTargetFile)
            VccUtil.deleteDirIfEmpty(dataEtcDir)

    @staticmethod
    def _sys_from_sync_etc_files(obj, file_pattern):
        # fixme: pattern is not supported yet
        dataEtcDir = os.path.join(obj._data_dir, "etc")
        dataEtcTargetFile = os.path.join(dataEtcDir, dirname.replace("/etc/", ""))

        if os.path.exists(dataEtcTargetFile):
            VccUtil.ensureDir("/etc")
            subprocess.check_call(["/bin/cp", dataEtcTargetFile, "/etc"])
        else:
            VccUtil.forceDelete(dirname)

    @staticmethod
    def _usr_cmp_dir_in_home(obj, dirname):
        pass

    @staticmethod
    def _usr_to_sync_dir_in_home(obj, dirname):
        pass

    @staticmethod
    def _usr_from_sync_dir_in_home(obj, dirname):
        pass

    @staticmethod
    def _usr_cmp_files_in_home(obj, file_pattern):
        pass

    @staticmethod
    def _usr_to_sync_files_in_home(obj, file_pattern):
        pass

    @staticmethod
    def _usr_from_sync_files_in_home(obj, file_pattern):
        pass

    @staticmethod
    def _usr_cmp_dir_in_config(obj, dirname):
        cfgDir = os.path.join(obj._data_dir, "_config")
        targetDir = os.path.join(cfgDir, dirname.replace(".config", "_config"))
        dirname = os.path.join(obj._home_dir, dirname)

        #fixme

    @staticmethod
    def _usr_to_sync_dir_in_config(obj, dirname):
        cfgDir = os.path.join(obj._data_dir, "_config")
        targetDir = os.path.join(cfgDir, dirname.replace(".config", "_config"))
        dirname = os.path.join(obj._home_dir, dirname)

        if os.path.exists(dirname):
            VccUtil.forceDelete(targetDir)
            VccUtil.ensureDir(cfgDir)
            subprocess.check_call(["/bin/cp", "-r", dirname, cfgDir])
        else:
            VccUtil.forceDelete(targetDir)
            VccUtil.deleteDirIfEmpty(cfgDir)

    @staticmethod
    def _usr_from_sync_dir_in_config(obj, dirname):
        ocfgDir = os.path.join(obj._home_dir, ".config")
        cfgDir = os.path.join(obj._data_dir, "_config")
        targetDir = os.path.join(cfgDir, dirname.replace(".config", "_config"))
        dirname = os.path.join(obj._home_dir, dirname)

        if os.path.exists(targetDir):
            VccUtil.ensureDir(ocfgDir)
            subprocess.check_call(["/bin/cp", "-r", targetDir, ocfgDir])
        else:
            VccUtil.forceDelete(dirname)

    @staticmethod
    def _usr_cmp_files_in_config(obj, file_pattern):
        pass

    @staticmethod
    def _usr_to_sync_files_in_config(obj, file_pattern):
        pass

    @staticmethod
    def _usr_from_sync_files_in_config(obj, file_pattern):
        pass


class VccApiServer:

    def __init__(self, param, filename):
        self.param = param

        self.serverListener = Gio.SocketListener.new()
        addr = Gio.UnixSocketAddress.new(filename)
        self.serverListener.add_address(addr, Gio.SocketType.STREAM, Gio.SocketProtocol.TCP)
        self.serverListener.accept_async(None, self._on_accept)

        self.sprocList = []

    def dispose(self):
        self.serverListener.close()
        for sproc in self.sprocList:
            sproc.close(immediate=True)

    def _on_accept(self, source_object, res):
        conn, dummy = source_object.accept_finish(res)
        peer_ip = conn.get_remote_address().get_address().to_string()

        bFound = False
        for p in self.param.managers["lan"].vpnsPluginList:
            netobj = ipaddress.IPv4Network(p.get_bridge().get_prefix()[0] + "/" + p.get_bridge().get_prefix()[1])
            if ipaddress.IPv4Address(peer_ip) in netobj:
                bFound = True
                break
        if not bFound:
            self.logger.error("CASCADE-API client %s rejected, invalid client IP address." % (peer_ip))
            conn.close()
            return

        for sproc in self.sprocList:
            if sproc.peer_ip == peer_ip:
                self.logger.error("CASCADE-API client %s rejected, multiple channel per IP address." % (peer_ip))
                conn.close()
                return

        self.sprocList.append(_ApiServerProcessor(self.pObj, self, conn))
        self.serverListener.accept_async(None, self._on_accept)

