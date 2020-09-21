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
FILE1_3 = join(DIR1, '.hidden.txt')
FILE2_1 = join(DIR2, 'file1.txt')


@pytest.fixture(scope='session', autouse=True)
def scope_session():
    yield
    # DIR2 is temprorary so clean it
    func.rm(DIR2, '-fr')


def test_rwx():
    res = func.rwx((0o700 & 0o700) >> 6, 0 & 0o4000)
    assert res == 'rwx'
    res = func.rwx((0o70 & 0o70) >> 3, 0 & 0o2000)
    assert res == 'rwx'
    res = func.rwx((0o7 & 0o7), 0 & 0o1000)
    assert res == 'rwx'
    res = func.rwx((0o7 & 0o7), 0o1000 & 0o1000)
    assert res == 'rws'
    res = func.rwx((0o7 & 0o7), 0o1000 & 0o1000, True)
    assert res == 'rwt'


def test_to_rwx():
    res = func.to_rwx(0o100777)
    assert res == '-rwxrwxrwx'
    res = func.to_rwx(0o040755)
    assert res == 'drwxr-xr-x'
    res = func.to_rwx(0o010755)
    assert res == 'prwxr-xr-x'
    res = func.to_rwx(0o020755)
    assert res == 'crwxr-xr-x'
    res = func.to_rwx(0o060755)
    assert res == 'brwxr-xr-x'
    res = func.to_rwx(0o120755)
    assert res == 'lrwxr-xr-x'
    res = func.to_rwx(0o140755)
    assert res == 'srwxr-xr-x'
    res = func.to_rwx(0o150755)
    assert res == '?rwxr-xr-x'


def test_to_perm():
    perm = func.to_perm(0o755)
    assert perm == '755'


def test_to_user():
    user = func.to_user(0)
    assert user == 'root'
    user = func.to_user(-1)
    assert user == '-1'


def test_to_group():
    group = func.to_group(0)
    assert group == 'wheel'
    group = func.to_group(12345)
    assert group == '12345'


def test_to_date_format():
    ts = datetime.now().timestamp()
    dt = func.to_date_format(ts)
    assert dt.find(':') >= 0
    dt = func.to_date_format(0)
    assert dt.find(':') < 0
    dt = func.to_date_format(None)
    assert dt == '(unknown date)'


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


def test_get_size():
    assert func.get_size(DIR1) > 0
    with pytest.raises(FileNotFoundError):
        func.get_size('NoSuchFile')


def test_readable_size():
    assert func.readable_size(536870912) == '512M'


def test_ls():
    # file
    dirs = func.ls(FILE1_1)
    assert len(dirs) == 1
    assert dirs[0]['children'][0]['name'] == 'file1.txt'
    # file with option
    dirs = func.ls(FILE1_1, '-ltra')
    assert len(dirs) == 1
    assert len(dirs[0]['children']) == 1
    # hidden file
    dirs = func.ls(FILE1_3, '-ltr')
    assert len(dirs) == 0
    # dir
    dirs = func.ls(DIR1)
    assert len(dirs) == 1
    assert len(dirs[0]['children']) == 3
    # dir with option
    dirs = func.ls(DIR1, '-l')
    assert len(dirs) == 1
    assert len(dirs[0]['children']) == 3
    # glob
    dirs = func.ls('tests/dir1*')
    assert len(dirs) == 1
    assert len(dirs[0]['children']) == 3
    # no such file or directory
    with pytest.raises(FileNotFoundError):
        func.ls('NoSuchDir')


def test_find():
    # dir
    paths = func.find(DIR1)
    assert len(paths) == 6
    # glob dir
    paths = func.find('tests/dir*')
    assert len(paths) == 6
    # dir with file type
    paths = func.find(DIR1, type='f')
    assert len(paths) == 4
    # dir with directory type
    paths = func.find(DIR1, type='d')
    assert len(paths) == 2
    # dir with name *file1*
    paths = func.find(DIR1, name='*file1*')
    assert len(paths) == 2
    # file
    paths = func.find(FILE1_1)
    assert len(paths) == 1
    # no such file or directory
    with pytest.raises(FileNotFoundError):
        func.find('NoSuchDir')


def test_cp():
    target = '{}.1'.format(DIR1)
    func.cp(DIR1, target)
    assert os.path.isdir(target) is True
    # clean up
    func.rm(target, '-fr')
    assert os.path.isdir(target) is False


def test_mv():
    target1 = '{}.1'.format(DIR1)
    target2 = '{}.2'.format(DIR1)
    func.cp(DIR1, target1)
    func.mv(target1, target2)
    assert os.path.isdir(target1) is False
    assert os.path.isdir(target2) is True
    # clean up
    func.rm(target2, '-fr')
    assert os.path.isdir(target2) is False


def test_mkdir():
    func.mkdir(DIR2)
    assert exists(DIR2)
    # already exists
    with pytest.raises(Exception):
        func.mkdir(DIR2)
    # force mkdir
    func.mkdir(DIR2, '-p')
    # clean up
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
    # no such file or directory
    with pytest.raises(FileNotFoundError):
        func.cat('NoSuchDir')
    # path is directory
    with pytest.raises(Exception):
        func.cat(DIR1)


def test_zcat():
    out = io.StringIO()
    func.zcat(FILE1_2, out)
    contents = out.getvalue()
    assert contents.find('hello') >= 0
    # no such file or directory
    with pytest.raises(FileNotFoundError):
        func.zcat('NoSuchDir')
    # path is directory
    with pytest.raises(Exception):
        func.zcat(DIR1)


def test_gzip():
    func.mkdir(DIR2)
    func.touch(FILE2_1)
    func.gzip(FILE2_1)
    assert not os.path.exists(FILE2_1)
    assert os.path.exists(FILE2_1 + '.gz')
    # already gz
    with pytest.raises(Exception):
        func.gzip(FILE2_1 + '.gz')
    # no such file or directory
    with pytest.raises(FileNotFoundError):
        func.gzip('NoSuchFile')
    func.rm(DIR2, '-fr')


def test_gunzip():
    func.mkdir(DIR2)
    func.touch(FILE2_1)
    func.gzip(FILE2_1)
    func.gunzip(FILE2_1 + '.gz')
    assert os.path.exists(FILE2_1)
    assert not os.path.exists(FILE2_1 + '.gz')
    # not gz
    with pytest.raises(Exception):
        func.gunzip(FILE2_1)
    # no such file or directory
    with pytest.raises(FileNotFoundError):
        func.gunzip('NoSuchFile')
    func.rm(DIR2, '-fr')


def test_grep():
    assert func.grep(FILE1_1, 'test') is True


def test_zgrep():
    assert func.zgrep(FILE1_1, 'test') is True


def test_sed():
    assert func.sed() is True
