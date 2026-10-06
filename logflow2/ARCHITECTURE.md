# ARCHITECTURE — Artırım 2 (Artırım 1 üzerine kurulu)

Odak: **bileşenler ve bağlayıcılar; arayüz ile uygulama farkı.**
Arayüz *ne* yapılacağını, uygulama *nasıl* yapıldığını söyler. `Pipeline` yalnızca
`Source`, `Stage`, `Sink` arayüzlerini bilir.

## İki Kutu Diyagramı

    +-----------------------+     Emitter.emit(str)     +-----------------------+
    |    FileLineSource     | ------------------------> |      ConsoleSink      |
    |   (implements Source) |   bağlayıcı (connector)   |    (implements Sink)  |
    +-----------------------+                           +-----------------------+

## Genişletilmiş görünüm (sonraki artırımlar)

    Source --emit--> [Stage 1] --emit--> [Stage 2] --emit--> Sink
                     (araya Pipeline'a dokunmadan eklenir)

## Arayüzler
| Arayüz | Sözleşme |
|---|---|
| `Source[O]` | `produce(out)` — kayıtları üretip `out`'a verir |
| `Stage[I,O]` | `process(item, out)`, `open()`, `close()` |
| `Sink[I]` | `consume(item)` |
| `Emitter[T]` | `emit(item)` — bileşenler arası bağlayıcı |

## Kararlar
1. **Emitter, dönüş değeri yerine.** Filtre 0, bölücü N çıktı üretebilir.
2. **Küçük arayüzler.** Tek sorumluluk; testte kolayca taklit edilir.
3. **Main'de iş mantığı yok.** Yalnızca argüman → kurulum → `run()`.
4. **Yaşam döngüsü güvenli.** `open` sırayla, `close` ters sırayla ve hata olsa bile çağrılır.
5. **Bilinen sınırlama.** `Pipeline[R]` tek kayıt tipiyle çalışır (`Stage[R,R]`);
   tip değiştiren stage'ler (`str → LogEntry`) sonraki artırımda ele alınacak.

---

# Artırım 2 — Tipli Kayıtlar ve İlk Gerçek Aşama

Odak: **sorumlulukların ayrılması, veri soyutlama, test disiplini.**

## Diyagram

    FileLineSource --str--> ParserStage --LogRecord--> ConsoleSink
      (dosyayı bilir)       (biçimi bilir)             (görüntüyü bilir)

Her kutu tek bir şeyi bilir: dosya okuma, CLF biçimi, ekrana yazma. `Pipeline` hâlâ yalnızca
arayüzleri bilir.

## Kararlar
6. **Alan kaydı değişmezdir.** Aşamalar arasında paylaşılan bir nesneyi bir aşama sessizce
   değiştirirse hatayı bulmak çok zorlaşır; değişmezlik bunu derleme/çalışma anında yakalar.
7. **`attributes` eşlemi genişleme noktasıdır.** Sonraki aşamalar ayrıştırıcının bilmediği veriyi
   kayda ekleyecek (5–7. haftalar). Kayıt biçimi genişlemeye açık, mevcut kodlar değişime kapalıdır.
8. **Ayrıştırma saf bir fonksiyondur** (`parse_line`: `str → LogRecord | None`). `ParserStage` yalnızca
   onu çağırır, sayar ve yayar; böylece mantık hat, dosya ve konsoldan bağımsız test edilir.
9. **Hatalı satır: bu hafta atla ve say.** Doğru ele alma 5. haftada gelecek.
10. **Önceki sınırlama giderildi.** `Pipeline[R]` tek tip taşıyordu; artık `Pipeline[I, O]`
    (kaynak tipi, hedef tipi). Aradaki dönüşümü aşamalar yapar. Yalnızca tip ipuçları değişti.

## Demo soruları

**Ayrıştırıcıyı eklemek için mevcut dosyalardan hangilerini değiştirdiniz?**
Davranış açısından yalnızca `main.py` (aşamayı hatta ekler, özeti yazar) ve `console_sink.py`
(artık `str` değil `LogRecord` alır). `pipeline.py`'da yalnızca tip ipuçları değişti, mantığı değişmedi.
`emitter.py`, `stage.py`, `source.py`, `sink.py`, `file_line_source.py` hiç değişmedi: aşama eklemek,
komşu aşamaları değiştirmeyi gerektirmedi.

**Ayrıştırıcı testiniz bir dosya okumuyor — bu nasıl mümkün ve neden önemli?**
`ParserStage` yalnızca `process(item, out)` sözleşmesine bağlıdır: girdiyi parametre olarak alır,
çıktıyı `Emitter` arayüzüne verir. Testte girdi doğrudan bir dizgidir; çıktıyı gerçek bir sink yerine
`CollectingEmitter` (test dublörü) toplar. Dosya, hat ya da konsol hiç devreye girmez.
Önemi: testler hızlıdır (milisaniye), diske/işletim sistemine bağlı değildir, başarısızlığın nedeni
tek bir aşamaya daraltılır ve her kenar durum (boş satır, bozuk saat) tek satırlık bir dizgiyle denenebilir.
Bu, arayüzlerin (Emitter) küçük ve ayrık tutulmasının doğrudan sonucudur.
