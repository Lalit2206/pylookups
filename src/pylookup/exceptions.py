class PyLookupError(Exception):
    """Base class for all pylookup errors."""


class NotFoundError(PyLookupError):
    """Raised when a lookup value has no match."""

    def __init__(self, value):
        super().__init__(f"value not found: {value!r}")
        self.value = value


class InvalidIndexError(PyLookupError):
    """Raised when a row/column position is out of range."""


class UnsupportedFormatError(PyLookupError):
    """Raised when a file's format cannot be read."""


class SheetNotFoundError(PyLookupError):
    """Raised when a workbook has no sheet by the requested name or number."""
