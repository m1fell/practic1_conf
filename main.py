import argparse
import os
from pathlib import Path

import yaml

from emulator.shell import Shell
from emulator.vfs import VirtualFileSystem


DEFAULT_VFS_PATH = "vfs_examples/nested"
DEFAULT_SCRIPT_PATH = None
DEFAULT_CONFIG_PATH = None


def read_config(config_path):
    if not config_path:
        return {}

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")

    with path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    if not isinstance(config, dict):
        raise ValueError("Конфигурационный файл должен содержать YAML-словарь.")

    return config


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Эмулятор UNIX-подобной командной оболочки"
    )
    parser.add_argument("--vfs", help="Путь к директории-источнику VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    parser.add_argument("--config", help="Путь к YAML-конфигурации")
    return parser.parse_args()


def main():
    arguments = parse_arguments()

    try:
        config = read_config(arguments.config)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Ошибка конфигурации: {error}")
        return 1

    # По условию настройки из YAML имеют приоритет над аргументами командной строки.
    vfs_path = config.get("vfs_path", arguments.vfs or DEFAULT_VFS_PATH)
    script_path = config.get("script_path", arguments.script or DEFAULT_SCRIPT_PATH)

    print("Параметры запуска:")
    print(f"  VFS: {vfs_path}")
    print(f"  Стартовый скрипт: {script_path if script_path else '(не задан)'}")
    print(f"  Конфигурация: {arguments.config if arguments.config else '(не задана)'}")

    try:
        vfs = VirtualFileSystem(vfs_path)
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки VFS: {error}")
        return 1

    shell = Shell(vfs)

    if script_path:
        try:
            shell.run_script(script_path)
        except OSError as error:
            print(f"Ошибка стартового скрипта: {error}")
            return 1

    if not shell.should_exit:
        shell.run_interactive()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
