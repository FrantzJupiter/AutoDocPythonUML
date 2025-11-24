import ast
import os
import sys
import urllib.parse
from pathlib import Path
from collections import deque

# --- HELPERS ---
def format_annotation(node):
    """Formata type hints complexos (ex: List[str])"""
    if node is None: return "Any"
    try:
        if isinstance(node, ast.Name): return node.id
        elif isinstance(node, ast.Attribute): return node.attr
        elif isinstance(node, ast.Subscript): 
            val = format_annotation(node.value)
            slice_val = format_annotation(node.slice)
            return f"{val}[{slice_val}]"
        elif isinstance(node, ast.Constant): return str(node.value)
        return "Any"
    except: return "Any"

def extract_types(node):
    """Extrai nomes de classes de dentro de type hints"""
    found = set()
    if node is None: return found
    nodes_to_check = deque([node])
    while nodes_to_check:
        curr = nodes_to_check.popleft()
        if isinstance(curr, ast.Name): found.add(curr.id)
        elif isinstance(curr, ast.Subscript):
            nodes_to_check.append(curr.value)
            nodes_to_check.append(curr.slice)
        elif isinstance(curr, ast.Tuple):
            for elt in curr.elts: nodes_to_check.append(elt)
    return found

def infer_type(node):
    if isinstance(node, ast.Constant): return type(node.value).__name__
    elif isinstance(node, ast.List): return "list"
    elif isinstance(node, ast.Dict): return "dict"
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name): return node.func.id
    return None

# --- ESTRUTURAS ---
class ClassInfo:
    def __init__(self, name, file_path, line):
        self.name = name
        self.line = line
        self.is_abstract = False
        self.is_dataclass = False
        self.attributes = {} 
        self.methods = {}    
        self.parents = []
        self.compositions = set() # (nome_classe, cardinalidade)
        self.aggregations = set() # (nome_classe, cardinalidade)
        self.dependencies = set()
        self.file_path = file_path

    def add_relation(self, type_set, target_class, cardinality="1"):
        # Helper para evitar duplicatas e gerenciar cardinalidade
        # Remove se já existir como dependência simples
        if target_class in self.dependencies:
            self.dependencies.remove(target_class)
        type_set.add((target_class, cardinality))

class FunctionInfo:
    def __init__(self, name, file_path, line):
        self.name = name
        self.line = line
        self.calls = set()
        self.dependencies = set()
        self.file_path = file_path

