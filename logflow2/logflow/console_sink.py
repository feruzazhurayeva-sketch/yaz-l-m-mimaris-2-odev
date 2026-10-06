from .log_record import LogRecord
from .sink import Sink


def format_record(r: LogRecord) -> str:
    """Kaydi okunabilir TEK satira cevirir."""
    return (f"{r.timestamp.isoformat(sep=' ')} {r.client_ip} "
            f"{r.method} {r.path} -> {r.status} ({r.bytes} B) ua=\"{r.user_agent}\"")


class ConsoleSink(Sink[LogRecord]):
    """Her LogRecord'u konsola tek satir olarak yazar."""

    def consume(self, item: LogRecord) -> None:
        print(format_record(item))
