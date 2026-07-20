import questionary
import argparse

from altvault.cli import outdated, pipeline, upload, dispatch, syncworkflow


def main():
    parser = argparse.ArgumentParser(prog="altvault")

    subparsers = parser.add_subparsers(dest="command")

    for module in (outdated, upload, pipeline, dispatch, syncworkflow):
        sub = module.register(subparsers)
        sub.set_defaults(func=module.run)

    args = parser.parse_args()

    if args.command is None:
        command = questionary.select(
            "Command",
            # choices=list(subparsers.choices),
            choices=[
                questionary.Choice(cmd, shortcut_key=cmd[0])
                for cmd in subparsers.choices
            ],
            use_shortcuts=True,
        ).ask()
        if command is None:
            raise ValueError("No command selected")
        args = parser.parse_args([command])

    args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