# --- ANÁLISE ---
def analyze_file(path):
    if not os.path.exists(path): sys.exit(1)
    with open(path, "r", encoding="utf-8") as f: source = f.read()
    tree = ast.parse(source, filename=path)
    
    all_class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    all_func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    
    classes = {}
    functions = {}

    for node in tree.body:
        # 1. CLASSES
        if isinstance(node, ast.ClassDef):
            cls = ClassInfo(node.name, path, node.lineno)
            
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == 'dataclass': cls.is_dataclass = True
            
            for base in node.bases:
                if isinstance(base, ast.Name): 
                    cls.parents.append(base.id)
                    if base.id == 'ABC': cls.is_abstract = True

            # -- Analisa Corpo da Classe --
            for item in node.body:
                
                # A) Atributos Tipados (Dataclasses ou Type Hints de Classe)
                if isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name): # Campo de Dataclass
                        type_str = format_annotation(item.annotation)
                        cls.attributes[item.target.id] = {'line': item.lineno, 'type': type_str}
                        
                        # Promoção de Type Hint para Agregação
                        types_found = extract_types(item.annotation)
                        for t in types_found:
                            if t in all_class_names:
                                card = "0..*" if "List" in type_str or "list" in type_str else "1"
                                # Se é dataclass, assumimos composição/agregação forte
                                cls.add_relation(cls.aggregations, t, card)

                # B) MÉTODOS
                if isinstance(item, ast.FunctionDef):
                    is_property = False
                    is_abstract = False
                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Name):
                            if dec.id == 'property': is_property = True
                            if dec.id == 'abstractmethod': is_abstract = True

                    # Analisa Tipos nos Argumentos (Dependências)
                    for arg in item.args.args:
                        if arg.annotation:
                            types_found = extract_types(arg.annotation)
                            cls.dependencies.update(types_found & all_class_names)
                    
                    if item.returns:
                        types_found = extract_types(item.returns)
                        cls.dependencies.update(types_found & all_class_names)

                    if is_property:
                        ret_type = format_annotation(item.returns) if item.returns else "Any"
                        cls.attributes[item.name] = {'line': item.lineno, 'type': ret_type}
                    else:
                        args_list = []
                        for arg in item.args.args:
                            if arg.arg == 'self': continue
                            arg_str = arg.arg
                            if arg.annotation: arg_str += f": {format_annotation(arg.annotation)}"
                            args_list.append(arg_str)
                        
                        method_name = item.name
                        if is_abstract: method_name += "*"
                        
                        cls.methods[method_name] = {
                            'line': item.lineno,
                            'args': ", ".join(args_list),
                            'ret': format_annotation(item.returns) if item.returns else ""
                        }
                        if is_abstract: cls.is_abstract = True

                        # Analisa Corpo do Método
                        args_map = {}
                        for arg in item.args.args:
                            if arg.arg == 'self': continue
                            if arg.annotation and isinstance(arg.annotation, ast.Name) and arg.annotation.id in all_class_names:
                                args_map[arg.arg] = (arg.annotation.id, True)
                            else:
                                for known in all_class_names:
                                    if arg.arg.lower() == known.lower(): args_map[arg.arg] = (known, False)

                        local_instances = {}
                        for stmt in ast.walk(item):
                            # Atributos self.x
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                        if target.attr not in cls.attributes:
                                            cls.attributes[target.attr] = {'line': stmt.lineno, 'type': infer_type(stmt.value)}
                            
                            # AnnAssign (self.x: List[Device] = ...)
                            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == 'self':
                                type_str = format_annotation(stmt.annotation)
                                cls.attributes[stmt.target.attr] = {'line': stmt.lineno, 'type': type_str}
                                
                                # Detecta Agregação via Type Hint
                                types_found = extract_types(stmt.annotation)
                                for t in types_found:
                                    if t in all_class_names:
                                        card = "0..*" if "List" in type_str or "list" in type_str else "1"
                                        cls.add_relation(cls.aggregations, t, card)

                            # Instanciações (Composição)
                            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                                if stmt.value.func.id in all_class_names:
                                    created = stmt.value.func.id
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and target.value.id == 'self': 
                                            cls.add_relation(cls.compositions, created, "1..*")
                                        elif isinstance(target, ast.Name): local_instances[target.id] = created
                                    # Se não salvou no self, é dependencia temporária, a menos que seja composição
                                    if created not in [x[0] for x in cls.compositions]:
                                        cls.dependencies.add(created)

                            # Listas (Append)
                            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                                if hasattr(stmt.value.func, 'attr') and stmt.value.func.attr == 'append':
                                    if stmt.value.args and isinstance(stmt.value.args[0], ast.Call):
                                        call = stmt.value.args[0]
                                        if isinstance(call.func, ast.Name) and call.func.id in all_class_names:
                                            cls.add_relation(cls.compositions, call.func.id, "1..*")
                                    elif stmt.value.args and isinstance(stmt.value.args[0], ast.Name):
                                        var = stmt.value.args[0].id
                                        if var in local_instances: 
                                            cls.add_relation(cls.compositions, local_instances[var], "1..*")
                                        elif var in args_map:
                                            detected, _ = args_map[var]
                                            # Evita duplicar se já foi detectado via type hint
                                            if detected not in [x[0] for x in cls.compositions]: 
                                                cls.add_relation(cls.aggregations, detected, "0..*")

                            # Raises
                            if isinstance(stmt, ast.Raise) and isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                                if stmt.exc.func.id in all_class_names: cls.dependencies.add(stmt.exc.func.id)

            classes[cls.name] = cls

        # 2. FUNÇÕES GLOBAIS
        elif isinstance(node, ast.FunctionDef):
            func = FunctionInfo(node.name, path, node.lineno)
            if node.returns:
                types_found = extract_types(node.returns)
                func.dependencies.update(types_found & all_class_names)
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                    tgt = sub.func.id
                    if tgt in all_func_names or tgt in all_class_names: func.calls.add(tgt)
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id in all_class_names:
                    func.dependencies.add(sub.func.id)
            functions[func.name] = func

    # 3. MAIN
    main_calls = set()
    for node in tree.body:
        if isinstance(node, ast.If):
            is_main = False
            if isinstance(node.test, ast.Compare):
                left = node.test.left
                if isinstance(left, ast.Name) and left.id == "__name__": is_main = True
            if is_main:
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                        tgt = sub.func.id
                        if tgt in all_func_names or tgt in all_class_names: main_calls.add(tgt)

    return classes, functions, main_calls

# --- CLUSTERIZAÇÃO ---
def get_clusters(classes):
    adjacency = {name: set() for name in classes}
    for name, cls in classes.items():
        # Extrai nomes das tuplas (classe, card) para o grafo
        comp_names = {x[0] for x in cls.compositions}
        agg_names = {x[0] for x in cls.aggregations}
        neighbors = comp_names | agg_names | cls.dependencies | set(cls.parents)
        for neighbor in neighbors:
            if neighbor in classes:
                adjacency[name].add(neighbor)
                adjacency[neighbor].add(name)
    visited = set(); clusters = []
    for name in classes:
        if name not in visited:
            cluster = []; queue = deque([name]); visited.add(name)
            while queue:
                curr = queue.popleft(); cluster.append(curr)
                for n in adjacency[curr]:
                    if n not in visited: visited.add(n); queue.append(n)
            clusters.append(cluster)
    return clusters

def identify_main_class(cluster_names, classes):
    if not cluster_names: return "Diagrama"
    scores = {name: 0 for name in cluster_names}
    for name in cluster_names:
        cls = classes[name]
        scores[name] += len(cls.compositions)*3 + len(cls.aggregations)*2 + len(cls.dependencies)*1
    return max(scores, key=scores.get)

