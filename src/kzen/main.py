"""Ví dụ gọi ForceAlign. Chạy: python -m kzen.main (cwd = repo, cần `sample.wav`)."""
from __future__ import annotations

from .utils import force_align


def main() -> None:
    words = force_align("sample.wav", "hello world")
    print(words)


if __name__ == "__main__":
    main()
