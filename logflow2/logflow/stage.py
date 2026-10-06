from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .emitter import Emitter

I = TypeVar("I")
O = TypeVar("O")


class StageException(Exception):
    """Bir stage/source islenirken olusan hata."""


class Stage(ABC, Generic[I, O]):
    """Girdiyi isler; 0, 1 veya N cikti uretebilir.

    Neden return degil Emitter? Cunku bir filtre girdi basina 0/1/N cikti
    uretebilir; donus degeri 1:1 iliskiyi zorlar.
    """

    @abstractmethod
    def process(self, item: I, out: Emitter[O]) -> None: ...

    def open(self) -> None:  # yasam dongusu kancasi (bu hafta kullanilmiyor)
        pass

    def close(self) -> None:
        pass
