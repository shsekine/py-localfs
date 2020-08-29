# -*- conding:utf-8 -*-

import pytest
from localfs import func
from os.path import exists, join, dirname


DIR1 = join(dirname(__file__), 'dir1')
DIR2 = join(dirname(__file__), 'dir2')
FILE1 = join(DIR2, 'file1.txt')


@pytest.fixture(scope='session', autouse=True)
def scope_session():
    yield
    func.rm(DIR2, '-fr')


def test_stat():
    stat = func.stat('README.md')
    print(stat)
    assert stat is not None


def test_ls():
    paths = func.ls(DIR1)
    assert len(paths) == 2
    paths = func.ls('tests/dir1')
    assert len(paths) == 2


def test_find():
    paths = func.find(DIR1)
    assert len(paths) == 4
    paths = func.find('tests/dir1')
    assert len(paths) == 4


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
