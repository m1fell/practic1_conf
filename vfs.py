from pathlib import Path


class VirtualFileSystem:
    """Дерево файлов и каталогов, которое хранится в памяти."""

    def __init__(self, source_path):
        self.source_path = Path(source_path).expanduser()
        self.root = {"type": "dir", "children": {}}
        self.current_path = "/"
        self.load()

    def load(self):
        if not self.source_path.exists():
            raise FileNotFoundError(
                f"директория VFS не найдена: {self.source_path}"
            )
        if not self.source_path.is_dir():
            raise ValueError(f"путь VFS не является директорией: {self.source_path}")

        self.root = self._load_directory(self.source_path)
        self.current_path = "/"

    def _load_directory(self, directory_path):
        node = {"type": "dir", "children": {}}
        for item in sorted(directory_path.iterdir(), key=lambda path: path.name.lower()):
            if item.is_symlink():
                # Символические ссылки не загружаем, чтобы не выходить за пределы VFS.
                continue
            if item.is_dir():
                node["children"][item.name] = self._load_directory(item)
            elif item.is_file():
                node["children"][item.name] = {
                    "type": "file",
                    "content": item.read_text(encoding="utf-8", errors="replace"),
                }
        return node

    def _normalize_path(self, path):
        if not path:
            return self.current_path

        if path.startswith("/"):
            parts = []
        else:
            parts = [part for part in self.current_path.split("/") if part]

        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)

        return "/" + "/".join(parts)

    def _get_node(self, path):
        normalized_path = self._normalize_path(path)
        node = self.root
        if normalized_path == "/":
            return node

        for part in normalized_path.strip("/").split("/"):
            if node["type"] != "dir" or part not in node["children"]:
                return None
            node = node["children"][part]
        return node

    def list_directory(self, path="."):
        node = self._get_node(path)
        if node is None:
            raise FileNotFoundError(f"путь не найден: {path}")
        if node["type"] != "dir":
            raise NotADirectoryError(f"это не каталог: {path}")
        return sorted(node["children"].keys())

    def change_directory(self, path):
        node = self._get_node(path)
        if node is None:
            raise FileNotFoundError(f"каталог не найден: {path}")
        if node["type"] != "dir":
            raise NotADirectoryError(f"это не каталог: {path}")
        self.current_path = self._normalize_path(path)

    def read_file(self, path):
        node = self._get_node(path)
        if node is None:
            raise FileNotFoundError(f"файл не найден: {path}")
        if node["type"] != "file":
            raise IsADirectoryError(f"это каталог, а не файл: {path}")
        return node["content"]

    def create_file(self, path):
        normalized_path = self._normalize_path(path)
        if normalized_path == "/":
            raise IsADirectoryError("нельзя создать файл вместо корневого каталога")

        parent_path, file_name = normalized_path.rsplit("/", 1)
        parent_path = parent_path or "/"
        if not file_name:
            raise ValueError("не указано имя файла")

        parent = self._get_node(parent_path)
        if parent is None:
            raise FileNotFoundError(f"каталог не найден: {parent_path}")
        if parent["type"] != "dir":
            raise NotADirectoryError(f"это не каталог: {parent_path}")
        if file_name in parent["children"]:
            if parent["children"][file_name]["type"] == "dir":
                raise IsADirectoryError(f"это каталог: {path}")
            return

        parent["children"][file_name] = {"type": "file", "content": ""}

    def reset(self):
        """Сбрасывает VFS в пустое состояние и очищает её физическую директорию."""
        if not self.source_path.exists():
            self.source_path.mkdir(parents=True, exist_ok=True)
        if not self.source_path.is_dir():
            raise NotADirectoryError(f"путь VFS не является директорией: {self.source_path}")

        for item in self.source_path.iterdir():
            if item.is_dir() and not item.is_symlink():
                self._remove_directory(item)
            elif item.is_file() or item.is_symlink():
                item.unlink()

        self.root = {"type": "dir", "children": {}}
        self.current_path = "/"

    def _remove_directory(self, directory_path):
        for item in directory_path.iterdir():
            if item.is_dir() and not item.is_symlink():
                self._remove_directory(item)
            else:
                item.unlink()
        directory_path.rmdir()
