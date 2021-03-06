import argparse
import os
import shlex
import subprocess

from zeynep.utils.envparse import env

_compose_files = {
    "production": "docker/docker-compose.prod.yml",
    "development": "docker/docker-compose.yml",
}
_django = "docker exec -it web python manage.py"


def assertive(text):
    return "\033[95m\033[1m" + text + "\033[0m"


def run_command(command, environment):
    message = assertive("(%s) Running: %s\n" % (environment, command))
    print(message)
    command = shlex.split(command)

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print(assertive("Operation cancelled."))


def main(parser, environment):  # noqa
    args = parser.parse_args()
    action = args.action

    if (action is None) and (not args.command):
        parser.print_help()
        return 1

    filename = _compose_files[environment]
    compose_cmd = "docker-compose -p zeynep -f %s" % filename
    command_map = {
        "command": f"{_django} {args.command}",
        "shell": f"{_django} shell",
        "test": f"{_django} test --settings=zeynep.settings.test"
        " --parallel 4 --shuffle --timing --keepdb",
        "console": "docker exec -it web sh",
    }

    if action is None:
        action = "command"

    if action == "star":
        if environment != "development":
            return "This command is only available in development environment."

        run_command("%s start" % compose_cmd, environment)
        run_command("%s logs -f --tail 100 web" % compose_cmd, environment)
        run_command("%s stop" % compose_cmd, environment)
        return 0

    if action == "logs":
        os.system("%s logs -f --tail 100" % compose_cmd)
        return 0

    default = "%s %s" % (compose_cmd, action)
    cmd = command_map.get(action, default)

    if args.detached:
        cmd += " -d"

    run_command(cmd, environment)
    return 0


def get_environment():
    environment = env.str("ZEYNEP_ENV", None)

    if environment is None:
        print(
            assertive("No environment specified, defaulting to development.")
        )
        return "development"

    if environment not in ("production", "development"):
        raise SystemExit(
            "Received invalid environment type, choices are: %s."
            % "development, production"
        )

    return environment


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs and manages docker containers."
    )
    parser.add_argument(
        "action",
        nargs="?",
        type=str,
        help="Specify an action.",
        choices=[
            "up",
            "down",
            "build",
            "restart",
            "star",
            "start",
            "stop",
            "shell",
            "console",
            "test",
            "logs",
        ],
    )
    parser.add_argument(
        "-d",
        "--detached",
        action="store_true",
        help="Run in detached mode.",
    )
    parser.add_argument(
        "-c",
        "--command",
        help="Run a Django command via 'manage.py'.",
    )
    raise SystemExit(main(parser, get_environment()))
