# -*- conding:utf-8 -*-

import pytest
from argparse import Namespace
from localfs import main, func
from os.path import exists, join, dirname
from typing import TextIO


DIR1 = join(dirname(__file__), 'dir1')
DIR2 = join(dirname(__file__), 'dir2')
DIR3 = join(dirname(__file__), 'dir3')
SUBDIR1 = join(DIR1, 'subdir1')
FILE1_1 = join(DIR1, 'file1.txt')
FILE1_2 = join(DIR1, 'file2.txt.gz')
FILE1_3 = join(DIR1, '.hidden.txt')
FILE2_1 = join(DIR2, 'file1.txt')
FILE3_1 = join(DIR3, 'file1.txt')
BUFFER = []


@pytest.fixture(scope='session', autouse=True)
def scope_session():
    yield


def _quiet(mocker):
    mocker.patch('localfs.func.print_out')
    mocker.patch('localfs.func.print_err')


def _dummy(*args, **kwargs) -> bool:
    return 0


def _print_out(s: str, file: TextIO = None) -> None:
    global BUFFER
    BUFFER.append(s)


def test_to_opt():
    args = Namespace(a=True, b=True, c=True, d=False)
    assert main.to_opt(args, 'a') == '-a'
    assert main.to_opt(args, 'd') == '-'
    assert main.to_opt(args, 'e') == '-'
    assert main.to_opt(args, 'abcd') == '-abc'


def test_ls(mocker):
    _quiet(mocker)
    ret = main.ls(Namespace(file=[DIR1], l=False, a=False, t=False, r=False))
    assert ret == 0
    ret = main.ls(Namespace(file=[DIR1, SUBDIR1], l=False, a=False, t=False, r=False))
    assert ret == 0
    ret = main.ls(Namespace(file=[DIR1, DIR1], l=False, a=False, t=False, r=False))
    assert ret == 0


def test_find(mocker):
    _quiet(mocker)
    ret = main.find(Namespace(path=DIR1, type='', name='*'))
    assert ret == 0


def test_cp(mocker):
    _quiet(mocker)
    target = '{}.1'.format(DIR1)
    ret = main.cp(Namespace(source=[DIR1], target=target, p=False, r=False))
    assert ret == 0
    assert exists(target) is True
    # no such file or directory
    ret = main.cp(Namespace(source=['NoSuchFile'], target=target, p=False, r=False))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[target], f=True, r=True))
    assert ret == 0


def test_mv(mocker):
    _quiet(mocker)
    target1 = '{}.1'.format(DIR1)
    target2 = '{}.2'.format(DIR1)
    ret = main.cp(Namespace(source=[DIR1], target=target1, p=False, r=False))
    assert ret == 0
    ret = main.mv(Namespace(source=[target1], target=target2))
    assert ret == 0
    assert exists(target1) is False
    assert exists(target2) is True
    # no such file or directory
    ret = main.mv(Namespace(source=['NoSuchFile'], target=target2))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[target2], f=True, r=True))
    assert ret == 0


def test_mkdir(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=True))
    assert ret == 0
    assert exists(DIR2) is True
    # already
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    assert ret == 1
    # clean up
    ret = main.rmdir(Namespace(directory=[DIR2]))
    assert ret == 0
    assert exists(DIR2) is False


def test_touch(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    ret = main.touch(Namespace(file=[FILE2_1], mode='644'))
    assert ret == 0
    assert exists(FILE2_1) is True
    # no such dir
    ret = main.touch(Namespace(file=[FILE3_1], mode='644'))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[DIR2], f=True, r=True))
    assert ret == 0


