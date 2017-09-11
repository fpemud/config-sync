#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class SystemObject:
    
    @property
    def cfg_pattern_list(self):
        return [
            "/etc/portage",
            "/var/lib/portage/world",
        ]

    @property
    def ncfs_pattern_list(self):
        return [
            "etc/portage",
            "portage-world",
        ]

    def convert_to(self, dataDir):
        # /etc/portage
        self._to_sync_etc_dir("/etc/portage", dataDir)

        # /var/lib/portage/world
        targetFile = os.path.join(dataDir, "portage-world")
        if os.path.exists("/var/lib/portage/word"):
            subprocess.check_call(["/bin/cp", "/var/lib/portage/word", dataDir])
        else:
            _forceDelete(targetFile)

    def convert_from(self, dataDir):
        # /etc/portage
        self._from_sync_etc_dir("/etc/portage", dataDir)

        # /var/lib/portage/world
        targetFile = os.path.join(dataDir, "portage-world")
        if os.path.exists(targetFile):
            _ensureDir("/var/lib/portage")
            subprocess.check_call(["/bin/cp", targetFile, "/var/lib/portage"])
        else:
            _forceDelete("/var/lib/portage/world")
            _deleteDirIfEmpty("/var/lib/portage")
            _deleteDirIfEmpty("/var/lib")


def _ensureDir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def _forceDelete(filename):
    if os.path.islink(filename):
        os.remove(filename)
    elif os.path.isfile(filename):
        os.remove(filename)
    elif os.path.isdir(filename):
        shutil.rmtree(filename)

def _deleteDirIfEmpty(dirname):
    if os.listdir(dirname) == []:
        os.rmdir(dirname)
