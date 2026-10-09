import os
import shlex


def parse_command(command_line):
    """Раскрывает переменные окружения и разбирает строку на команду и аргументы."""
    expanded_line = os.path.expandvars(command_line)
    try:
        parts = shlex.split(expanded_line)
    except ValueError as error:
        raise ValueError(f"Не удалось разобрать команду: {error}") from error

    if not parts:
        return None, []

    return parts[0], parts[1:]
