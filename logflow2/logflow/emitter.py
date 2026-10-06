from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Emitter(ABC, Generic[T]):
    """Bir bilesenin ciktisini bir sonrakine iletme sozlesmesi (baglayici)."""

    @abstractmethod
    def emit(self, item: T) -> None: ...


class FunctionEmitter(Emitter[T]):
    """Bir fonksiyonu Emitter olarak sarar."""

    def __init__(self, fn: Callable[[T], None]) -> None:
        self._fn = fn

    def emit(self, item: T) -> None:
        self._fn(item)
