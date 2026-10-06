from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .emitter import Emitter

O = TypeVar("O")


class Source(ABC, Generic[O]):
    """Kayit uretir ve Emitter'a verir."""

    @abstractmethod
    def produce(self, out: Emitter[O]) -> None: ...
