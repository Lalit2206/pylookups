# Roadmap

pylookups releases follow a simple sequential series: **0.1.1 → 0.1.2 →
0.1.3 → ...** Each release is small and focused.

The current release is always the one on
[PyPI](https://pypi.org/project/pylookups/); the
[Changelog](changelog.md) lists every version.

## 0.1.2 — fixes

**Fixes and corrections — no new functions.**

- `xlookup(..., if_not_found=None)` now returns `None` instead of raising.
  The default is an internal sentinel, so every value — `None`, `0`, `""` —
  is returned as given, and only omitting the argument raises
  `NotFoundError`.
- `filter(..., if_empty=None)` likewise returns `None` on an empty result;
  omitting `if_empty` still returns `[]`.
- `sort()` now raises `InvalidIndexError` when `by` is out of range for any
  row (ragged tables included), instead of a raw `IndexError` from the sort
  key. This matches `vlookup`/`hlookup`/`index`.

## Have a suggestion?

Open an issue on
[GitHub](https://github.com/Lalit2206/pylookups/issues) — feature
requests are welcome.
