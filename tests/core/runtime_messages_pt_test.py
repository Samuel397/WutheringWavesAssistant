import ast
import re
from pathlib import Path

from src.core.task import TaskStatus


REPO_ROOT = Path(__file__).resolve().parents[2]
HAN_RE = re.compile(r"[\u3400-\u9fff]")
LOGGER_METHODS = {"info", "warning", "error", "exception", "critical"}
NOTIFICATION_METHODS = {"show_windows_notification"}
# Tuples are (relative path, line number, literal). Keep this empty unless a
# Chinese literal is proven to be an internal protocol value rather than text
# shown to the user.
ALLOWED_HAN_RUNTIME_MESSAGES: set[tuple[str, int, str]] = set()
FORBIDDEN_ENGLISH_RUNTIME_FRAGMENTS = {
    "all update urls failed",
    "challenge complete",
    "feature match failed",
    "free and open-source",
    "page not found",
    "task is not active",
    "text not found",
    "unexpected root state",
    "using game language",
    "using game path",
}


def _runtime_source_files() -> list[Path]:
    return sorted((REPO_ROOT / "src").rglob("*.py"))


def _is_user_visible_message_call(node: ast.Call) -> bool:
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr in NOTIFICATION_METHODS:
        return True
    return (
        func.attr in LOGGER_METHODS
        and isinstance(func.value, ast.Name)
        and func.value.id == "logger"
    )


def _literal_segments(node: ast.AST):
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            yield child.value


def test_runtime_messages_have_no_unreviewed_chinese_literals():
    found: set[tuple[str, int, str]] = set()
    for path in _runtime_source_files():
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_user_visible_message_call(node):
                arguments = [*node.args, *(keyword.value for keyword in node.keywords)]
            elif isinstance(node, ast.Raise) and node.exc is not None:
                arguments = [node.exc]
            else:
                continue
            for argument in arguments:
                for literal in _literal_segments(argument):
                    if HAN_RE.search(literal):
                        found.add((relative_path, node.lineno, literal))

    assert found == ALLOWED_HAN_RUNTIME_MESSAGES


def test_task_status_text_is_in_portuguese():
    for status in TaskStatus:
        assert not HAN_RE.search(status.display_name)
        assert not HAN_RE.search(status.description)


def test_known_english_runtime_messages_do_not_regress():
    found: set[tuple[str, int, str]] = set()
    for path in _runtime_source_files():
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_user_visible_message_call(node):
                arguments = [*node.args, *(keyword.value for keyword in node.keywords)]
            elif isinstance(node, ast.Raise) and node.exc is not None:
                arguments = [node.exc]
            else:
                continue
            for argument in arguments:
                for literal in _literal_segments(argument):
                    lowered = literal.casefold()
                    for fragment in FORBIDDEN_ENGLISH_RUNTIME_FRAGMENTS:
                        if fragment in lowered:
                            found.add((relative_path, node.lineno, fragment))

    assert not found
