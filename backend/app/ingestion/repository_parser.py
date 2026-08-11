from dataclasses import dataclass
from pathlib import Path

from app.ingestion.file_loader import (
    is_supported_file,
    should_ignore,
    load_text_file,
)


@dataclass
class RepositoryFile:
    path: str
    language: str
    content: str


EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".swift": "swift",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".txt": "text",
}


def detect_language(path: Path) -> str:
    return EXTENSION_TO_LANGUAGE.get(
        path.suffix.lower(),
        "unknown",
    )


def parse_repository(repository_path: Path) -> list[RepositoryFile]:
    """Parse supported text files from a repository."""

    files = []

    for path in repository_path.rglob("*"):
        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        if not is_supported_file(path):
            continue

        try:
            content = load_text_file(path)
        except OSError:
            continue

        relative_path = path.relative_to(repository_path)

        files.append(
            RepositoryFile(
                path=str(relative_path),
                language=detect_language(path),
                content=content,
            )
        )

    return files
