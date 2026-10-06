# LogFlow — Artırım 2: Tipli Kayıtlar ve İlk Gerçek Filtre

Bir log dosyasını **hat (pipeline)** üzerinden okuyup, her satırı yapılandırılmış bir
`LogRecord` nesnesine çevirerek konsola yazan küçük bir sistem.
Bu artırımda hat artık `str` değil, **alan modeli (domain model)** taşır.

## Çalıştırma (Python 3.8+, ek paket yok)

    py main.py data/access-small.log            # Windows
    python3 main.py data/access-small.log       # macOS / Linux
    py main.py data/access-with-errors.log      # hatalı satırlı örnek
    py main.py --help

Örnek çıktı:

    2026-09-29 10:00:00+03:00 85.105.14.9 GET / -> 200 (16169 B) ua="Mozilla/5.0"
    ...
    Toplam: 200 kayit islendi, 0 hatali satir atlandi.

Hatalı satırlar **yalnızca atlanır ve sayılır**; sayı en sonda yazdırılır.
Bunların doğru ele alınması (hata kaydı, karantina vb.) **5. haftada** gelecek —
mimari katman katman inşa edilir.

## Testler

    py -m unittest discover -s tests -v

33 test: `ParserStage` (8 zorunlu durum + ek durumlar), `LogRecord` (değişmezlik),
`ConsoleSink`, hat yaşam döngüsü ve uçtan uca çıktı.

`ParserStage` testleri dosya sistemine **dokunmaz**: aşamaya bir dizgi verilir, yaydığı
çıktılar `tests/collecting_emitter.py` içindeki **toplayıcı emitter** (test dublörü) ile yakalanır.
Bu test dublörü sonraki haftalarda da yeniden kullanılacak.

## Satır kapsama (line coverage)

| Dosya | Kapsama |
|---|---|
| `logflow/parser_stage.py` | %100 |
| `logflow/log_record.py` | %100 |
| `logflow/console_sink.py` | %100 |
| `logflow/pipeline.py` | %100 |
| diğer `logflow/*.py` | %100 |
| `main.py` | %96 (yalnızca `sys.exit(main())` satırı) |
| **Toplam** | **%99,5** (216 çalıştırılabilir satırın 215'i) |

Ölçüm, Python standart kütüphanesindeki `trace` modülüyle yapıldı (`tests/` hariç).
`coverage` paketiyle yeniden ölçmek için:

    pip install coverage
    python -m coverage run -m unittest discover -s tests
    python -m coverage report -m

## Sözlük
| Terim | Anlamı | Bizde |
|---|---|---|
| Record | Hattan akan veri birimi | `LogRecord` (değişmez) |
| Stage | Kaydı işleyen, 0/1/N çıktı üretebilen bileşen | `ParserStage` (`str` → `LogRecord`) |
| Source | Kayıt üretir | `FileLineSource` |
| Sink | Kayıt tüketir | `ConsoleSink` |
| Pipeline | Zinciri kurar ve çalıştırır | `Pipeline` |
| Collecting emitter | Yayılanları listeye toplayan test dublörü | `tests/collecting_emitter.py` |

## Dizin
    logflow/          emitter, stage, source, sink (arayüzler); file_line_source,
                      console_sink (uygulamalar); log_record (alan kaydı);
                      parser_stage (CLF ayrıştırıcı); pipeline
    main.py           argüman oku → hattı kur → run() → özet yaz
    tests/            birim ve uçtan uca testler + collecting_emitter (test dublörü)
    data/             access-small.log (200 satır), access-with-errors.log (hatalı satırlı)
    ARCHITECTURE.md   mimari açıklama, demo soruları
    CHANGELOG.md      değişen dosyaların listesi

## Tasarım notları
- **`LogRecord` değişmezdir** (`frozen=True`; `attributes` salt-okunur). Bir aşama kaydı
  değiştiremez, yenisini üretir.
- **`attributes` eşlemi** genişleme noktasıdır: sonraki aşamalar (5–7. haftalar),
  bugünkü ayrıştırıcının bilmediği verileri kayda ekleyecektir. Yeni veri için
  `LogRecord`'a alan eklemek yerine anahtar/değer eklenir; kaydı kullanan hiçbir dosya değişmez.
  Ayrıştırıcı bunu şimdilik boş bırakır.
- **Biçim:** CLF; satır sonunda isteğe bağlı `"referer" "user-agent"` (combined biçim) desteklenir.
  User-agent yoksa boş dizgi olur. Bayt alanı `-` ise 0 sayılır.
- **Hatalı sayılanlar:** boş satır, eksik alan, geçersiz zaman damgası (bilinmeyen ay,
  imkânsız gün/saat), 100–599 dışı veya sayısal olmayan durum kodu, sayısal olmayan bayt,
  `METHOD yol` biçiminde olmayan istek satırı.
- `Stage.process` değer döndürmez, `Emitter` ile yayar: filtre/ayrıştırıcı 0, bölücü N çıktı üretebilir.

Sürüm: `v2`
