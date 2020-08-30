# -*- conding:utf-8 -*-

import sys
from localfs import func
from typing import List, Dict, Any


MAIN_USAGE = 'pylocalfs <subcmd> [subopt] [subarg ...]'
SUB_USAGE = {
    'ls': 'pylocalfs -ls [-@altr%] [file ...]'
}


# parse_argv
def parse_argv(argv: List[str]) -> Dict[str, Any]:
    if len(argv) <= 2:
        return None
    script = argv.pop(0)
    subcmd = argv.pop(0).replace('-', '')
    if subcmd not in SUB_USAGE.keys():
        return None
    opt = []
    args = []
    for arg in argv:
        if arg.startswith('-'):
            opt.append(arg.replace('-', ''))
        else:
            args.append(arg)
    return {
        'script': script,
        'subcmd': subcmd,
        'opt': opt,
        'args': args
    }


# ls
def ls(args: List[str], opt: List[str]):
    rc = 0
    optprm = '-{}'.format(''.join(opt))
    for tgt in args:
        paths = func.ls(tgt, optprm)
        for p in paths:
            print(p)
    return rc


def main():
    args = parse_argv(sys.argv)
    if args is None:
        print(MAIN_USAGE, file=sys.stderr)
        sys.exit(1)
    rc = 0
    if args['subcmd'] == 'ls':
        rc = ls(args['args'], args['opt'])
    sys.exit(rc)


if __name__ == "__main__":
    main()
