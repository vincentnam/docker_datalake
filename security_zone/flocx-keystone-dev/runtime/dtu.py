#!/usr/bin/python

import argparse
import jinja2
import os
import sys


def kvpair(v):
    return v.split('=')


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('-s', '--set', action='append', type=kvpair, default=[])
    p.add_argument('-o', '--output')
    p.add_argument('template')

    return p.parse_args()


def main():
    args = parse_args()

    vars = dict(args.set)

    with open(args.template) as fd:
        template = jinja2.Template(fd.read())

    with (open(args.output, 'w') if args.output else sys.stdout) as fd:
        fd.write(template.render(
            environ=os.environ,
            **vars))


if __name__ == '__main__':
    main()
