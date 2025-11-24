# Auto-Documentação: generate_uml.py
> Arquivo analisado: `generate_uml.py`

## 🏗️ Estrutura de Classes
```mermaid
classDiagram
direction TB
class ClassInfo {
  +name
  +line
  +attributes : dict
  +methods : dict
  +parents : list
  +compositions : set
  +aggregations : set
  +dependencies : set
  +file_path
  +__init__(name, file_path, line)
}
link ClassInfo "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:42" "Ir para ClassInfo"
class FunctionInfo {
  +name
  +line
  +calls : set
  +file_path
  +__init__(name, file_path, line)
}
link FunctionInfo "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:54" "Ir para FunctionInfo"
```

## 🚀 Fluxo de Execução
```mermaid
graph TD
%% Estilos Transparentes
classDef main fill:none,stroke:#9c27b0,stroke-width:2px;
classDef func fill:none,stroke:#2196f3,stroke-width:2px;
classDef cls fill:none,stroke:#ffc107,stroke-width:2px;
Start([__main__])
class Start main
Start --> generate_mermaid
Start --> analyze_file
format_annotation[[format_annotation]]
class format_annotation func
format_annotation --> format_annotation
click format_annotation "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:9" "Ir para função format_annotation"
infer_type[[infer_type]]
class infer_type func
click infer_type "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:29" "Ir para função infer_type"
analyze_file[[analyze_file]]
class analyze_file func
analyze_file --> ClassInfo
analyze_file --> format_annotation
analyze_file --> infer_type
analyze_file --> FunctionInfo
click analyze_file "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:62" "Ir para função analyze_file"
create_vscode_link[[create_vscode_link]]
class create_vscode_link func
click create_vscode_link "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:207" "Ir para função create_vscode_link"
generate_mermaid[[generate_mermaid]]
class generate_mermaid func
generate_mermaid --> create_vscode_link
click generate_mermaid "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:219" "Ir para função generate_mermaid"
class ClassInfo cls
click ClassInfo "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:42" "Ir para classe ClassInfo"
class FunctionInfo cls
click FunctionInfo "vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:54" "Ir para classe FunctionInfo"
```

## 📍 Índice de Navegação
### Classes
- 🟡 **[ClassInfo](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:42)** (Linha 42)
- 🟡 **[FunctionInfo](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:54)** (Linha 54)

### Funções
- 🔵 **[analyze_file](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:62)** (Linha 62)
- 🔵 **[create_vscode_link](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:207)** (Linha 207)
- 🔵 **[format_annotation](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:9)** (Linha 9)
- 🔵 **[generate_mermaid](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:219)** (Linha 219)
- 🔵 **[infer_type](vscode://file/C%3A/Users/luisf/Desktop/Frantz/Estudos/Uniacademia/Orienta%C3%A7%C3%A3o%20a%20objetos/excecoes_poo/generate_uml.py:29)** (Linha 29)