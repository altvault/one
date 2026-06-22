import argparse


def register(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser("pipeline")
    parser.add_argument("name")
    parser.add_argument("--app-version")
    return parser


def run(args: argparse.Namespace):
    print(args.name)
    print(args.app_version)
    pass
