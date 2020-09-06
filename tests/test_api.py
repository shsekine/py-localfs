# -*- conding:utf-8 -*-

import json
import pytest
from localfs import api
from os.path import exists, join, dirname


DIR1 = join(dirname(__file__), 'dir1')
DIR2 = join(dirname(__file__), 'dir2')
FILE1 = join(DIR2, 'file1.txt')


def test_ls():
    r = api.ls(DIR1)
    assert type(r) is str
    res = json.loads(r)
    assert res['status'] == 0
    assert len(res['stdout']) == 2
