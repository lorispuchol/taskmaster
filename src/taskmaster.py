import sys
import yaml
from server.server import start_server
from shared.global_variables import programs, config


def parse_config(config_file) -> dict:
    with open(config_file, "r") as f:
        global config
        config = yaml.safe_load(f)
    print("Config file parsed successfully")
    return config


def check_config(conf: dict):

    required_fields = ["programs"]

    if not conf:
        raise Exception("Config file is empty")
    if not isinstance(conf, dict):
        raise Exception("Config file must start by an object")
    for field in required_fields:
        if field not in conf:
            raise Exception(f"Config file is missing required field: {field}")
    if not isinstance(conf["programs"], dict):
        raise Exception("Config file 'programs' field must be an object")
    return True


def taskmaster():
    try:
        config = parse_config(sys.argv[1])
        check_config(config)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    start_server()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <config_file>")
        sys.exit(1)
    taskmaster()