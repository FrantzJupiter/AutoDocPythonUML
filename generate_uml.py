import ast
import os
import sys
import urllib.parse
from pathlib import Path
from collections import deque

class ClassInfo:
    def __init__(self, name, file_path, line):
        self.name = name
        self.line = line
        self.attributes = {} 
        self.methods = {}    
        self.parents = []
        self.compositions = set()   # *-- (Tem dentro)
        self.aggregations = set()   # o-- (Recebe e guarda)
        self.dependencies = set()   # ..> (Usa temporariamente / Raise)
        self.file_path = file_path

def analyze_file(path):
    if not os.path.exists(path):
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=path)
    all_class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    classes = {}

    for class_node in [node for node in tree.body if isinstance(node, ast.ClassDef)]:
        cls = ClassInfo(class_node.name, path, class_node.lineno)

        # 1. Herança
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                cls.parents.append(base.id)

        # 2. Métodos
        for method_node in [n for n in class_node.body if isinstance(n, ast.FunctionDef)]:
            cls.methods[method_node.name] = method_node.lineno
            
            args_map = {}
            for arg in method_node.args.args:
                if arg.arg == 'self': continue
                if arg.annotation and isinstance(arg.annotation, ast.Name):
                    if arg.annotation.id in all_class_names:
                        args_map[arg.arg] = (arg.annotation.id, True)
                else:
                    for known_class in all_class_names:
                        if arg.arg.lower() == known_class.lower():
                            args_map[arg.arg] = (known_class, False)

            local_instances = {} 

            for stmt in ast.walk(method_node):
                # Captura de atributos
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                            if target.attr not in cls.attributes:
                                cls.attributes[target.attr] = stmt.lineno

                # --- Lógica de Relacionamentos ---

                # A. Detectar 'raise Class()' (Dependência)
                if isinstance(stmt, ast.Raise):
                    if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                        if stmt.exc.func.id in all_class_names:
                             cls.dependencies.add(stmt.exc.func.id)

                # B. Composição/Agregação via Atribuição
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id in all_class_names:
                        created_class = stmt.value.func.id
                        # Se salvar no self -> Composição
                        is_composition = False
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                cls.compositions.add(created_class)
                                is_composition = True
                            elif isinstance(target, ast.Name):
                                local_instances[target.id] = created_class
                        
                        # Se criou localmente mas não salvou no self -> Dependência (Uso temporário)
                        if not is_composition:
                            cls.dependencies.add(created_class)

                # C. Appends (Listas)
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
                                cls.compositions.add(local_instances[var_name]) # É composição pois foi criado dentro
                            elif var_name in args_map:
                                detected_class, has_hint = args_map[var_name]
                                if detected_class not in cls.compositions:
                                    cls.aggregations.add(detected_class) # É agregação pois veio de fora

                # D. Atribuição de Argumento (Agregação)
                if isinstance(stmt, ast.Assign):
                    source_arg = None
                    if isinstance(stmt.value, ast.Name):
                        source_arg = stmt.value.id
                    
                    if source_arg and source_arg in args_map:
                        detected_class, has_hint = args_map[source_arg]
                        if method_node.name == '__init__' and not has_hint:
                            continue
                        if detected_class not in cls.compositions:
                            cls.aggregations.add(detected_class)

        classes[cls.name] = cls
    return classes

def get_clusters(classes):
    """Agrupa classes conectadas (incluindo dependências)"""
    adjacency = {name: set() for name in classes}
    for name, cls in classes.items():
        # Agora inclui dependencias no grafo para agrupar exceções com quem as lança
        neighbors = cls.compositions | cls.aggregations | cls.dependencies | set(cls.parents)
        for neighbor in neighbors:
            if neighbor in classes:
                adjacency[name].add(neighbor)
                adjacency[neighbor].add(name)
    
    visited = set()
    clusters = []
    for name in classes:
        if name not in visited:
            cluster = []
            queue = deque([name])
            visited.add(name)
            while queue:
                current = queue.popleft()
                cluster.append(current)
                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            clusters.append(cluster)
    return clusters

