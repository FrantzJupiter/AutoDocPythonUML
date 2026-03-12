from models.midia import Midia

class Filme(Midia):
    def __init__(self, titulo: str, duracao: int, diretor: str):
        super().__init__(titulo, duracao)
        self.diretor = diretor

    def __str__(self):
        return f"Filme: {self.titulo} - Dir: {self.diretor} ({self.duracao} min)"
