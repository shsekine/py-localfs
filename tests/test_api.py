# -*- conding:utf-8 -*-

import json
from localfs import api
from os.path import join, dirname


DIR1 = join(dirname(__file__), 'dir1')
DIR2 = join(dirname(__file__), 'dir2')
FILE1 = join(DIR2, 'file1.txt')


def test_ls():
    res = api.ls(DIR1)
    assert type(res) is str
    res_obj = json.loads(res)
    assert res_obj['status'] == 0
    assert len(res_obj['stdout']) == 2
