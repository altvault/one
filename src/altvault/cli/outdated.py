import argparse


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("outdated")
    return parser


def run(args: argparse.Namespace):
    pass
