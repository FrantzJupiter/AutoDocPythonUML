from models.midia import Midia


class Serie(Midia):
    def __init__(self, titulo: str, duracao: int, temporadas: int):
        super().__init__(titulo, duracao)
        self.temporadas = temporadas

    def __str__(self):
        return f"Série: {self.titulo} - {self.temporadas} temporadas ({self.duracao} min)"
