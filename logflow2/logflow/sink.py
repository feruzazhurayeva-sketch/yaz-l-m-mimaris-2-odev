from abc import ABC, abstractmethod
from typing import Generic, TypeVar

I = TypeVar("I")


class Sink(ABC, Generic[I]):
    """Hattin sonu; kayitlari tuketir."""

    @abstractmethod
    def consume(self, item: I) -> None: ...
