# -*- conding:utf-8 -*-

import glob
import grp
import os
import pwd
import re
import shutil
import stat as st_stat
from pathlib import Path
from typing import List, Dict, Any


GLOB_PATTERN = re.compile(r'^.*[*?].*$')


#
def analyze_path(path: str) -> Dict[str, Any]:
    tokens = os.path.split(path)
    base = []
    sub = []
    is_glob = False
    for t in tokens:
        if GLOB_PATTERN.match(t):
            is_glob = True
        if is_glob:
            sub.append(t)
        else:
            base.append(t)
    return {
        'path': path,
        'is_glob': is_glob,
        'base': os.path.sep.join(base),
        'sub': os.path.sep.join(sub)
    }


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


# stat
def stat(path: str) -> os.stat_result:
    return os.stat(path)


# ls
def ls(path: str) -> List[Path]:
    info = analyze_path(path)
    if info['is_glob']:
        paths = glob.glob(path)
    elif os.path.isdir(path):
        paths = os.listdir(path)
    elif os.path.isfile(path):
        paths = [path]
    else:
        raise FileNotFoundError('{}: No such file or directory'.format(path))
    return paths


# find
def find(path: str, name: str = '*') -> List[str]:
    res = glob.glob(path)
    res.extend(glob.glob(os.path.join(path, '**', name), recursive=True))
    return res


# grep
def grep():
    pass


# cp
def cp(src: str, dst: str) -> bool:
    shutil.copytree(src, dst)
    return True


# mv
def mv(src: str, dst: str) -> bool:
    shutil.move(src, dst)
    return True


# mkdir
def mkdir(path: str, mode: str = '755', opt: str = '') -> bool:
    if opt.find('p') >= 0:
        os.makedirs(path, mode=int(mode, 8), exist_ok=True)
    else:
        os.mkdir(path)
    return True


# touch
def touch(path: str, mode: str = '644') -> bool:
    Path(path).touch(mode=int(mode, 8), exist_ok=True)
    return True


# rm
def rm(path: str, opt: str = '') -> bool:
    if opt.find('f') >= 0 and not os.path.exists(path):
        return True
    if os.path.isdir(path) and opt.find('r') >= 0:
        shutil.rmtree(path)
    else:
        os.remove(path)
    return True


# rmdir
def rmdir(path: str) -> bool:
    os.rmdir(path)
    return True


# chmod
def chmod(path: str, mode: str, opt: str = '') -> bool:
    paths = find(path) if opt.find('R') >= 0 else [path]
    for p in paths:
        os.chmod(p, int(mode, 8))
    return True


# chown
def chown(path: str, user: str = None, group: str = None, opt: str = '') -> bool:
    paths = find(path) if opt.find('R') >= 0 else [path]
    for p in paths:
        shutil.chown(p, user, group)
    return True
