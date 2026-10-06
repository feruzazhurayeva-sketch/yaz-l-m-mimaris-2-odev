from .emitter import Emitter
from .source import Source
from .stage import StageException


class FileLineSource(Source[str]):
    """Dosyayi okur, her satir icin bir str yayar."""

    def __init__(self, path: str) -> None:
        self._path = path

    def produce(self, out: Emitter[str]) -> None:
        try:
            with open(self._path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    out.emit(line.rstrip("\r\n"))
        except OSError as e:
            raise StageException(f"Dosya acilamadi: {self._path} ({e.strerror})") from e
