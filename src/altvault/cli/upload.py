import argparse


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("upload")
    parser.add_argument("file_path")
    return parser


def run(args: argparse.Namespace):
    pass
