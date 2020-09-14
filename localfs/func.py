# -*- conding:utf-8 -*-

import fnmatch
import gzip as gz
import grp
import os
import pwd
import re
import shutil
import stat as st_stat
import sys
import time
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Any, TextIO


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
def get_stat(path: str) -> Dict[str, Any]:
    st = stat(path)
    return {
        'path': path,
        'stat': st,
        'mode': to_rwx(st.st_mode),
        'nlink': str(st.st_nlink),
        'user': to_user(st.st_uid),
        'group': to_group(st.st_gid),
        'size': str(st.st_size),
        'date': to_date_format(st.st_mtime),
        'mtime': st.st_mtime
    }


#
def format_short(paths: List[Dict[str, Any]]) -> List[str]:
    res = []
    for p in paths:
        inf = [
            p['name']
        ]
        res.append(' '.join(inf))
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
        inf = [
            p['mode'],
            p['nlink'].rjust(2),
            p['user'].ljust(max_usr_len),
            p['group'].ljust(max_grp_len),
            p['size'].rjust(max_siz_len),
            p['date'],
            p['name']
        ]
        res.append(' '.join(inf))
    return res


#
def is_glob_path(path: str) -> bool:
    return GLOB_PATTERN.match(path)


#
def split_glob_path(path: str) -> List[Any]:
    if is_glob_path(path):
        t_idx = 0
        for i, c in enumerate(path):
            if c == '*' or c == '?':
                break
            elif c == os.path.sep:
                t_idx = i
        base = path[:t_idx]
        sub = path[t_idx:].lstrip(os.path.sep)
    else:
        base = path
        sub = ''
    return [base, sub]


#
def split_path(path: str) -> List[str]:
    tokens = path.split(os.path.sep)
    base = tokens[0]
    sub = os.path.sep.join(tokens[1:])
    return [base, sub]


#
def abspath(path: str) -> str:
    path = str(path)
    return os.path.abspath(path)


# stat
def stat(path: str) -> os.stat_result:
    path = str(path)
    return os.stat(path)


#
def _ls(path: str, sub: str, opt: str, res: List[str]) -> bool:
    pat, next = split_path(sub)
    if os.path.isdir(path):
        dir = {'path': path, 'children': []}
        for p in os.listdir(path):
            if pat != '' and not fnmatch.fnmatch(p, pat):
                continue
            if opt.find('a') < 0 and p.startswith('.'):
                continue
            pp = os.path.join(path, p)
            if pat != '' and os.path.isdir(pp):
                _ls(pp, next, opt, res)
            else:
                file = {'name': p, 'path': pp}
                if opt.find('l') >= 0:
                    st = get_stat(pp)
                    file.update(st)
                dir['children'].append(file)
        if pat == '':
            res.append(dir)
    else:
        dir_name = os.path.dirname(path)
        base_name = os.path.basename(path)
        dir = {'path': dir_name, 'children': []}
        if opt.find('a') < 0 and base_name.startswith('.'):
            return True
        file = {'name': base_name, 'path': path}
        if opt.find('l') >= 0:
            st = get_stat(path)
            file.update(st)
        dir['children'].append(file)
        res.append(dir)
    return True


# ls
def ls(path: str, opt: str = '') -> List[Dict[str, Any]]:
    path = str(path)
    base, sub = split_glob_path(path)
    if base == '' or not os.path.exists(base):
        raise FileNotFoundError('{}: No such file or directory'.format(base))
    match_dirs = []
    _ls(base, sub, opt, match_dirs)

    res = []
    for dir in match_dirs:
        if opt.find('t') >= 0:
            k = 'mtime'
            r = opt.find('r') < 0
        else:
            k = 'path'
            r = opt.find('r') >= 0
        dir['children'] = sorted(dir['children'], key=itemgetter(k), reverse=r)
        res.append(dir)
    return res


# _find
def _find(path: str, sub: str, type: str, name: str, res: List[str]) -> bool:
    if type != 'f':
        if name == '' or fnmatch.fnmatch(os.path.basename(path), name):
            res.append(path)
    if os.path.isdir(path):
        pat, next = split_path(sub)
        for p in os.listdir(path):
            if pat != '' and not fnmatch.fnmatch(p, pat):
                continue
            pp = os.path.join(path, p)
            if os.path.isdir(pp):
                _find(pp, next, type, name, res)
            elif type != 'd':
                if name == '' or fnmatch.fnmatch(p, name):
                    res.append(pp)
    return True


# find
def find(path: str, type: str = '', name: str = '') -> List[str]:
    path = str(path)
    base, sub = split_glob_path(path)
    if base == '' or not os.path.exists(base):
        raise FileNotFoundError('{}: No such file or directory'.format(base))
    res = []
    _find(base, sub, type, name, res)
    return res


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
def du(path: str, opt: str = '') -> List[tuple]:
    path = str(path)
    paths = find(path) if opt.find('s') < 0 else [path]
    res = []
    for p in paths:
        r = shutil.disk_usage(path)
        res.append(r)
    return res


# cat
def cat(path: str, file: TextIO = sys.stdout) -> bool:
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError('cat: {}: No such file or directory'.format(path))
    elif os.path.isdir(path):
        raise Exception('cat: {}: Is a directory'.format(path))
    with open(path, encoding='utf-8') as f:
        for line in f:
            print(line.rstrip('\n'), file=file)
    return True


# zcat
def zcat(path: str, file: TextIO = sys.stdout) -> bool:
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError('zcat: {}: No such file or directory'.format(path))
    elif os.path.isdir(path):
        raise Exception('zcat: {}: Is a directory'.format(path))
    with gz.open(path, 'rb') as f_in:
        for line in f_in:
            print(line.decode('utf-8').rstrip('\n'), file=file)
    return True


# gzip
def gzip(path: str) -> bool:
    path = str(path)
    if path.endswith('.gz'):
        raise Exception('gzip: {} already has .gz suffix -- unchanged'.format(path))
    elif not os.path.isfile(path):
        raise FileNotFoundError('gzip: {}: No such file or directory'.format(path))
    with open(path, 'rb') as f_in:
        with gz.open('{}.gz'.format(path), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    rm(path)
    return True


# gunzip
def gunzip(path: str) -> bool:
    path = str(path)
    if not path.endswith('.gz'):
        raise Exception('gunzip: {}: unknown suffix -- ignored'.format(path))
    elif not os.path.isfile(path):
        raise FileNotFoundError('gunzip: {}: No such file or directory'.format(path))
    with gz.open(path, 'rb') as f_in:
        with open(re.sub(r'\.gz$', '', path), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    rm(path)
    return True


# grep
def grep():
    pass


# zgrep
def zgrep():
    pass


# sed
def sed():
    pass
