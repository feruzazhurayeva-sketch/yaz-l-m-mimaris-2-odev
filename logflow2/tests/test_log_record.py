import dataclasses
import unittest
from datetime import datetime, timezone

from logflow.log_record import LogRecord


def make(**kw):
    base = dict(timestamp=datetime(2026, 9, 29, tzinfo=timezone.utc), client_ip="1.2.3.4",
                method="GET", path="/", status=200, bytes=10, user_agent="ua", raw="x")
    base.update(kw)
    return LogRecord(**base)


class LogRecordTests(unittest.TestCase):
    def test_fields_cannot_be_reassigned(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            make().status = 500

    def test_attributes_is_read_only(self):
        with self.assertRaises(TypeError):
            make(attributes={"a": "1"}).attributes["b"] = "2"

    def test_attributes_copied_from_caller(self):
        src = {"a": "1"}
        r = make(attributes=src)
        src["a"] = "degisti"
        self.assertEqual(r.attributes["a"], "1")

    def test_attributes_default_is_empty(self):
        self.assertEqual(dict(make().attributes), {})

    def test_equality_by_value(self):
        self.assertEqual(make(), make())
        self.assertNotEqual(make(), make(status=404))


if __name__ == "__main__":
    unittest.main()
