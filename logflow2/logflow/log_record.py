from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class LogRecord:
    """Hattan akan alan kaydi (domain record). DEGISMEZ (immutable).

    Alanlar atanamaz (frozen=True) ve `attributes` salt-okunur bir gorunume
    sarilir; yani bir stage kaydi "yerinde" degistiremez, yenisini uretir.

    Neden `attributes`?
        Kayit bicimi genislemeye acik olmali. 5-7. haftalardaki asamalar
        (zenginlestirme, etiketleme vb.) bugunku ayristiricinin HICBIR sey
        bilmedigi verileri (ornegin cografi konum, oturum kimligi) kayda
        eklemek isteyecek. Her yeni veri icin LogRecord'a alan eklersek,
        kaydi kullanan her dosya degisir. `attributes` ile yeni veri, mevcut
        kodlara dokunmadan anahtar/deger olarak tasinir.
    """

    timestamp: datetime            # saat dilimi bilgili (timezone-aware) an
    client_ip: str
    method: str
    path: str                      # sorgu dizesi (?id=42) dahil
    status: int
    bytes: int                     # CLF'de "-" ise 0
    user_agent: str
    attributes: Mapping[str, str] = field(default_factory=dict)
    raw: str = ""                  # ham satir (hata ayiklama / denetim icin)

    def __post_init__(self) -> None:
        # Kopyalayip salt-okunur yap: disaridaki dict sonradan degisse de kayit degismez.
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))
