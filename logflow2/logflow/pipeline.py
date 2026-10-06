from typing import Any, Generic, List, TypeVar

from .emitter import Emitter, FunctionEmitter
from .sink import Sink
from .source import Source
from .stage import Stage

I = TypeVar("I")   # source'un urettigi kayit tipi
O = TypeVar("O")   # sink'in tukettigi kayit tipi


class Pipeline(Generic[I, O]):
    """Source -> [Stage ...] -> Sink.

    Pipeline yalnizca arayuzleri bilir; dosya mi, ag mi, konsol mu oldugunu bilmez.
    Source ile Sink farkli kayit tipleri tasiyabilir (ornegin str -> LogRecord);
    aradaki tip donusumunu stage'ler yapar. Calisma mantigi artirim 1'dekiyle aynidir.
    """

    def __init__(self, source: Source[I], sink: Sink[O]) -> None:
        self._source = source
        self._sink = sink
        self._stages: List[Stage[Any, Any]] = []

    def add_stage(self, stage: Stage[Any, Any]) -> "Pipeline[I, O]":
        self._stages.append(stage)
        return self

    def run(self) -> None:
        opened: List[Stage[Any, Any]] = []
        try:
            for stage in self._stages:
                stage.open()
                opened.append(stage)
            self._source.produce(self._build_chain())
        finally:
            # Hata olsa bile acilan stage'ler ters sirada kapanir.
            for stage in reversed(opened):
                stage.close()

    def _build_chain(self) -> Emitter[Any]:
        # Sondan basa kur: sink <- stage[n-1] <- ... <- stage[0]
        head: Emitter[Any] = FunctionEmitter(self._sink.consume)
        for stage in reversed(self._stages):
            head = FunctionEmitter(self._link(stage, head))
        return head

    @staticmethod
    def _link(stage: Stage[Any, Any], nxt: Emitter[Any]):
        return lambda item: stage.process(item, nxt)
