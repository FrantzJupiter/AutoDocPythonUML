import ast
import os
import sys
import urllib.parse
from pathlib import Path
from collections import deque

# --- ESTRUTURAS DE DADOS ---
class ClassInfo:
    def __init__(self, name, file_path, line):
        self.name = name
        self.line = line
        self.attributes = {}
        self.methods = {}
        self.parents = []
        self.compositions = set()
        self.aggregations = set()
        self.dependencies = set()
        self.file_path = file_path

class FunctionInfo:
    def __init__(self, name, file_path, line):
        self.name = name
        self.line = line
        self.calls = set()
        self.file_path = file_path

# --- ANÁLISE (O Cérebro) ---
def analyze_file(path):
    if not os.path.exists(path):
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=path)
    
    all_class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    all_func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    
    classes = {}
    functions = {}

    # 1. ANALISAR CLASSES (Lógica Detalhada Restaurada)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            cls = ClassInfo(node.name, path, node.lineno)
            # Herança
            for base in node.bases:
                if isinstance(base, ast.Name): cls.parents.append(base.id)
            
            # Métodos
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    cls.methods[item.name] = item.lineno
                    
                    # Mapeia argumentos para Agregação
                    args_map = {}
                    for arg in item.args.args:
                        if arg.arg == 'self': continue
                        if arg.annotation and isinstance(arg.annotation, ast.Name):
                            if arg.annotation.id in all_class_names:
                                args_map[arg.arg] = (arg.annotation.id, True)
                        else:
                            for known_class in all_class_names:
                                if arg.arg.lower() == known_class.lower():
                                    args_map[arg.arg] = (known_class, False)

                    local_instances = {}

                    for stmt in ast.walk(item):
                        # Captura Atributos
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    if target.attr not in cls.attributes: cls.attributes[target.attr] = stmt.lineno
                        
                        # Dependências (Raise)
                        if isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                             if stmt.exc.func.id in all_class_names: cls.dependencies.add(stmt.exc.func.id)

                        # Composição (Atribuição)
                        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id in all_class_names:
                                created_class = stmt.value.func.id
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                        cls.compositions.add(created_class)
                                    elif isinstance(target, ast.Name):
                                        local_instances[target.id] = created_class
                                # Se criou local, é dependência temporária (se não virar composição depois)
                                cls.dependencies.add(created_class)

                        # Listas (Append) - Composição vs Agregação
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            if hasattr(stmt.value.func, 'attr') and stmt.value.func.attr == 'append':
                                # Append(Classe()) -> Composição
                                if stmt.value.args and isinstance(stmt.value.args[0], ast.Call):
                                    call_node = stmt.value.args[0]
                                    if isinstance(call_node.func, ast.Name) and call_node.func.id in all_class_names:
                                        cls.compositions.add(call_node.func.id)
                                # Append(variavel)
                                elif stmt.value.args and isinstance(stmt.value.args[0], ast.Name):
                                    var_name = stmt.value.args[0].id
                                    if var_name in local_instances:
                                        cls.compositions.add(local_instances[var_name])
                                    elif var_name in args_map:
                                        detected_class, _ = args_map[var_name]
                                        if detected_class not in cls.compositions:
                                            cls.aggregations.add(detected_class)

                        # Agregação via Atribuição
                        if isinstance(stmt, ast.Assign):
                            source_arg = None
                            if isinstance(stmt.value, ast.Name): source_arg = stmt.value.id
                            if source_arg and source_arg in args_map:
                                detected_class, has_hint = args_map[source_arg]
                                if not (item.name == '__init__' and not has_hint):
                                    if detected_class not in cls.compositions:
                                        cls.aggregations.add(detected_class)

            classes[cls.name] = cls

        # 2. ANALISAR FUNÇÕES GLOBAIS
        elif isinstance(node, ast.FunctionDef):
            func = FunctionInfo(node.name, path, node.lineno)
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Call) and isinstance(sub_node.func, ast.Name):
                    target = sub_node.func.id
                    if target in all_func_names or target in all_class_names:
                        func.calls.add(target)
            functions[func.name] = func

    # 3. ANALISAR O "MAIN"
    main_calls = set()
    for node in tree.body:
        if isinstance(node, ast.If):
            is_main = False
            if isinstance(node.test, ast.Compare):
                left = node.test.left
                if isinstance(left, ast.Name) and left.id == "__name__":
                    is_main = True
            
            if is_main:
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call) and isinstance(sub_node.func, ast.Name):
                        target = sub_node.func.id
                        if target in all_func_names or target in all_class_names:
                            main_calls.add(target)

    return classes, functions, main_calls

