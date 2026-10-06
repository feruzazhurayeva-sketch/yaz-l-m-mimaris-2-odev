import contextlib
import io
import os
import tempfile
import unittest

from logflow.emitter import Emitter
from logflow.file_line_source import FileLineSource
from logflow.pipeline import Pipeline
from logflow.sink import Sink
from logflow.source import Source
from logflow.stage import Stage, StageException
import main as logflow_main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "data", "access-small.log")


class ListSource(Source[str]):
    def __init__(self, items):
        self.items = items

    def produce(self, out: Emitter[str]) -> None:
        for i in self.items:
            out.emit(i)


class CollectSink(Sink[str]):
    def __init__(self):
        self.items = []

    def consume(self, item: str) -> None:
        self.items.append(item)


class Filter(Stage[str, str]):          # 0 veya 1 cikti
    def process(self, item, out):
        if "404" in item:
            out.emit(item)


class Splitter(Stage[str, str]):        # N cikti
    def process(self, item, out):
        for part in item.split():
            out.emit(part)


class Recorder(Stage[str, str]):
    def __init__(self, name, log, fail=False):
        self.name, self.log, self.fail = name, log, fail

    def open(self):
        self.log.append(f"open {self.name}")

    def close(self):
        self.log.append(f"close {self.name}")

    def process(self, item, out):
        if self.fail:
            raise StageException("bozuk")
        out.emit(item)


class PipelineTests(unittest.TestCase):
    def run_pipe(self, items, *stages):
        sink = CollectSink()
        p = Pipeline(ListSource(items), sink)
        for s in stages:
            p.add_stage(s)
        p.run()
        return sink.items

    def test_passthrough_without_stages(self):
        self.assertEqual(self.run_pipe(["a", "b"]), ["a", "b"])

    def test_filter_emits_zero_or_one(self):
        self.assertEqual(self.run_pipe(["x 200", "y 404"], Filter()), ["y 404"])

    def test_splitter_emits_many(self):
        self.assertEqual(self.run_pipe(["a b c"], Splitter()), ["a", "b", "c"])

    def test_stage_order(self):
        self.assertEqual(self.run_pipe(["a 404 b"], Filter(), Splitter()), ["a", "404", "b"])

    def test_lifecycle_open_in_order_close_reversed(self):
        log = []
        self.run_pipe(["a"], Recorder("1", log), Recorder("2", log))
        self.assertEqual(log, ["open 1", "open 2", "close 2", "close 1"])

    def test_close_called_on_error(self):
        log = []
        with self.assertRaises(StageException):
            self.run_pipe(["a"], Recorder("1", log, fail=True))
        self.assertEqual(log, ["open 1", "close 1"])


class FileSourceTests(unittest.TestCase):
    def test_strips_crlf(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".log", delete=False) as f:
            f.write(b"one\r\ntwo\r\n")
        try:
            sink = CollectSink()
            Pipeline(FileLineSource(f.name), sink).run()
            self.assertEqual(sink.items, ["one", "two"])
        finally:
            os.remove(f.name)

    def test_missing_file_raises(self):
        with self.assertRaises(StageException):
            Pipeline(FileLineSource("yok.log"), CollectSink()).run()


class EndToEndTests(unittest.TestCase):
    def run_main(self, path):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = logflow_main.main([path])
        return code, out.getvalue().splitlines(), err.getvalue()

    def test_main_prints_every_record_and_summary(self):
        code, lines, _ = self.run_main(SAMPLE)
        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 201)                 # 200 kayit + 1 ozet satiri
        self.assertTrue(lines[0].startswith("2026-09-29 10:00:00+03:00 85.105.14.9 GET / -> 200"))
        self.assertEqual(lines[-1], "Toplam: 200 kayit islendi, 0 hatali satir atlandi.")

    def test_main_counts_bad_lines(self):
        code, lines, _ = self.run_main(os.path.join(ROOT, "data", "access-with-errors.log"))
        self.assertEqual(code, 0)
        self.assertEqual(lines[-1], "Toplam: 3 kayit islendi, 4 hatali satir atlandi.")
        self.assertEqual(len(lines), 4)                   # 3 kayit + ozet

    def test_main_missing_file_returns_1(self):
        code, lines, err = self.run_main("yok.log")
        self.assertEqual(code, 1)
        self.assertIn("Hata", err)
        self.assertEqual(lines, [])                       # hata varsa ozet basilmaz


if __name__ == "__main__":
    unittest.main()
