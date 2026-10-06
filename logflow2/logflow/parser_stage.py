import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from .emitter import Emitter
from .log_record import LogRecord
from .stage import Stage

# Tirnakli alanlarin govdesi: icinde bosluk ve \" olabilir.
# CLF: host ident authuser [tarih] "istek" durum bayt
# Combined bicimi: ardindan "referer" "user-agent" (bu kisim istege bagli).
# Alanlar arasi \s+ : fazladan bosluk hosgorulur.
_LINE = re.compile(
    r"^(?P<ip>\S+)\s+\S+\s+\S+\s+"
    r"\[(?P<time>[^\]]+)\]\s+"
    r'"(?P<request>(?:[^"\\]|\\.)*)"\s+'
    r"(?P<status>\S+)\s+(?P<bytes>\S+)"
    r'(?:\s+"(?P<referer>(?:[^"\\]|\\.)*)"'
    r'\s+"(?P<agent>(?:[^"\\]|\\.)*)")?$'
)

_TIME = re.compile(
    r"^(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2}) ([+-])(\d{2})(\d{2})$"
)

# strptime("%b") yerel ayara baglidir; kendi tablomuz her makinede ayni calisir.
_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}


def _parse_time(text: str) -> Optional[datetime]:
    m = _TIME.match(text)
    if not m or m.group(2) not in _MONTHS:
        return None
    day, _, year, hh, mm, ss, sign, tzh, tzm = m.groups()
    offset = timedelta(hours=int(tzh), minutes=int(tzm))
    if sign == "-":
        offset = -offset
    try:
        return datetime(int(year), _MONTHS[m.group(2)], int(day),
                        int(hh), int(mm), int(ss), tzinfo=timezone(offset))
    except ValueError:      # 32/Sep, 25:00:00, +9999 gibi imkansiz degerler
        return None


def parse_line(line: str) -> Optional[LogRecord]:
    """Bir CLF satirini LogRecord'a cevirir; gecersizse None doner (istisna firlatmaz)."""
    text = line.strip()
    m = _LINE.match(text)
    if not m:
        return None

    timestamp = _parse_time(m.group("time"))
    if timestamp is None:
        return None

    status_text = m.group("status")
    if not (status_text.isascii() and status_text.isdigit() and len(status_text) == 3):
        return None
    status = int(status_text)
    if not 100 <= status <= 599:
        return None

    bytes_text = m.group("bytes")
    if bytes_text == "-":                   # CLF: icerik yok
        size = 0
    elif bytes_text.isascii() and bytes_text.isdigit():
        size = int(bytes_text)
    else:
        return None

    parts = m.group("request").split()      # "GET /path HTTP/1.1"
    if len(parts) < 2:
        return None

    return LogRecord(
        timestamp=timestamp,
        client_ip=m.group("ip"),
        method=parts[0],
        path=parts[1],
        status=status,
        bytes=size,
        user_agent=m.group("agent") or "",
        attributes={},                      # ayristirici bos birakir; sonraki asamalar doldurur
        raw=line,
    )


class ParserStage(Stage[str, LogRecord]):
    """str (ham satir) -> LogRecord.

    Hatali satirlar bu hafta YALNIZCA atlanir ve sayilir. Dogru ele alinmalari
    (hata kaydi, karantina, hata hatti) 5. haftada gelecek.
    """

    def __init__(self) -> None:
        self.parsed_count = 0
        self.skipped_count = 0

    def open(self) -> None:
        self.parsed_count = 0       # ayni nesne tekrar calistirilirsa sayaclar sifirlanir
        self.skipped_count = 0

    def process(self, item: str, out: Emitter[LogRecord]) -> None:
        record = parse_line(item)
        if record is None:
            self.skipped_count += 1
            return
        self.parsed_count += 1
        out.emit(record)
