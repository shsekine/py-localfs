# -*- conding:utf-8 -*-

import sys
from argparse import ArgumentParser, Namespace
from localfs import func


#
def print_err(s: str) -> None:
    print(s, file=sys.stderr)


#
def to_opt(args: Namespace, flag: str) -> str:
    opt = '-'
    # charactor loop
    for f in flag:
        opt += f if hasattr(args, f) and getattr(args, f) is True else ''
    return opt

    
# ls
def ls(args: Namespace) -> int:
    rc = 0
    opt = to_opt(args, 'alrt')
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
def find(args: Namespace) -> int:
    rc = 0
    paths = func.find(args.path, args.name)
    for p in paths:
        print(p)
    return rc


# cp
def cp(args: Namespace) -> int:
    rc = 0
    opt = to_opt(args, 'pr')
    for s in args.source:
        try:
            func.cp(s, args.target, opt)
        except Exception as e:
            print_err(e)
            rc = 1
            break 
    return rc


# mv
def mv(args: Namespace) -> int:
    rc = 0
    for s in args.source:
        try:
            func.mv(s, args.target)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# mkdir
def mkdir(args: Namespace) -> int:
    rc = 0
    opt = to_opt(args, 'p')
    for d in args.directory:
        try:
            func.mkdir(d, args.mode, opt)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# touch
def touch(args: Namespace) -> int:
    rc = 0
    for f in args.file:
        try:
            func.touch(f, args.mode)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# rm
def rm(args: Namespace) -> int:
    rc = 0
    opt = to_opt(args, 'fr')
    for f in args.file:
        try:
            func.rm(f, opt)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# rmdir
def rmdir(args: Namespace):
    rc = 0
    for d in args.directory:
        try:
            func.rmdir(d)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# chmod
def chmod(args: Namespace):
    rc = 0
    opt = to_opt(args, 'R')
    for f in args.file:
        try:
            func.chmod(f, args.mode, opt)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# chown
def chown(args: Namespace):
    rc = 0
    opt = to_opt(args, 'R')
    tokens = args.ownergroup.split(':')
    if len(tokens) > 1:
        owner = tokens[0]
        group = tokens[1]
    else:
        owner = tokens[0]
        group = None
    for f in args.file:
        try:
            func.chown(f, owner, group, opt)
        except Exception as e:
            print_err(e)
            rc = 1
            break
    return rc


# du
def du(args: Namespace):
    rc = 0
    return rc


# cat
def cat(args: Namespace):
    rc = 0
    return rc


# zcat
def zcat(args: Namespace):
    rc = 0
    return rc


# gzip
def gzip(args: Namespace):
    rc = 0
    return rc


# gunzip
def gunzip(args: Namespace):
    rc = 0
    return rc


def main():
    parser = ArgumentParser(description='Python local filesystem access library')
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
    cp_parser.add_argument('source', nargs='+', default=['.'])
    cp_parser.add_argument('target')
    cp_parser.set_defaults(func=cp)

    mv_parser = subparsers.add_parser('mv', help='mv')
    mv_parser.add_argument('source', nargs='+', default=['.'])
    mv_parser.add_argument('target')
    mv_parser.set_defaults(func=mv)

    mkdir_parser = subparsers.add_parser('mkdir', help='mkdir')
    mkdir_parser.add_argument('-p', action='store_true')
    mkdir_parser.add_argument('-m', '--mode', default='755')
    mkdir_parser.add_argument('directory', nargs='+', default=['.'])
    mkdir_parser.set_defaults(func=mkdir)

    touch_parser = subparsers.add_parser('touch', help='touch')
    touch_parser.add_argument('-m', '--mode', default='644')
    touch_parser.add_argument('file', nargs='+', default=['.'])
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
    chmod_parser.add_argument('-R', action='store_true')
    chmod_parser.add_argument('mode')
    chmod_parser.add_argument('file', nargs='+', default=['.'])
    chmod_parser.set_defaults(func=chmod)

    chown_parser = subparsers.add_parser('chown', help='chown')
    chown_parser.add_argument('-R', action='store_true')
    chown_parser.add_argument('ownergroup')
    chown_parser.add_argument('file', nargs='+', default=['.'])
    chown_parser.set_defaults(func=chown)

    du_parser = subparsers.add_parser('du', help='du')
    du_parser.add_argument('-s', action='store_true')
    du_parser.add_argument('-h', action='store_true')
    du_parser.add_argument('file', nargs='+', default=['.'])
    du_parser.set_defaults(func=du)

    cat_parser = subparsers.add_parser('cat', help='cat')
    cat_parser.add_argument('file', nargs='+', default=['.'])
    cat_parser.set_defaults(func=cat)

    zcat_parser = subparsers.add_parser('zcat', help='zcat')
    zcat_parser.add_argument('file', nargs='+', default=['.'])
    zcat_parser.set_defaults(func=zcat)

    gzip_parser = subparsers.add_parser('gzip', help='gzip')
    gzip_parser.add_argument('file', nargs='+', default=['.'])
    gzip_parser.set_defaults(func=gzip)

    gunzip_parser = subparsers.add_parser('gunzip', help='gunzip')
    gunzip_parser.add_argument('file', nargs='+', default=['.'])
    gunzip_parser.set_defaults(func=gunzip)

    args = parser.parse_args()

    try:
        ret = args.func(args)
        exit(ret)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
