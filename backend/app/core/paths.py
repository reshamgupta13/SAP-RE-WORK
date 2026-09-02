"""Resolve repository paths for local and deployed environments."""

from __future__ import annotations

from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def resolve_fixtures_dir(configured: str) -> Path:
    """Resolve fixtures directory relative to backend root or repo root."""
    path = Path(configured)
    if path.is_absolute():
        return path

    from_backend = (_BACKEND_ROOT / path).resolve()
    if from_backend.exists():
        return from_backend

    repo_fixtures = (_BACKEND_ROOT.parent / "fixtures").resolve()
    if repo_fixtures.exists():
        return repo_fixtures

    return from_backend
