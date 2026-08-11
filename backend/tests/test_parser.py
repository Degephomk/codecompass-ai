from pathlib import Path

from app.ingestion.repository_parser import parse_repository


def test_parse_repository(tmp_path: Path):
    repository = tmp_path / "test_repo"
    repository.mkdir()

    python_file = repository / "main.py"
    python_file.write_text(
        'print("Hello CodeCompass")',
        encoding="utf-8",
    )

    readme_file = repository / "README.md"
    readme_file.write_text(
        "# Test Repository",
        encoding="utf-8",
    )

    unsupported_file = repository / "image.xyz"
    unsupported_file.write_text(
        "should be ignored",
        encoding="utf-8",
    )

    files = parse_repository(repository)

    assert len(files) == 2

    paths = {file.path for file in files}

    assert "main.py" in paths
    assert "README.md" in paths
    assert "image.xyz" not in paths
