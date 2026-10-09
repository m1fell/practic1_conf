import os
from pathlib import Path

from emulator.parser import parse_command


class Shell:
    def __init__(self, vfs):
        self.vfs = vfs
        self.should_exit = False
        self.user_name = os.environ.get("USER") or os.environ.get("USERNAME") or "user"

    def prompt(self):
        vfs_name = self.vfs.source_path.name or "vfs"
        return f"{vfs_name}:{self.vfs.current_path} $ "

    def run_interactive(self):
        while not self.should_exit:
            try:
                command_line = input(self.prompt())
            except EOFError:
                print()
                break
            self.execute_line(command_line)

    def run_script(self, script_path):
        path = Path(script_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"стартовый скрипт не найден: {path}")
        if not path.is_file():
            raise ValueError(f"путь стартового скрипта не является файлом: {path}")

        with path.open("r", encoding="utf-8") as script_file:
            for raw_line in script_file:
                command_line = raw_line.rstrip("\n")
                if not command_line.strip() or command_line.lstrip().startswith("#"):
                    continue
                print(self.prompt() + command_line)
                self.execute_line(command_line, from_script=True)
                if self.should_exit:
                    break

    def execute_line(self, command_line, from_script=False):
        try:
            command, arguments = parse_command(command_line)
            if command is None:
                return
            self.execute_command(command, arguments)
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
            if from_script:
                # Ошибочная строка показывается, сообщается об ошибке, скрипт продолжается.
                return

    def execute_command(self, command, arguments):
        if command == "exit":
            if arguments:
                print("Использование: exit")
                return
            self.should_exit = True
        elif command == "ls":
            self.command_ls(arguments)
        elif command == "cd":
            self.command_cd(arguments)
        elif command == "whoami":
            self.command_whoami(arguments)
        elif command == "tac":
            self.command_tac(arguments)
        elif command == "echo":
            self.command_echo(arguments)
        elif command == "touch":
            self.command_touch(arguments)
        elif command == "vfs-init":
            self.command_vfs_init(arguments)
        else:
            print(f"Ошибка: неизвестная команда: {command}")

    def command_ls(self, arguments):
        if len(arguments) > 1:
            print("Использование: ls [путь]")
            return
        path = arguments[0] if arguments else "."
        for name in self.vfs.list_directory(path):
            print(name)

    def command_cd(self, arguments):
        if len(arguments) > 1:
            print("Использование: cd [каталог]")
            return
        path = arguments[0] if arguments else "/"
        self.vfs.change_directory(path)

    def command_whoami(self, arguments):
        if arguments:
            print("Использование: whoami")
            return
        print(self.user_name)

    def command_tac(self, arguments):
        if len(arguments) != 1:
            print("Использование: tac <файл>")
            return
        content = self.vfs.read_file(arguments[0])
        lines = content.splitlines()
        for line in reversed(lines):
            print(line)

    def command_echo(self, arguments):
        print(" ".join(arguments))

    def command_touch(self, arguments):
        if not arguments:
            print("Использование: touch <файл> [файл ...]")
            return
        for path in arguments:
            self.vfs.create_file(path)

    def command_vfs_init(self, arguments):
        if arguments:
            print("Использование: vfs-init")
            return
        self.vfs.reset()
        print("VFS сброшена. Физическая директория очищена.")
