# Değişiklik Günlüğü

## v2 — Artırım 2: Tipli kayıtlar ve ilk gerçek aşama

Hatta `str` yerine `LogRecord` akar; araya `ParserStage` eklendi.

### Yeni dosyalar
- `logflow/log_record.py` — değişmez `LogRecord` (+ `attributes` genişleme noktası)
- `logflow/parser_stage.py` — CLF ayrıştırıcı `ParserStage`; hatalı satırları atlar ve sayar
- `tests/collecting_emitter.py` — toplayıcı emitter (test dublörü)
- `tests/test_parser_stage.py` — ParserStage testleri (8 zorunlu + ek durumlar)
- `tests/test_log_record.py` — değişmezlik testleri
- `tests/test_console_sink.py` — ConsoleSink biçim testleri
- `data/access-with-errors.log` — hatalı satırlı örnek veri
- `CHANGELOG.md` — bu dosya

### Değiştirilen dosyalar
- `main.py` — hatta `ParserStage` eklendi; sonda "Toplam: N kayıt, M hatalı satır" özeti
- `logflow/console_sink.py` — `Sink[str]` → `Sink[LogRecord]`; tek satırlık okunabilir biçim
- `logflow/pipeline.py` — **yalnızca tip ipuçları**: `Pipeline[R]` → `Pipeline[I, O]`,
  `Stage[R,R]` → `Stage[Any,Any]`. Çalışma mantığı (`run`, `_build_chain`, `_link`) aynıdır.
- `tests/test_pipeline.py` — uçtan uca testler yeni çıktıya göre güncellendi
  (+ hatalı satır sayımı testi); hat testleri değişmedi
- `README.md`, `ARCHITECTURE.md`, `.github/workflows/tests.yml` — dokümantasyon ve CI (kapsama raporu)

### Değişmeyen dosyalar
`emitter.py`, `stage.py`, `source.py`, `sink.py`, `file_line_source.py`
— yeni aşama eklenirken komşu bileşenler değişmedi.

## v1 — Artırım 1: İskelet hat
