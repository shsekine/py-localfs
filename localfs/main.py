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
    multi = len(args.file) > 0
    for af in args.file:
        paths = func.ls(af, opt)
        if args.l:
            dsps = func.format_long(paths)
        else:
            dsps = func.format_short(paths)
        if multi:
            print('{}:'.format(af))
            for d in dsps:
                print(d)
            print('')
        else:
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

    args = parser.parse_args()
    print(args)

    try:
        ret = args.func(args)
        exit(ret)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
