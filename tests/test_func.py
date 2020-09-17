# -*- conding:utf-8 -*-

import io
import os
import pytest
from datetime import datetime
from localfs import func
from os.path import exists, join, dirname


DIR1 = join(dirname(__file__), 'dir1')
DIR2 = join(dirname(__file__), 'dir2')
FILE1_1 = join(DIR1, 'file1.txt')
FILE1_2 = join(DIR1, 'file2.txt.gz')
FILE2_1 = join(DIR2, 'file1.txt')


@pytest.fixture(scope='session', autouse=True)
def scope_session():
    yield
    func.rm(DIR2, '-fr')


def test_rwx():
    res = func.rwx((0o700 & 0o700) >> 6, 0 & 0o4000)
    assert res == 'rwx'
    res = func.rwx((0o70 & 0o70) >> 3, 0 & 0o2000)
    assert res == 'rwx'
    res = func.rwx((0o7 & 0o7), 0 & 0o1000)
    assert res == 'rwx'


def test_to_rwx():
    res = func.to_rwx(0o100777)
    assert res == '-rwxrwxrwx'
    res = func.to_rwx(0o040755)
    assert res == 'drwxr-xr-x'


def test_to_perm():
    perm = func.to_perm(0o755)
    assert perm == '755'


def test_to_user():
    user = func.to_user(0)
    assert user == 'root'


def test_to_group():
    group = func.to_group(0)
    assert group == 'wheel'


def test_to_date_format():
    ts = datetime.now().timestamp()
    dt = func.to_date_format(ts)
    assert dt.find(':') >= 0
    dt = func.to_date_format(0)
    assert dt.find(':') < 0


def test_get_stat():
    inf = func.get_stat(__file__)
    assert 'path' in inf
    assert 'stat' in inf


def test_format_short():
    inf = func.get_stat(__file__)
    inf['name'] = 'file1'
    paths = func.format_short([inf])
    assert type(paths[0]) is str
    assert len(paths[0].split(' ')) == 1


def test_format_long():
    inf = func.get_stat(__file__)
    inf['name'] = 'file1'
    paths = func.format_long([inf])
    assert type(paths[0]) is str
    assert len(paths[0].split(' ')) > 1


def test_is_glob_path():
    assert func.is_glob_path('test/dir1') is False
    assert func.is_glob_path('test/d?r1') is True
    assert func.is_glob_path('test/dir*') is True


def test_split_glob_path():
    path = '.'
    base, sub = func.split_glob_path(path)
    assert base == '.'
    assert sub == ''
    path = './test/test.txt'
    base, sub = func.split_glob_path(path)
    assert base == './test/test.txt'
    assert sub == ''
    path = 'test/*'
    base, sub = func.split_glob_path(path)
    assert base == 'test'
    assert sub == '*'
    path = '/aaa/bbb/c*/ddd.txt'
    [base, sub] = func.split_glob_path(path)
    assert base == '/aaa/bbb'
    assert sub == 'c*/ddd.txt'
    path = '*'
    [base, sub] = func.split_glob_path(path)
    assert base == ''
    assert sub == '*'


def test_split_path():
    base, sub = func.split_path('aaa/bbb/ccc')
    assert base == 'aaa'
    assert sub == 'bbb/ccc'


def test_abspath():
    bfr = '.'
    aft = func.abspath(bfr)
    assert bfr != aft


def test_stat():
    stat = func.stat('README.md')
    assert stat is not None
    assert func.to_perm(stat.st_mode) == '644'


def test_ls():
    dirs = func.ls(FILE1_1)
    assert len(dirs) == 1
    assert dirs[0]['children'][0]['name'] == 'file1.txt'
    print(dirs)
    dirs = func.ls(DIR1)
    assert len(dirs) == 1
    assert len(dirs[0]['children']) == 3
    dirs = func.ls('tests/dir1*')
    assert len(dirs) == 1
    assert len(dirs[0]['children']) == 3


def test_find():
    paths = func.find(DIR1)
    assert len(paths) == 5
    paths = func.find('tests/dir1')
    assert len(paths) == 5
    for p in paths:
        func.abspath(p)


def test_cp():
    dir1 = '{}.1'.format(DIR1)
    func.cp(DIR1, dir1)
    assert os.path.isdir(dir1) is True
    func.rm(dir1, '-fr')
    assert os.path.isdir(dir1) is False


def test_mv():
    dir1 = '{}.1'.format(DIR1)
    dir2 = '{}.2'.format(DIR1)
    func.cp(DIR1, dir1)
    func.mv(dir1, dir2)
    assert os.path.isdir(dir1) is False
    assert os.path.isdir(dir2) is True
    func.rm(dir2, '-fr')
    assert os.path.isdir(dir2) is False


def test_mkdir():
    func.mkdir(DIR2)
    assert exists(DIR2)
    func.rmdir(DIR2)


def test_touch():
    func.mkdir(DIR2)
    func.touch(FILE2_1)
    assert exists(FILE2_1)
    func.rm(DIR2, '-r')


def test_rm():
    func.mkdir(DIR2)
    func.touch(FILE2_1)
    assert exists(FILE2_1)
    func.rm(FILE2_1)
    assert not exists(FILE2_1)
    with pytest.raises(Exception):
        func.rm(DIR2)
    func.rm(DIR2, '-r')
    assert not exists(DIR2)
    func.rm(DIR2, '-fr')


def test_rmdir():
    func.mkdir(DIR2)
    assert exists(DIR2)
    func.rmdir(DIR2)
    assert not exists(DIR2)


def test_chmod():
    func.mkdir(DIR2)
    func.touch(FILE2_1)
    stat = func.stat(FILE2_1)
    assert func.to_perm(stat.st_mode) == '644'
    func.chmod(DIR2, '777', '-R')
    stat = func.stat(DIR2)
    assert func.to_perm(stat.st_mode) == '777'
    stat = func.stat(FILE2_1)
    assert func.to_perm(stat.st_mode) == '777'
    func.chmod(FILE2_1, '644')
    stat = func.stat(FILE2_1)
    assert func.to_perm(stat.st_mode) == '644'
    func.rm(DIR2, '-fr')


def test_chown():
    func.mkdir(DIR2)
    func.touch(FILE2_1)
    stat = func.stat(FILE2_1)
    user = func.to_user(stat.st_uid)
    assert func.to_user(stat.st_uid) == user
    func.chown(DIR2, user=user, opt='-R')
    stat = func.stat(DIR2)
    assert func.to_user(stat.st_uid) == user
    stat = func.stat(FILE2_1)
    assert func.to_user(stat.st_uid) == user
    func.chown(FILE2_1, user=user)
    stat = func.stat(FILE2_1)
    assert func.to_user(stat.st_uid) == user
    func.rm(DIR2, '-fr')


def test_du():
    res = func.du(DIR1)
    assert res is not None


def test_cat():
    out = io.StringIO()
    func.cat(FILE1_1, out)
    contents = out.getvalue()
    assert contents.find('hello') >= 0


def test_zcat():
    out = io.StringIO()
    func.zcat(FILE1_2, out)
    contents = out.getvalue()
    assert contents.find('hello') >= 0


def test_gzip():
    pass


def test_gunzip():
    pass
