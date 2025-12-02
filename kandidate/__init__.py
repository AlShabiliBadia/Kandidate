"""Top-level package for the modern Kandidate engine."""

from importlib import metadata

try:
    __version__ = metadata.version("kandidate")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"

__all__ = ["__version__"]
