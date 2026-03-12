# 📘 Documentação: main.py
> Gerado automaticamente via AutoDoc.py - Criado por [FrantzJupiter](https://github.com/FrantzJupiter/AutoDocUML)

## 🚀 Fluxo de Execução (Main)
```mermaid
graph TD
Start([Início])
S0["Instancia app : StreamingApp"]
Start --> S0
S1["Instancia m1 : Filme"]
S0 --> S1
S2["Instancia m2 : Serie"]
S1 --> S2
S3["Chama app.cadastrar_midia()"]
S2 --> S3
S4["Chama app.cadastrar_midia()"]
S3 --> S4
S5["Chama c1.adicionar_favorito()"]
S4 --> S5
S6["Chama c1.adicionar_favorito()"]
S5 --> S6
S7["Instancia c1 : Cliente"]
S6 --> S7
S8["Chama app.cadastrar_cliente()"]
S7 --> S8
S9["Instancia c2 : Cliente"]
S8 --> S9
S10["Chama app.cadastrar_cliente()"]
S9 --> S10
S10 --> End([Fim])
```

## 🏗️ Diagrama de Classes Unificado
```mermaid
classDiagram
direction TB
class StreamingApp {
  +clientes : list
  +midias : list
  +__init__()
  +cadastrar_cliente(cliente)
  +cadastrar_midia(midia)
  +listar_midias()
  +buscar_midia(titulo)
}
StreamingApp "1" o-- "0..*" Cliente : agregação
StreamingApp "1" o-- "0..*" Midia : agregação
class Cliente {
  +nome : Any
  +favoritos : list
  +plano : Any
  +__init__(nome, plano)
  +adicionar_favorito(midia)
  +listar_favoritos()
  +__str__()
}
Cliente "1" o-- "0..*" Midia : agregação
Cliente ..> PlanoInvalidoException : usa
class PlanoInvalidoException {
  <<Exception>>
  +__init__(plano)
}
class Exception { 
 <<External>> 
 }
Exception <|-- PlanoInvalidoException
class Filme {
  +diretor : Any
  +__init__(titulo, duracao, diretor)
  +__str__()
}
Midia <|-- Filme
class Midia {
  +titulo : Any
  +_duracao : NoneType
  +duracao : Any
  +__init__(titulo, duracao)
  +duracao()
  +__str__()
}
class Serie {
  +temporadas : Any
  +__init__(titulo, duracao, temporadas)
  +__str__()
}
Midia <|-- Serie
```

## 📍 Índice de Navegação

### 📂 `app.py`
- 🟡 **[StreamingApp](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:1)** (Linha 1)
  - **Atributos:**
    - 🔹 [clientes](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:3) : `list`
    - 🔹 [midias](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:4) : `list`
  - **Métodos:**
    - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:2)
    - 🔸 [cadastrar_cliente()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:6)
    - 🔸 [cadastrar_midia()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:9)
    - 🔸 [listar_midias()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:12)
    - 🔸 [buscar_midia()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/app.py:15)

### 📂 `cliente.py`
- 🟡 **[Cliente](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:3)** (Linha 3)
  - **Atributos:**
    - 🔹 [nome](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:5) : `Any`
    - 🔹 [favoritos](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:6) : `list`
    - 🔹 [plano](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:7) : `Any`
  - **Métodos:**
    - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:4)
    - 🔸 [adicionar_favorito()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:12)
    - 🔸 [listar_favoritos()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:15)
    - 🔸 [__str__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/cliente.py:20)

### 📂 `excecoes.py`
- 🟡 **[PlanoInvalidoException](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/excecoes.py:1)** (Linha 1)
  - **Métodos:**
    - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/excecoes.py:2)

### 📂 `filme.py`
- 🟡 **[Filme](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/filme.py:3)** (Linha 3)
  - **Atributos:**
    - 🔹 [diretor](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/filme.py:6) : `Any`
  - **Métodos:**
    - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/filme.py:4)
    - 🔸 [__str__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/filme.py:8)

### 📂 `midia.py`
- 🟡 **[Midia](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:1)** (Linha 1)
  - **Atributos:**
    - 🔹 [titulo](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:3) : `Any`
    - 🔹 [_duracao](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:4) : `NoneType`
    - 🔹 [duracao](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:5) : `Any`
  - **Métodos:**
    - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:2)
    - 🔸 [duracao()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:8)
    - 🔸 [__str__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/midia.py:17)

### 📂 `serie.py`
- 🟡 **[Serie](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/serie.py:4)** (Linha 4)
  - **Atributos:**
    - 🔹 [temporadas](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/serie.py:7) : `Any`
  - **Métodos:**
    - 🔸 [__init__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/serie.py:5)
    - 🔸 [__str__()](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Script%20Auto%20Documentacao%20UML/AutoDocUML/exemplo/models/serie.py:9)