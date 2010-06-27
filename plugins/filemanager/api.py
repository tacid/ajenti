# -*- coding: utf-8 -*-

import os, stat, pwd, grp
import platform
import statvfs
#import win32api
#platform.system()

def pretty_size_view(bytes):
    if bytes >= 1073741824:
        return str(round(bytes / 1024.0 / 1024 / 1024, 2)) + ' GB'
    elif bytes >= 1048576:
        return str(round(bytes / 1024 / 1024, 2)) + ' MB'
    elif bytes >= 1024:
        return str(round(bytes / 1024, 2)) + ' KB'
    elif bytes < 1024:
        return str(bytes) + ' b'

class LocalFS:
    def __init__(self, path=None, show_hidden=False):
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = path
        self.selected = []
        self.show_hidden = show_hidden 

    def is_readable(self, path):
        return os.access(path, os.R_OK)

    def is_writeable(self, path):
        return os.access(path, os.W_OK)

    def get_owner(self, stat_info):
        try:
            name = "%-8s" % pwd.getpwuid(stat_info.st_uid)[0]
        except KeyError:
            name = "%-8s" % stat_info.st_uid
        return name.strip(" ")

    def get_group(self, stat_info):
        try:
            group = "%-8s" % grp.getgrgid(stat_info.st_gid)[0]
        except KeyError:
            group = "%-8s" % stat_info.st_gid
        return group

    def get_perms(self, stat_info):
        mode = stat_info.st_mode
        perms="-"
        if stat.S_ISDIR(mode):
            perms="d"
        elif stat.S_ISLNK(mode):
            perms="l"
        mode=stat.S_IMODE(mode)
        for who in "USR", "GRP", "OTH":
            for what in "R", "W", "X":
                if mode & getattr(stat, "S_I"+what+who):
                    perms=perms+what.lower()
                else:
                    perms=perms+"-"
        return perms

    def listdir(self):
        if self.is_readable(self.path) and os.path.isdir(self.path):
            if self.show_hidden:
                return os.listdir(self.path)
            return tuple(s for s in os.listdir(self.path) if s[0] != '.')
        return ()

    def split_linux_path(self):
        result = []
        head, tail = os.path.split(os.path.realpath(self.path))
        if not tail:
            return [['/', None]]
        else:
            result.append([tail, None])
        while tail:
            head, tail = os.path.split(head)
            result.append([tail if tail else '/', os.path.join(head, tail)])
        result.reverse()
        return result

    def split_win_path(self):
        "Split path for windows. NEED TEST!! "
        result = []
        head, tail = os.path.split(os.path.realpath(self.path))
        if not tail:
            return [[head, None]]
        else:
            result.append([tail, None])
        while tail:
            head, tail = os.path.split(head)
            result.append([tail if tail else head, os.path.join(head, tail)])
        result.reverse()
        return result

    def split_path(self):
        if platform.system() == "Linux":
            return self.split_linux_path()
        else:
            return self.split_win_path()

    def get_folders(self):
        result = {}
        folders = list(os.path.join(self.path, p) for p in self.listdir() if os.path.isdir(os.path.join(self.path, p)) )
        for f in folders:
            stat_info = os.lstat(f)
            result[f] = { 'name' : os.path.basename(f),
                          'perms' : self.get_perms(stat_info),
                          'link' : os.readlink(f) if os.path.islink(f) else None,
                          'size' : None,
                          'owner' : self.get_owner(stat_info),
                          'group' : self.get_group(stat_info)
                        }
        f = os.path.abspath(os.path.join(self.path, '..'))
        if f != self.path:
            stat_info = os.lstat(f)
            result[f] = { 'name' : '..',
                          'perms' : self.get_perms(stat_info),
                          'link' : os.readlink(f) if os.path.islink(f) else None,
                          'size' : None,
                          'owner' : self.get_owner(stat_info),
                          'group' : self.get_group(stat_info)
                        }
        return result

    def get_files(self):
        result = {}
        files = tuple(os.path.join(self.path, p) for p in self.listdir() if os.path.isfile(os.path.join(self.path, p)) )
        for f in files:
            stat_info = os.lstat(f)
            result[f] = { 'name' : os.path.basename(f),
                          'perms' : self.get_perms(stat_info),
                          'link' : os.readlink(f) if os.path.islink(f) else None,
                          'size' : self.get_size(f),
                          'owner' : self.get_owner(stat_info),
                          'group' : self.get_group(stat_info)
                        }
        return result
#### Добавить обработчики прав
    def chdir(self, path):
        if path is None:
            self.path = os.getcwd()
        elif os.path.isabs(path):
            self.path = path
        else:
            self.path = os.path.join(self.path, path)

    def up(self):
        self.path = os.path.abspath(os.path.join(self.path, '..'))

##################
    def get_size(self, path):
        return os.path.getsize(path)

    # Copy selected files from current folder to other FS
    def copy_to(self, fs):
        pass

    # Copy "file" from local FS to current folder
    def copy(self, file):
        pass

    def move_to(self, fs):
        pass

    def move(self, file):
        pass

    def unlink(self, file):
        pass

    def win_free_space(self):
        "Get free space on disk for windows"
        #r =  win32api.GetDiskFreeSpace(r'd:')
        #free_space =r[0]*r[1]*r[2]
        pass

    def win_used_space(self):
        "Get used space on disk for windows"
        pass

    def win_total_space(self):
        "Get used space on disk for windows"

    def linux_free_space(self):
        st = os.statvfs(self.path)
        return st[statvfs.F_BSIZE] * st[statvfs.F_BFREE]

    def linux_used_space(self):
        st = os.statvfs(self.path)
        return st[statvfs.F_BSIZE] * (st[statvfs.F_BLOCKS] - st[statvfs.F_BAVAIL])

    def linux_total_space(self):
        st = os.statvfs(self.path)
        return st[statvfs.F_BSIZE] * st[statvfs.F_BLOCKS]        

    def free_space(self):
        if platform.system() == "Linux":
            return self.linux_free_space()
        else:
            return self.win_free_space()

    def used_space(self):
        if platform.system() == "Linux":
            return self.linux_used_space()
        else:
            return self.win_used_space()

    def total_space(self):
        if platform.system() == "Linux":
            return self.linux_total_space()
        else:
            return self.win_total_space()

#ut = LocalFS('/mnt/windows/media')
#ut.chdir('/etc')
#for s in ut.get_folders(): print s
#print ut.get_size('/etc')
#print pretty_size_view(ut.free_space())