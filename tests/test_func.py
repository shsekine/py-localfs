# -*- conding:utf-8 -*-

import pytest
from datetime import datetime
from localfs import func
from os.path import exists, join, dirname


DIR1 = join(dirname(__file__), 'dir1')
DIR2 = join(dirname(__file__), 'dir2')
FILE1 = join(DIR2, 'file1.txt')


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


def test_get_path_info():
    inf = func.get_path_info(__file__)
    assert 'stat' not in inf
    inf = func.get_path_info(__file__, '-l')
    assert 'stat' in inf


def test_format_short():
    inf = func.get_path_info(__file__)
    paths = func.format_short([inf])
    assert type(paths[0]) is str
    assert len(paths[0].split(' ')) == 1


def test_format_long():
    inf = func.get_path_info(__file__, '-l')
    paths = func.format_long([inf])
    assert type(paths[0]) is str
    assert len(paths[0].split(' ')) > 1


def test_optproc_ls():
    paths = [DIR1]
    infs = func.optproc_ls(paths, '-l')
    assert type(infs[0]) is dict


def test_abspath():
    bfr = '.'
    aft = func.abspath(bfr)
    assert bfr != aft


def test_stat():
    stat = func.stat('README.md')
    assert stat is not None
    assert func.to_perm(stat.st_mode) == '644'


def test_ls():
    paths = func.ls(DIR1)
    assert len(paths) == 2
    paths = func.ls('tests/dir1')
    assert len(paths) == 2
    # paths = func.ls('tests/dir*', '-l')
    # assert len(paths) == 2
    # fpaths = func.format_long(paths)
    # assert len(fpaths) == 2


def test_find():
    paths = func.find(DIR1)
    assert len(paths) == 4
    paths = func.find('tests/dir1')
    assert len(paths) == 4
    for p in paths:
        func.abspath(p)


def test_mkdir():
    func.mkdir(DIR2)
    assert exists(DIR2)
    func.rmdir(DIR2)


def test_touch():
    func.mkdir(DIR2)
    func.touch(FILE1)
    assert exists(FILE1)
    func.rm(DIR2, '-r')


def test_rm():
    func.mkdir(DIR2)
    func.touch(FILE1)
    assert exists(FILE1)
    func.rm(FILE1)
    assert not exists(FILE1)
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
    func.touch(FILE1)
    stat = func.stat(FILE1)
    assert func.to_perm(stat.st_mode) == '644'
    func.chmod(DIR2, '777', '-R')
    stat = func.stat(DIR2)
    assert func.to_perm(stat.st_mode) == '777'
    stat = func.stat(FILE1)
    assert func.to_perm(stat.st_mode) == '777'
    func.chmod(FILE1, '644')
    stat = func.stat(FILE1)
    assert func.to_perm(stat.st_mode) == '644'
    func.rm(DIR2, '-fr')


def test_chown():
    func.mkdir(DIR2)
    func.touch(FILE1)
    stat = func.stat(FILE1)
    user = func.to_user(stat.st_uid)
    assert func.to_user(stat.st_uid) == user
    func.chown(DIR2, user=user, opt='-R')
    stat = func.stat(DIR2)
    assert func.to_user(stat.st_uid) == user
    stat = func.stat(FILE1)
    assert func.to_user(stat.st_uid) == user
    func.chown(FILE1, user=user)
    stat = func.stat(FILE1)
    assert func.to_user(stat.st_uid) == user
    func.rm(DIR2, '-fr')


def test_du():
    res = func.du(DIR1)
    assert res is not None
