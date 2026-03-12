#Desafio: Sistema Streaming com conceitos de POO - Professor Christien
#Luis Frantz Granado Junior

from models.filme import Filme
from models.serie import Serie
from models.cliente import Cliente
from models.app import StreamingApp
from models.excecoes import PlanoInvalidoException

def main():
    app = StreamingApp()

    # Cadastro de mídias
    m1 = Filme("A Origem", 148, "Christopher Nolan")
    m2 = Serie("Breaking Bad", 47, 5)

    app.cadastrar_midia(m1)
    app.cadastrar_midia(m2)

    print("\n--- Mídias cadastradas ---")
    print(app.listar_midias())

    # Cadastro de cliente com try/except
    print("\n--- Cadastro de clientes ---")

    try:
        c1 = Cliente("João", "premium")
        app.cadastrar_cliente(c1)
    except PlanoInvalidoException as e:
        print("[ERRO]", e)

    try:
        # este gera erro para demonstrar o tratamento
        c2 = Cliente("Maria", "superplus")
        app.cadastrar_cliente(c2)
    except PlanoInvalidoException as e:
        print("[ERRO]", e)

    # Adicionar favoritos
    print("\n--- Favoritos de João ---")
    c1.adicionar_favorito(m1)
    c1.adicionar_favorito(m2)

    print(c1.listar_favoritos())

    # Buscar mídia
    buscada = app.buscar_midia("A ORIGEM")
    print("\nBusca por título:", buscada)

if __name__ == "__main__":
    main()
