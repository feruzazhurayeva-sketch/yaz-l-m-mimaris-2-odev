from logflow.emitter import Emitter


class CollectingEmitter(Emitter):
    """Test dublori (test double): stage'in yaydigi her ogeyi listeye toplar.

    Stage testlerinde dosya, ag ya da gercek Sink gerekmez:
        stage.process("bir satir", emitter)  ->  emitter.items
    Her hafta yeniden kullanilir.
    """

    def __init__(self) -> None:
        self.items = []

    def emit(self, item) -> None:
        self.items.append(item)
