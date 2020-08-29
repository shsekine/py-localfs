# -*- conding:utf-8 -*-

import argparse
from localfs import func


# ls
def ls(args: object):
    rc = 0
    files = []
    if args.opt is not None:
        if args.opt.startswith('-'):
           opt = args.opt
        else:
           opt = ''


    for tp in args.file:
        paths = func.ls(tp)
        for p in paths:
            print(p)
    return rc


def main():
    parser = argparse.ArgumentParser(description='Python local filesystem access library')
    subparsers = parser.add_subparsers()
    subparsers.required = True

    ls_parser = subparsers.add_parser('ls', help='ls')
    ls_parser.add_argument('opt', nargs='?')
    ls_parser.add_argument('file', nargs='*')
    ls_parser.set_defaults(func=ls)

    args = parser.parse_args()

    try:
        ret = args.func(args)
        exit(ret)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
