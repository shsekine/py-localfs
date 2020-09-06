# -*- conding:utf-8 -*-

import fnmatch
import glob
import grp
import os
import pwd
import re
import shutil
import time
import stat as st_stat
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Any


GLOB_PATTERN = re.compile(r'^.*[*?].*$')


#
def rwx(n: int, suid: int, sticky: bool = False) -> str:
    if suid > 0:
        suid = 2
    res = '-r'[n >> 2] + '-w'[(n >> 1) & 1]
    if sticky:
        res += '-xTt'[suid + (n & 1)]
    else:
        res += '-xSs'[suid + (n & 1)]
    return res


#
def to_rwx(st_mode: int) -> str:
    kind = st_stat.S_IFMT(st_mode)
    if kind == st_stat.S_IFIFO:
        res = 'p'
    elif kind == st_stat.S_IFCHR:
        res = 'c'
    elif kind == st_stat.S_IFDIR:
        res = 'd'
    elif kind == st_stat.S_IFBLK:
        res = 'b'
    elif kind == st_stat.S_IFREG:
        res = '-'
    elif kind == st_stat.S_IFLNK:
        res = 'l'
    elif kind == st_stat.S_IFSOCK:
        res = 's'
    else:
        res = '?'
    res += rwx((st_mode & 0o700) >> 6, st_mode & st_stat.S_ISUID)
    res += rwx((st_mode & 0o70) >> 3, st_mode & st_stat.S_ISGID)
    res += rwx((st_mode & 0o7), st_mode & st_stat.S_ISVTX)
    return res


#
def to_perm(st_mode: int) -> str:
    res = ''
    res += str((st_mode & 0o700) >> 6)
    res += str((st_mode & 0o70) >> 3)
    res += str(st_mode & 0o7)
    return res


#
def to_user(uid: int) -> str:
    try:
        return pwd.getpwuid(uid).pw_name
    except Exception:
        return str(uid)


#
def to_group(gid: int) -> str:
    try:
        return grp.getgrgid(gid).gr_name
    except Exception:
        return str(gid)


#
def to_date_format(mtime: int) -> str:
    if mtime is not None and mtime != int(0xffffffff):
        if abs(time.time() - mtime) > 1552000:
            return time.strftime('%d %b %Y', time.localtime(mtime))
        else:
            return time.strftime('%d %b %H:%M', time.localtime(mtime))
    else:
        return '(unknown date)'


#
def format_short(paths: List[Dict[str, Any]]) -> List[str]:
    res = []
    for p in paths:
        dat = [
            p['path']
        ]
        res.append(' '.join(dat))
    return res


#
def format_long(paths: List[Dict[str, Any]]) -> List[str]:
    res = []
    max_usr_len = 4
    max_grp_len = 4
    max_siz_len = 4
    for p in paths:
        max_usr_len = max(len(p['user']), max_usr_len)
        max_grp_len = max(len(p['group']), max_grp_len)
        max_siz_len = max(len(p['size']), max_siz_len)
    for p in paths:
        dat = [
            p['mode'],
            p['nlink'].ljust(2),
            p['user'].ljust(max_usr_len),
            p['group'].ljust(max_grp_len),
            p['size'].rjust(max_siz_len),
            p['date'],
            p['path']
        ]
        res.append(' '.join(dat))
    return res


#
def ls_optproc(paths: List[str], opt: str = '', relbase: str = None) -> List[Dict[str, Any]]:
    res = []
    for p in paths:
        if opt.find('a') < 0 and p.startswith('.'):
            continue
        relpath = p if relbase is None else os.path.join(relbase, p)
        abspath = os.path.abspath(relpath)
        dat = {'path': p, 'abspath': abspath}
        if opt.find('l') >= 0:
            st = stat(abspath)
            dat['stat'] = st
            dat['mode'] = to_rwx(st.st_mode)
            dat['nlink'] = str(st.st_nlink)
            dat['user'] = to_user(st.st_uid)
            dat['group'] = to_group(st.st_gid)
            dat['size'] = str(st.st_size)
            dat['date'] = to_date_format(st.st_mtime)
            dat['mtime'] = st.st_mtime
        res.append(dat)
    if opt.find('t') >= 0:
        key = 'mtime'
        rev = opt.find('r') < 0
    else:
        key = 'path'
        rev = opt.find('r') >= 0
    res = sorted(res, key=itemgetter(key), reverse=rev)
    return res


#
def abspath(path: str) -> str:
    path = str(path)
    return os.path.abspath(path)


# stat
def stat(path: str) -> os.stat_result:
    path = str(path)
    return os.stat(path)


# ls
def ls(path: str, opt: str = '') -> List[Dict[str, Any]]:
    path = str(path)
    if GLOB_PATTERN.match(path):
        paths = glob.glob(path)
        return ls_optproc(paths, opt)
    elif os.path.isdir(path):
        paths = os.listdir(path)
        return ls_optproc(paths, opt, path)
    elif os.path.isfile(path):
        paths = [path]
        return ls_optproc(paths, opt)
    else:
        raise FileNotFoundError('{}: No such file or directory'.format(path))


# find
def find(path: str, name: str = '*') -> List[str]:
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError('{}: No such file or directory'.format(path))
    paths = []
    if fnmatch.fnmatch(path, name):
        paths.extend(glob.glob(path))
    paths.extend(glob.glob(os.path.join(path, '**', name), recursive=True))
    return paths


# cp
def cp(src: str, dst: str, opt: str = '') -> bool:
    shutil.copytree(str(src), str(dst))
    return True


# mv
def mv(src: str, dst: str) -> bool:
    shutil.move(str(src), str(dst))
    return True


# mkdir
def mkdir(path: str, mode: str = '755', opt: str = '') -> bool:
    path = str(path)
    if opt.find('p') >= 0:
        os.makedirs(path, mode=int(mode, 8), exist_ok=True)
    else:
        os.mkdir(path, mode=int(mode, 8))
    return True


# touch
def touch(path: str, mode: str = '644') -> bool:
    Path(path).touch(mode=int(mode, 8), exist_ok=True)
    return True


# rm
def rm(path: str, opt: str = '') -> bool:
    path = str(path)
    if opt.find('f') >= 0 and not os.path.exists(path):
        return True
    if os.path.isdir(path) and opt.find('r') >= 0:
        shutil.rmtree(path)
    else:
        os.remove(path)
    return True


# rmdir
def rmdir(path: str) -> bool:
    path = str(path)
    os.rmdir(path)
    return True


# chmod
def chmod(path: str, mode: str, opt: str = '') -> bool:
    path = str(path)
    paths = find(path) if opt.find('R') >= 0 else [path]
    for p in paths:
        os.chmod(str(p), int(mode, 8))
    return True


# chown
def chown(path: str, user: str = None, group: str = None, opt: str = '') -> bool:
    path = str(path)
    paths = find(path) if opt.find('R') >= 0 else [path]
    for p in paths:
        shutil.chown(str(p), user, group)
    return True


# du
def du():
    pass


# cat
def cat():
    pass


# zcat
def zcat():
    pass


# gzip
def gzip():
    pass


# gunzip
def gunzip():
    pass


# grep
def grep():
    pass


# zgrep
def zgrep():
    pass


# sed
def sed():
    pass
