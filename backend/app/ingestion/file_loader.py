from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".kts",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".txt",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "coverage",
}


def is_supported_file(path: Path) -> bool:
    """Return True if the file type is supported."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def should_ignore(path: Path) -> bool:
    """Return True if any path component belongs to an ignored directory."""
    return any(
        part in IGNORED_DIRECTORIES
        for part in path.parts
    )


def load_text_file(path: Path) -> str:
    """Read a source file as UTF-8 text."""
    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )
