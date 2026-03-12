class Midia:
    def __init__(self, titulo: str, duracao: int):
        self.titulo = titulo
        self._duracao = None
        self.duracao = duracao  # usa o setter

    @property
    def duracao(self):
        return self._duracao

    @duracao.setter
    def duracao(self, minutos):
        if minutos <= 0:
            raise ValueError("A duração deve ser positiva.")
        self._duracao = minutos

    def __str__(self):
        return f"{self.titulo} ({self.duracao} min)"