def create_vscode_link(file_path, line):
    try:
        abs_path = os.path.abspath(file_path)
        path_obj = Path(abs_path)
        posix_path = path_obj.as_posix()
        if ':' in posix_path and not posix_path.startswith('/'): posix_path = '/' + posix_path
        encoded_path = urllib.parse.quote(posix_path)
        return f"vscode://file{encoded_path}:{line}"
    except: return "#"

# --- MARKDOWN GENERATION ---
def generate_mermaid(classes, functions, main_calls, file_path):
    lines = []
    filename = os.path.basename(file_path)
    lines.append(f"# Auto-Documentação: {filename}")
    lines.append(f"> Arquivo analisado: `{filename}`")
    lines.append("")

    # 1. FLUXO GLOBAL
    if functions or main_calls:
        lines.append("## 🚀 Fluxo de Execução Global")
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append("%% Estilos Transparentes")
        lines.append("classDef main fill:none,stroke:#9c27b0,stroke-width:2px;")
        lines.append("classDef func fill:none,stroke:#2196f3,stroke-width:2px;")
        lines.append("classDef cls fill:none,stroke:#ffc107,stroke-width:2px;")

        if main_calls:
            lines.append("Start([__main__])"); lines.append("class Start main")
            for call in main_calls: lines.append(f"Start --> {call}")

        for name, func in functions.items():
            lines.append(f"{name}[[{name}]]"); lines.append(f"class {name} func")
            for target in func.calls: lines.append(f"{name} --> {target}")
            for dep in func.dependencies:
                 if dep in classes: lines.append(f"{name} -.-> {dep}")

        used_classes = set().union(main_calls)
        for func in functions.values(): used_classes.update(func.calls)
        
        for name in classes:
            if name in used_classes: lines.append(f"class {name} cls")

        lines.append("```")
        lines.append("")

    # 2. DIAGRAMAS DE CLASSE
    clusters = get_clusters(classes)
    if clusters:
        lines.append("## 🏗️ Estrutura de Classes (Por Contexto)")
        for cluster in clusters:
            main_cls = identify_main_class(cluster, classes)
            ordered_names = sorted(cluster)
            
            lines.append(f"### Contexto: {main_cls}")
            lines.append("```mermaid")
            lines.append("classDiagram")
            lines.append("direction TB")
            
            for name in ordered_names:
                cls = classes[name]
                stereotype = ""
                if cls.is_abstract: stereotype = "<<Abstract>>"
                if cls.is_dataclass: stereotype = "<<Dataclass>>"
                
                lines.append(f"class {cls.name} {{")
                if stereotype: lines.append(f"  {stereotype}")
                
                for attr, info in sorted(cls.attributes.items()):
                    typ = f" : {info['type']}" if info['type'] else ""
                    lines.append(f"  +{attr}{typ}")
                for meth, info in sorted(cls.methods.items()):
                    ret = f" : {info['ret']}" if info['ret'] else ""
                    lines.append(f"  +{meth}({info['args']}){ret}")
                lines.append("}")
                
                # Herança
                for p in cls.parents:
                    if p in cluster or p in ["ABC", "Exception"]: lines.append(f"{p} <|-- {cls.name}")
                
                # Composição (com cardinalidade)
                for c_name, card in sorted(list(cls.compositions)):
                    if c_name in cluster: 
                        lines.append(f'{cls.name} "1" *-- "{card}" {c_name} : composição')
                
                # Agregação (com cardinalidade)
                for a_name, card in sorted(list(cls.aggregations)):
                    if a_name in cluster: 
                        lines.append(f'{cls.name} "1" o-- "{card}" {a_name} : agregação')
                
                # Dependência
                comp_names = {x[0] for x in cls.compositions}
                agg_names = {x[0] for x in cls.aggregations}
                for d in sorted(cls.dependencies):
                    if d in cluster and d not in comp_names and d not in agg_names:
                        lines.append(f'{cls.name} ..> {d} : usa')
            
            lines.append("```")
            lines.append("#### 📍 Navegação Detalhada")
            for name in ordered_names:
                cls = classes[name]
                link = create_vscode_link(cls.file_path, cls.line)
                lines.append(f"- 🟡 **[{cls.name}]({link})** (Linha {cls.line})")
                for attr, info in sorted(cls.attributes.items()):
                    attr_link = create_vscode_link(cls.file_path, info['line'])
                    typ = f" `({info['type']})`" if info['type'] else ""
                    lines.append(f"  - 🔹 [{attr}]({attr_link}){typ}")
                for meth, info in sorted(cls.methods.items()):
                    meth_link = create_vscode_link(cls.file_path, info['line'])
                    lines.append(f"  - 🔸 [{meth}()]({meth_link})")
            lines.append("\n---\n")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    file_path = sys.argv[1]
    try:
        classes, functions, main_calls = analyze_file(file_path)
        output = generate_mermaid(classes, functions, main_calls, file_path)
        dir_name = os.path.dirname(os.path.abspath(file_path))
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        out_name = os.path.join(dir_name, f"{base_name}_autodoc.md")
        with open(out_name, "w", encoding="utf-8") as f: f.write(output)
        print(out_name)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)