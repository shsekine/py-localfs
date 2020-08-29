# -*- conding:utf-8 -*-

import json
from setuptools import setup


with open('meta.json', mode='r', encoding='utf-8') as f:
    meta = json.load(f)


setup(
    name=meta['name'],
    description=meta['description'],
    version=meta['version'],
    author=meta['author'],
    author_email=meta['author_email'],
    url=meta['url'],
    license='MIT',
    namespace_packages=[],
    packages=[
        'localfs'
    ],
    package_dir={
        'localfs': 'localfs'
    },
    package_data={
        '': ['*.ini']
    },
    scripts=[],
    install_requires=[],
    tests_require=[],
    entry_points={}
)
