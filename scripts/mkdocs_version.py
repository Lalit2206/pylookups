"""MkDocs hook: replace {{ version }} in any page with the real version.

The version is read from pyproject.toml at build time, so the docs can never
show a stale release number — bumping pyproject.toml is enough.

Registered under `hooks:` in mkdocs.yml. Uses no third-party packages, and
no tomllib, so it works on every Python version MkDocs itself supports.
"""
import pathlib
import re

PLACEHOLDER = "{{ version }}"
PYPROJECT = pathlib.Path(__file__).resolve().parent.parent / "pyproject.toml"


def _read_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    found = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not found:
        raise RuntimeError(f"no version = \"...\" line found in {PYPROJECT}")
    return found.group(1)


VERSION = _read_version()


def on_page_markdown(markdown: str, **kwargs) -> str:
    return markdown.replace(PLACEHOLDER, VERSION)