# --- GERAÇÃO DE LINKS ---
def create_vscode_link(file_path, line):
    try:
        abs_path = os.path.abspath(file_path)
        path_obj = Path(abs_path)
        posix_path = path_obj.as_posix()
        if ':' in posix_path and not posix_path.startswith('/'):
            posix_path = '/' + posix_path
        encoded_path = urllib.parse.quote(posix_path)
        return f"vscode://file{encoded_path}:{line}"
    except:
        return "#"

# --- GERAÇÃO DO MERMAID (O Renderizador) ---
def generate_mermaid(classes, functions, main_calls, file_path):
    lines = []
    filename = os.path.basename(file_path)
    
    lines.append(f"# Auto-Documentação: {filename}")
    lines.append(f"> Arquivo analisado: `{filename}`")
    lines.append("")

    # --- SEÇÃO 1: ESTRUTURA DE CLASSES (Com cardinalidade restaurada) ---
    if classes:
        lines.append("## 🏗️ Estrutura de Classes")
        lines.append("```mermaid")
        lines.append("classDiagram")
        lines.append("direction TB")
        
        for name, cls in classes.items():
            lines.append(f"class {cls.name} {{")
            for attr in cls.attributes: lines.append(f"  +{attr}")
            for method in cls.methods: lines.append(f"  +{method}()")
            lines.append("}")
            
            # Herança
            for parent in cls.parents:
                if parent in classes or parent == "Exception":
                    lines.append(f"{parent} <|-- {cls.name}")
            
            # Composição (*--)
            for comp in sorted(cls.compositions):
                if comp in classes:
                    lines.append(f'{cls.name} "1" *-- "1..*" {comp} : composição')
            
            # Agregação (o--)
            for agg in sorted(cls.aggregations):
                if agg in classes:
                    lines.append(f'{cls.name} "1" o-- "0..*" {agg} : agregação')
            
            # Dependência (..>)
            # Filtramos para não mostrar dependência se já for composição/agregação
            for dep in sorted(cls.dependencies):
                if dep in classes and dep not in cls.compositions and dep not in cls.aggregations:
                     lines.append(f'{cls.name} ..> {dep} : usa')
            
            link = create_vscode_link(cls.file_path, cls.line)
            lines.append(f'link {cls.name} "{link}" "Ir para {cls.name}"')
        
        lines.append("```")
        lines.append("")

    # --- SEÇÃO 2: FLUXO DE EXECUÇÃO (Modo Transparente) ---
    if functions or main_calls:
        lines.append("## 🚀 Fluxo de Execução")
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append("%% Estilos Transparentes (fill:none)")
        lines.append("classDef main fill:none,stroke:#9c27b0,stroke-width:2px;")
        lines.append("classDef func fill:none,stroke:#2196f3,stroke-width:2px;")
        lines.append("classDef cls fill:none,stroke:#ffc107,stroke-width:2px;")

        if main_calls:
            lines.append("Start([__main__])")
            lines.append("class Start main")
            for call in main_calls:
                lines.append(f"Start --> {call}")

        for name, func in functions.items():
            lines.append(f"{name}[[{name}]]")
            lines.append(f"class {name} func")
            for target in func.calls:
                lines.append(f"{name} --> {target}")
            link = create_vscode_link(func.file_path, func.line)
            lines.append(f'click {name} "{link}" "Ir para função {name}"')

        for name in classes:
            # Só desenha a classe no fluxo se ela for chamada
            if any(name in f.calls for f in functions.values()) or (name in main_calls):
                lines.append(f"class {name} cls")
                link = create_vscode_link(classes[name].file_path, classes[name].line)
                lines.append(f'click {name} "{link}" "Ir para classe {name}"')

        lines.append("```")
        lines.append("")

    # --- SEÇÃO 3: ÍNDICE ---
    lines.append("## 📍 Índice de Navegação")
    if classes:
        lines.append("### Classes")
        for name, cls in sorted(classes.items()):
            link = create_vscode_link(cls.file_path, cls.line)
            lines.append(f"- 🟡 **[{name}]({link})** (Linha {cls.line})")
    
    if functions:
        lines.append("\n### Funções")
        for name, func in sorted(functions.items()):
            link = create_vscode_link(func.file_path, func.line)
            lines.append(f"- 🔵 **[{name}]({link})** (Linha {func.line})")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        classes, functions, main_calls = analyze_file(file_path)
        output = generate_mermaid(classes, functions, main_calls, file_path)
        dir_name = os.path.dirname(os.path.abspath(file_path))
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        out_name = os.path.join(dir_name, f"{base_name}_autodoc.md")
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(output)
        print(out_name)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)