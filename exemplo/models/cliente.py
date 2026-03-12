from models.excecoes import PlanoInvalidoException

class Cliente:
    def __init__(self, nome: str, plano: str):
        self.nome = nome
        self.favoritos = []
        self.plano = plano

        if plano not in ["basic", "premium"]:
            raise PlanoInvalidoException(plano)

    def adicionar_favorito(self, midia):
        self.favoritos.append(midia)

    def listar_favoritos(self):
        if not self.favoritos:
            return "Nenhum favorito."
        return "\n".join(str(m) for m in self.favoritos)

    def __str__(self):
        return f"Cliente: {self.nome} (Plano: {self.plano})"
