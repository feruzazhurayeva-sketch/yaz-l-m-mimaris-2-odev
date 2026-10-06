"""Main uc is yapar: argumanlari oku, hatti kur, run() cagir, ozeti yaz. Baska hicbir sey."""
import argparse
import sys

from logflow.console_sink import ConsoleSink
from logflow.file_line_source import FileLineSource
from logflow.parser_stage import ParserStage
from logflow.pipeline import Pipeline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="logflow", description="Bir log dosyasini hat uzerinden yapilandirilmis kayit olarak yazar.")
    parser.add_argument("path", help="okunacak log dosyasi (ornek: data/access-small.log)")
    args = parser.parse_args(argv)                                   # 1) arguman oku

    parser_stage = ParserStage()
    pipeline = (Pipeline(FileLineSource(args.path), ConsoleSink())   # 2) hatti kur
                .add_stage(parser_stage))
    try:
        pipeline.run()                                               # 3) calistir
    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        return 1

    print(f"Toplam: {parser_stage.parsed_count} kayit islendi, "
          f"{parser_stage.skipped_count} hatali satir atlandi.")     # 4) ozet
    return 0


if __name__ == "__main__":
    sys.exit(main())