def test_rm(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    ret = main.touch(Namespace(file=[FILE2_1], mode='644'))
    assert ret == 0
    assert exists(FILE2_1) is True
    ret = main.rm(Namespace(file=[DIR2], f=False, r=False))
    assert ret == 1
    ret = main.rm(Namespace(file=[DIR2], f=True, r=True))
    assert ret == 0
    assert exists(FILE2_1) is False
    assert exists(DIR2) is False


def test_rmdir(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    assert ret == 0
    assert exists(DIR2) is True
    ret = main.rmdir(Namespace(directory=[DIR2]))
    assert ret == 0
    assert exists(DIR2) is False
    # no such dir
    ret = main.rmdir(Namespace(directory=[DIR3]))
    assert ret == 1


def test_chmod(mocker):
    _quiet(mocker)
    global BUFFER
    po = mocker.patch('localfs.func.print_out')
    po.side_effect = _print_out
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    ret = main.touch(Namespace(file=[FILE2_1], mode='644'))
    BUFFER = []
    ret = main.ls(Namespace(file=[FILE2_1], l=True, a=False, t=False, r=False))
    assert BUFFER[0].find('rw-r--r--') >= 0
    ret = main.chmod(Namespace(file=[FILE2_1], mode='400', R=False))
    BUFFER = []
    ret = main.ls(Namespace(file=[FILE2_1], l=True, a=False, t=False, r=False))
    assert BUFFER[0].find('r--------') >= 0
    ret = main.chmod(Namespace(file=[DIR2], mode='777', R=True))
    BUFFER = []
    ret = main.ls(Namespace(file=[FILE2_1], l=True, a=False, t=False, r=False))
    assert BUFFER[0].find('rwxrwxrwx') >= 0
    # no such file
    ret = main.chmod(Namespace(file=[FILE3_1], mode='644', R=False))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[DIR2], f=True, r=True))
    assert ret == 0


def test_chown(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    ret = main.touch(Namespace(file=[FILE2_1], mode='644'))
    st = func.get_stat(FILE2_1)
    og = '{}:{}'.format(st['user'], st['group'])
    ret = main.chown(Namespace(file=[FILE2_1], ownergroup=og, R=False))
    assert ret == 0
    # owner only
    og = '{}'.format(st['user'])
    ret = main.chown(Namespace(file=[FILE2_1], ownergroup=og, R=False))
    assert ret == 0
    # no such file
    ret = main.chown(Namespace(file=['NoSuchFile'], ownergroup=og, R=False))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[DIR2], f=True, r=True))
    assert ret == 0


def test_du(mocker):
    _quiet(mocker)
    ret = main.du(Namespace(file=[DIR1], s=True, h=True))
    assert ret == 0
    ret = main.du(Namespace(file=[DIR1], s=True, h=False))
    assert ret == 0
    # no such file
    ret = main.du(Namespace(file=['NoSuchFile'], s=True, R=True))
    assert ret == 1


def test_cat(mocker):
    _quiet(mocker)
    global BUFFER
    po = mocker.patch('localfs.func.print_out')
    po.side_effect = _print_out
    BUFFER = []
    ret = main.cat(Namespace(file=[FILE1_1]))
    assert BUFFER[0].find('hello') >= 0
    assert ret == 0
    # no such file
    ret = main.cat(Namespace(file=['NoSuchFile']))
    assert ret == 1


def test_zcat(mocker):
    _quiet(mocker)
    global BUFFER
    po = mocker.patch('localfs.func.print_out')
    po.side_effect = _print_out
    BUFFER = []
    ret = main.zcat(Namespace(file=[FILE1_2]))
    assert BUFFER[0].find('hello') >= 0
    assert ret == 0
    # no such file
    ret = main.zcat(Namespace(file=['NoSuchFile']))
    assert ret == 1


def test_gzip(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    ret = main.touch(Namespace(file=[FILE2_1], mode='644'))
    ret = main.gzip(Namespace(file=[FILE2_1]))
    assert exists(FILE2_1 + '.gz') is True
    assert ret == 0
    # no such file
    ret = main.gzip(Namespace(file=['NoSuchFile']))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[DIR2], f=True, r=True))
    assert ret == 0


def test_gunzip(mocker):
    _quiet(mocker)
    ret = main.mkdir(Namespace(directory=[DIR2], mode='755', p=False))
    ret = main.touch(Namespace(file=[FILE2_1], mode='644'))
    ret = main.gzip(Namespace(file=[FILE2_1]))
    assert exists(FILE2_1) is False
    ret = main.gunzip(Namespace(file=[FILE2_1 + '.gz']))
    assert exists(FILE2_1) is True
    assert ret == 0
    # no such file
    ret = main.gunzip(Namespace(file=['NoSuchFile']))
    assert ret == 1
    # clean up
    ret = main.rm(Namespace(file=[DIR2], f=True, r=True))
    assert ret == 0


def test_nop(mocker):
    _quiet(mocker)
    ret = main.nop(Namespace())
    assert ret == 0


def test_main(mocker):
    _quiet(mocker)
    parser = mocker.patch('localfs.main.ArgumentParser')
    parser.return_value = parser
    parser.parse_args.return_value = Namespace(func=_dummy)
    ret = main.main()
    assert ret == 0
    parser.parse_args.return_value = Namespace(func=None)
    ret = main.main()
    assert ret == 1
