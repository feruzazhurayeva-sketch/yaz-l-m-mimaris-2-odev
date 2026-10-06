import contextlib
import io
import unittest
from datetime import datetime, timedelta, timezone

from logflow.console_sink import ConsoleSink, format_record
from logflow.log_record import LogRecord

REC = LogRecord(datetime(2026, 9, 29, 10, 0, 0, tzinfo=timezone(timedelta(hours=3))),
                "85.105.14.9", "GET", "/products?id=42", 200, 16169, "Mozilla/5.0", {}, "raw")


class ConsoleSinkTests(unittest.TestCase):
    def test_format_is_single_readable_line(self):
        text = format_record(REC)
        self.assertEqual(text, '2026-09-29 10:00:00+03:00 85.105.14.9 GET /products?id=42 '
                               '-> 200 (16169 B) ua="Mozilla/5.0"')
        self.assertNotIn("\n", text)

    def test_consume_prints_one_line(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ConsoleSink().consume(REC)
        self.assertEqual(buf.getvalue(), format_record(REC) + "\n")


if __name__ == "__main__":
    unittest.main()
