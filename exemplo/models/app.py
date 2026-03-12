class StreamingApp:
    def __init__(self):
        self.clientes = []
        self.midias = []

    def cadastrar_cliente(self, cliente):
        self.clientes.append(cliente)

    def cadastrar_midia(self, midia):
        self.midias.append(midia)

    def listar_midias(self):
        return "\n".join(str(m) for m in self.midias)

    def buscar_midia(self, titulo):
        for m in self.midias:
            if m.titulo.lower() == titulo.lower():
                return m
        return None
