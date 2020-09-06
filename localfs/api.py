# -*- conding:utf-8 -*-

import json
from types import SimpleNamespace
from typing import List, Dict, Any
from localfs import func


"""
Success example:
{"status": 0, "stdout": "", "stderr": ""}

Failure example:
{"status": 1, "stdout": "", "stderr": "[Errno 2] No such file or directory: 'test2'"}
"""


#
def json_response(status: int, stdout: Any, stderr: Any) -> str:
    return json.dumps({
        'status': status,
        'stdout': stdout,
        'stderr': stderr
    })


# ls
def ls(path: str, opt: str = '') -> str:
    try:
        paths = func.ls(path, opt)
        return json_response(0, paths, '')
    except Exception as e:
        return json_response(1, '', e)


# find
def find(path: str, name: str = '*') -> List[str]:
    pass


# cp
def cp(src: str, dst: str, opt: str = '') -> bool:
    pass


# mv
def mv(src: str, dst: str) -> bool:
    pass


# mkdir
def mkdir(path: str, mode: str = '755', opt: str = '') -> bool:
    pass


# touch
def touch(path: str, mode: str = '644') -> bool:
    pass


# rm
def rm(path: str, opt: str = '') -> bool:
    pass


# rmdir
def rmdir(path: str) -> bool:
    pass


# chmod
def chmod(path: str, mode: str, opt: str = '') -> bool:
    pass


# chown
def chown(path: str, user: str = None, group: str = None, opt: str = '') -> bool:
    pass


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
