# -*- conding:utf-8 -*-

import pytest
from argparse import Namespace
from localfs import main


def test_to_opt():
    args = Namespace(a=True, b=True, c=True, d=False)
    assert main.to_opt(args, 'a') == '-a'
    assert main.to_opt(args, 'd') == '-'
    assert main.to_opt(args, 'e') == '-'
    assert main.to_opt(args, 'abcd') == '-abc'
