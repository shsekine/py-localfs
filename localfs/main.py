# -*- conding:utf-8 -*-

import argparse
import sys
from localfs import func
from typing import List, Dict, Any


# ls
def ls(args: object):
    rc = 0
    opt = ''
    opt += 'a' if args.a else ''
    opt += 'l' if args.l else ''
    opt += 'r' if args.r else ''
    opt += 't' if args.t else ''
    for af in args.file:
        paths = func.ls(af, opt)
        if args.l:
            dsps = func.format_long(paths)
        else:
            dsps = func.format_short(paths)
        for d in dsps:
            print(d)
    return rc


# find
def find(args: object):
    rc = 0
    paths = func.find(args.path, args.name)
    for p in paths:
        print(p)
    return rc


# cp
def cp(args: object):
    rc = 0
    paths = func.find(args.path, args.name)
    for p in paths:
        print(p)
    return rc


# mv
def mv(args: object):
    rc = 0
    paths = func.find(args.path, args.name)
    for p in paths:
        print(p)
    return rc


# mkdir
def mkdir(args: object):
    rc = 0
    opt = ''
    opt += 'p' if args.p else ''
    func.mkdir(args.path, args.mode, opt)
    return rc


# touch
def touch(args: object):
    rc = 0
    return rc


# rm
def rm(args: object):
    rc = 0
    return rc


# rmdir
def rmdir(args: object):
    rc = 0
    return rc


# chmod
def chmod(args: object):
    rc = 0
    return rc


# chown
def chown(args: object):
    rc = 0
    return rc


def main():
    parser = argparse.ArgumentParser(description='Python local filesystem access library')
    subparsers = parser.add_subparsers()
    subparsers.required = True

    ls_parser = subparsers.add_parser('ls', help='ls')
    ls_parser.add_argument('-a', action='store_true')
    ls_parser.add_argument('-l', action='store_true')
    ls_parser.add_argument('-r', action='store_true')
    ls_parser.add_argument('-t', action='store_true')
    ls_parser.add_argument('file', nargs='*', default=['.'])
    ls_parser.set_defaults(func=ls)

    find_parser = subparsers.add_parser('find', help='find')
    find_parser.add_argument('-name', nargs='?', default='*')
    find_parser.add_argument('path')
    find_parser.set_defaults(func=find)

    cp_parser = subparsers.add_parser('cp', help='cp')
    cp_parser.add_argument('-p', action='store_true')
    cp_parser.add_argument('-r', action='store_true')
    cp_parser.add_argument('source', nargs='*', default=['.'])
    cp_parser.add_argument('target')
    cp_parser.set_defaults(func=cp)

    mv_parser = subparsers.add_parser('mv', help='mv')
    mv_parser.add_argument('source', nargs='*', default=['.'])
    mv_parser.add_argument('target')
    mv_parser.set_defaults(func=mv)

    mkdir_parser = subparsers.add_parser('mkdir', help='mkdir')
    mkdir_parser.add_argument('-p', action='store_true')
    mkdir_parser.add_argument('-m', '--mode')
    mkdir_parser.add_argument('directory')
    mkdir_parser.set_defaults(func=mkdir)

    touch_parser = subparsers.add_parser('touch', help='touch')
    touch_parser.add_argument('file')
    touch_parser.set_defaults(func=touch)

    rm_parser = subparsers.add_parser('rm', help='rm')
    rm_parser.add_argument('-f', action='store_true')
    rm_parser.add_argument('-r', action='store_true')
    rm_parser.add_argument('file', nargs='+', default=['.'])
    rm_parser.set_defaults(func=rm)

    rmdir_parser = subparsers.add_parser('rmdir', help='rmdir')
    rmdir_parser.add_argument('directory', nargs='+', default=['.'])
    rmdir_parser.set_defaults(func=rmdir)

    chmod_parser = subparsers.add_parser('chmod', help='chmod')
    chmod_parser.add_argument('source', nargs='*', default=['.'])
    chmod_parser.add_argument('target')
    chmod_parser.set_defaults(func=chmod)

    chown_parser = subparsers.add_parser('chown', help='chown')
    chown_parser.add_argument('source', nargs='*', default=['.'])
    chown_parser.add_argument('target')
    chown_parser.set_defaults(func=chown)

    args = parser.parse_args()

    try:
        ret = args.func(args)
        exit(ret)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
