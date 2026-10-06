import unittest
from datetime import datetime, timedelta, timezone

from logflow.parser_stage import ParserStage
from tests.collecting_emitter import CollectingEmitter

GOOD = ('85.105.14.9 - - [29/Sep/2026:10:00:00 +0300] '
        '"GET / HTTP/1.1" 200 16169 "-" "Mozilla/5.0"')


class ParserStageTests(unittest.TestCase):
    """Dosya sistemine dokunmaz: stage'e dizgi verir, ciktiyi CollectingEmitter'dan okur."""

    def setUp(self):
        self.stage = ParserStage()
        self.out = CollectingEmitter()

    def parse(self, line):
        self.stage.process(line, self.out)
        return self.out.items

    # --- Odevin istedigi 8 durum -------------------------------------------

    def test_1_valid_line(self):
        (r,) = self.parse(GOOD)
        self.assertEqual(r.client_ip, "85.105.14.9")
        self.assertEqual(r.method, "GET")
        self.assertEqual(r.path, "/")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.bytes, 16169)
        self.assertEqual(r.user_agent, "Mozilla/5.0")
        self.assertEqual(r.timestamp,
                         datetime(2026, 9, 29, 10, 0, 0, tzinfo=timezone(timedelta(hours=3))))
        self.assertEqual(dict(r.attributes), {})
        self.assertEqual(r.raw, GOOD)
        self.assertEqual((self.stage.parsed_count, self.stage.skipped_count), (1, 0))

    def test_2_missing_field(self):
        # durum ve bayt alanlari yok
        self.assertEqual(self.parse('1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET / HTTP/1.1"'), [])
        self.assertEqual(self.stage.skipped_count, 1)

    def test_3_bad_timestamp(self):
        for ts in ("29/Foo/2026:10:00:00 +0300",     # bilinmeyen ay
                   "32/Sep/2026:10:00:00 +0300",     # imkansiz gun
                   "29/Sep/2026:25:00:00 +0300",     # imkansiz saat
                   "dun aksam"):
            with self.subTest(ts=ts):
                line = f'1.2.3.4 - - [{ts}] "GET / HTTP/1.1" 200 10 "-" "ua"'
                self.assertEqual(self.parse(line), [])
        self.assertEqual(self.stage.skipped_count, 4)

    def test_4_bad_status_code(self):
        for status in ("abc", "20", "2000", "999", "000"):
            with self.subTest(status=status):
                line = f'1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET / HTTP/1.1" {status} 10 "-" "ua"'
                self.assertEqual(self.parse(line), [])
        self.assertEqual(self.stage.skipped_count, 5)

    def test_5_empty_line(self):
        for line in ("", "   ", "\t"):
            self.parse(line)
        self.assertEqual(self.out.items, [])
        self.assertEqual(self.stage.skipped_count, 3)

    def test_6_extra_whitespace(self):
        line = ('   85.105.14.9  -   -  [29/Sep/2026:10:00:00 +0300]   '
                '"GET / HTTP/1.1"   200   16169   "-"   "Mozilla/5.0"   ')
        (r,) = self.parse(line)
        self.assertEqual((r.client_ip, r.status, r.bytes, r.user_agent),
                         ("85.105.14.9", 200, 16169, "Mozilla/5.0"))

    def test_7_quoted_user_agent_with_spaces(self):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        line = f'1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET / HTTP/1.1" 200 10 "-" "{ua}"'
        (r,) = self.parse(line)
        self.assertEqual(r.user_agent, ua)

    def test_8_query_string(self):
        line = '1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET /products?id=42&x=a%20b HTTP/1.1" 200 10 "-" "ua"'
        (r,) = self.parse(line)
        self.assertEqual(r.path, "/products?id=42&x=a%20b")
        self.assertEqual(r.method, "GET")

    # --- Ek durumlar ---------------------------------------------------------

    def test_dash_bytes_is_zero(self):
        (r,) = self.parse('1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET / HTTP/1.1" 304 - "-" "ua"')
        self.assertEqual(r.bytes, 0)

    def test_plain_clf_without_agent(self):
        (r,) = self.parse('1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET / HTTP/1.1" 200 10')
        self.assertEqual(r.user_agent, "")

    def test_negative_timezone_offset(self):
        (r,) = self.parse('1.2.3.4 - - [29/Sep/2026:10:00:00 -0530] "GET / HTTP/1.1" 200 10 "-" "ua"')
        self.assertEqual(r.timestamp.utcoffset(), -timedelta(hours=5, minutes=30))

    def test_bad_request_line_is_skipped(self):
        self.assertEqual(self.parse('1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "-" 400 0 "-" "-"'), [])

    def test_non_numeric_bytes_is_skipped(self):
        self.assertEqual(self.parse('1.2.3.4 - - [29/Sep/2026:10:00:00 +0300] "GET / HTTP/1.1" 200 x "-" "ua"'), [])

    def test_mixed_lines_are_counted(self):
        for line in (GOOD, "cop", GOOD, "", GOOD):
            self.stage.process(line, self.out)
        self.assertEqual(len(self.out.items), 3)
        self.assertEqual((self.stage.parsed_count, self.stage.skipped_count), (3, 2))

    def test_open_resets_counters(self):
        self.parse(GOOD)
        self.parse("cop")
        self.stage.open()
        self.assertEqual((self.stage.parsed_count, self.stage.skipped_count), (0, 0))


if __name__ == "__main__":
    unittest.main()