def identify_main_class(cluster_names, classes):
    if not cluster_names: return "Diagrama"
    if len(cluster_names) == 1: return cluster_names[0]
    scores = {name: 0 for name in cluster_names}
    for name in cluster_names:
        cls = classes[name]
        scores[name] += len(cls.compositions) * 3
        scores[name] += len(cls.aggregations) * 2
        scores[name] += len(cls.dependencies) * 1
        
        # Penaliza classes que são "filhas" ou "dependências" de outras
        for potential_parent in cluster_names:
            if name in classes[potential_parent].compositions: scores[name] -= 2
            if name in classes[potential_parent].aggregations: scores[name] -= 1
            if name in classes[potential_parent].dependencies: scores[name] -= 1
    return max(scores, key=scores.get)

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

def generate_mermaid(classes):
    clusters = get_clusters(classes)
    lines = []
    
    lines.append("# Diagramas UML Gerados")
    lines.append(f"> Arquivo analisado: `{os.path.basename(list(classes.values())[0].file_path)}`")
    lines.append("")

    for cluster_names in clusters:
        main_class = identify_main_class(cluster_names, classes)
        ordered_names = sorted(cluster_names)
        
        lines.append(f"## Contexto: {main_class}")
        lines.append("")
        
        # --- DIAGRAMA ---
        lines.append("```mermaid")
        lines.append("classDiagram")
        lines.append("direction TB")
        
        for name in ordered_names:
            cls = classes[name]
            lines.append(f"class {cls.name} {{")
            for attr in sorted(cls.attributes.keys()):
                lines.append(f"  +{attr}")
            for method in sorted(cls.methods.keys()):
                lines.append(f"  +{method}()")
            lines.append("}")

        for name in ordered_names:
            cls = classes[name]
            
            # Herança
            for parent in cls.parents:
                if parent in cluster_names:
                    lines.append(f"{parent} <|-- {cls.name}")
                # Se herdar de Exception (builtin), mostra também se quiser, ou remove se preferir só classes do arquivo
                elif parent == "Exception": 
                    lines.append(f"Exception <|-- {cls.name}")
            
            # Composição (*--)
            for comp in sorted(cls.compositions):
                if comp in cluster_names:
                    lines.append(f'{cls.name} "1" *-- "1..*" {comp} : composição')
            
            # Agregação (o--)
            for agg in sorted(cls.aggregations):
                if agg in cluster_names:
                    lines.append(f'{cls.name} "1" o-- "0..*" {agg} : agregação')
            
            # Dependência (..>) NOVO!
            for dep in sorted(cls.dependencies):
                if dep in cluster_names:
                     lines.append(f'{cls.name} ..> {dep} : usa')

        # Link na Classe
        for name in ordered_names:
            cls = classes[name]
            link = create_vscode_link(cls.file_path, cls.line)
            lines.append(f'link {cls.name} "{link}" "Ir para Classe"')

        lines.append("```")
        
        # --- ÍNDICE ---
        lines.append("\n### 📍 Navegação Detalhada no Código")
        
        for name in ordered_names:
            cls = classes[name]
            cls_link = create_vscode_link(cls.file_path, cls.line)
            lines.append(f"- **[{cls.name}]({cls_link})** (Linha {cls.line})")
            
            if cls.attributes:
                for attr, line in sorted(cls.attributes.items()):
                    attr_link = create_vscode_link(cls.file_path, line)
                    lines.append(f"  - 🔹 [{attr}]({attr_link})")
            
            if cls.methods:
                for method, line in sorted(cls.methods.items()):
                    method_link = create_vscode_link(cls.file_path, line)
                    lines.append(f"  - 🔸 [{method}()]({method_link})")
        
        lines.append("\n---\n")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        classes = analyze_file(file_path)
        output = generate_mermaid(classes)
        dir_name = os.path.dirname(os.path.abspath(file_path))
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        out_name = os.path.join(dir_name, f"uml_{base_name}.md")
        with open(out_name, "w", encoding="utf-8") as f:
            f.write(output)
        print(out_name)
    except Exception:
        sys.exit(1)