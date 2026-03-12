import ast
import os
import sys
import urllib.parse
import argparse
from pathlib import Path
from collections import deque, defaultdict

# ==========================================
# 1. HELPERS E LINKS
# ==========================================

def get_link(file_path, line, root_dir, is_web=False, repo_url=""):
    """Gera links dinamicamente: locais (vscode://) ou remotos (GitHub/Web)."""
    try:
        abs_path = Path(file_path).resolve()
        
        if is_web and repo_url:
            rel_path = abs_path.relative_to(root_dir).as_posix()
            clean_repo = repo_url.rstrip('/')
            return f"{clean_repo}/blob/main/{rel_path}#L{line}"
        else:
            posix_path = abs_path.as_posix()
            if ':' in posix_path and not posix_path.startswith('/'): 
                posix_path = '/' + posix_path
            encoded_path = urllib.parse.quote(posix_path)
            return f"vscode://file{encoded_path}:{line}"
    except Exception: 
        return "#"

def format_annotation(node):
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

def infer_simple_type(node):
    """Infere o tipo baseado no valor atribuido no AST."""
    if isinstance(node, ast.Constant):
        return type(node.value).__name__
    elif isinstance(node, ast.List):
        return "list"
    elif isinstance(node, ast.Dict):
        return "dict"
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id 
    return "Any"

def get_base_types(node):
    found = set()
    if node is None: return found
    queue = deque([node])
    while queue:
        curr = queue.popleft()
        if isinstance(curr, ast.Name): found.add(curr.id)
        elif isinstance(curr, ast.Attribute): found.add(curr.attr)
        elif isinstance(curr, ast.Subscript):
            queue.append(curr.value)
            queue.append(curr.slice)
        elif isinstance(curr, ast.Tuple):
            for elt in curr.elts: queue.append(elt)
    return found

# ==========================================
# 2. ESTRUTURAS DE DADOS
# ==========================================

class ClassInfo:
    def __init__(self, name, filepath, lineno):
        self.name = name
        self.filepath = str(Path(filepath).resolve())
        self.lineno = lineno
        self.parents = []
        self.attrs = {}   
        self.methods = [] 
        self.is_abstract = False
        self.is_dataclass = False
        self.compositions = set()
        self.aggregations = set()
        self.dependencies = set()

    def add_attr(self, name, type_str, line):
        if name not in self.attrs or (self.attrs[name]['type'] == 'Any' and type_str != 'Any'):
            self.attrs[name] = {'type': type_str, 'line': line}

    def add_method(self, name, args, line):
        for m in self.methods:
            if m['name'] == name: return 
        self.methods.append({'name': name, 'args': args, 'line': line})

    def add_relation(self, kind, target_name, card="1"):
        if target_name == self.name: return 
        
        if kind == 'comp':
            self.aggregations = {(t, c) for t, c in self.aggregations if t != target_name}
            self.dependencies.discard(target_name)
            self.compositions.add((target_name, card))
        elif kind == 'agg':
            if target_name not in [x[0] for x in self.compositions]:
                self.dependencies.discard(target_name)
                self.aggregations.add((target_name, card))
        elif kind == 'dep':
            if target_name not in [x[0] for x in self.compositions] and \
               target_name not in [x[0] for x in self.aggregations]:
                self.dependencies.add(target_name)

class ExecutionStep:
    def __init__(self, text, line, file):
        self.text = text
        self.line = line
        self.file = file

# ==========================================
# 3. CORE ANALYZER
# ==========================================

class ProjectAnalyzer:
    def __init__(self, entry_point):
        self.entry_point = Path(entry_point).resolve()
        self.root_dir = self.entry_point.parent if self.entry_point.is_file() else self.entry_point
        self.base_repo_dir = Path.cwd() 
        self.global_classes = {} 
        self.files_ast = {}      
        self.main_flow = []
        
    def run(self):
        print(f"Indexando projeto a partir de: {self.root_dir}")
        self._step_1_index_files()
        self._step_2_analyze_relationships()
        if self.entry_point.is_file():
            self._step_3_trace_main_flow()
            return self._filter_scope()
        return self.global_classes, []

    def _step_1_index_files(self):
        py_files = list(self.root_dir.rglob("*.py"))
        me = Path(__file__).resolve()

        for path in py_files:
            if path.resolve() == me and self.entry_point != me: 
                continue
                
            try:
                with open(path, "r", encoding="utf-8") as f: source = f.read()
                tree = ast.parse(source, filename=str(path))
                self.files_ast[str(path.resolve())] = tree
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if node.name not in self.global_classes:
                            self.global_classes[node.name] = ClassInfo(node.name, path, node.lineno)
                        else:
                            self.global_classes[node.name].filepath = str(path.resolve())
                            self.global_classes[node.name].lineno = node.lineno
            except Exception as e:
                print(f"[Aviso] Falha ao processar {path.name}: {e}")

    def _step_2_analyze_relationships(self):
        for file_path, tree in self.files_ast.items():
            local_scope = {} 
            for node in tree.body:
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        real_name = alias.name
                        local_var = alias.asname if alias.asname else alias.name
                        if real_name in self.global_classes: local_scope[local_var] = real_name
            for node in tree.body:
                if isinstance(node, ast.ClassDef): local_scope[node.name] = node.name

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    self._analyze_class_ast(node, local_scope)

    def _analyze_class_ast(self, class_node, scope):
        cls_info = self.global_classes[class_node.name]
        
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                if base.id not in cls_info.parents: cls_info.parents.append(base.id)
                if base.id == 'ABC': cls_info.is_abstract = True
            elif isinstance(base, ast.Attribute):
                 if base.attr not in cls_info.parents: cls_info.parents.append(base.attr)

        for dec in class_node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == 'dataclass': cls_info.is_dataclass = True

        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                t_str = format_annotation(item.annotation)
                cls_info.add_attr(item.target.id, t_str, item.lineno)
                self._link_types(cls_info, item.annotation, 'comp' if cls_info.is_dataclass else 'agg', scope)

            if isinstance(item, ast.FunctionDef):
                args_list = [a.arg for a in item.args.args if a.arg != 'self']
                cls_info.add_method(item.name, ", ".join(args_list), item.lineno)
                
                for arg in item.args.args: self._link_types(cls_info, arg.annotation, 'dep', scope)
                self._link_types(cls_info, item.returns, 'dep', scope)

                self._analyze_method_body(cls_info, item, scope)

    def _analyze_method_body(self, cls_info, method_node, file_scope):
        method_scope = file_scope.copy()
        local_instances = {} 

        for arg in method_node.args.args:
            if arg.arg == 'self': continue
            types = get_base_types(arg.annotation)
            if types:
                for t in types:
                    if t in self.global_classes: 
                        method_scope[arg.arg] = t; break
            else:
                for known_cls in self.global_classes:
                    if arg.arg.lower() == known_cls.lower(): method_scope[arg.arg] = known_cls

        for stmt in ast.walk(method_node):
            
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        inferred_type = infer_simple_type(stmt.value)
                        cls_info.add_attr(target.attr, inferred_type, stmt.lineno)

            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                cls_name = stmt.value.func.id
                real_cls = file_scope.get(cls_name, cls_name)
                
                if real_cls in self.global_classes:
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                            cls_info.add_relation('comp', real_cls)
                        elif isinstance(target, ast.Name):
                            local_instances[target.id] = real_cls
                            cls_info.add_relation('dep', real_cls)

            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func = stmt.value.func
                if isinstance(func, ast.Attribute) and func.attr == 'append':
                    is_self_attr = (isinstance(func.value, ast.Attribute) and 
                                    isinstance(func.value.value, ast.Name) and 
                                    func.value.value.id == 'self')
                    
                    if is_self_attr and stmt.value.args:
                        arg = stmt.value.args[0]
                        
                        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                            name = arg.func.id
                            if name in file_scope: 
                                cls_info.add_relation('comp', file_scope[name], "1..*")

                        elif isinstance(arg, ast.Name):
                            var_name = arg.id
                            if var_name in local_instances:
                                cls_info.add_relation('comp', local_instances[var_name], "1..*")
                            elif var_name in method_scope:
                                cls_info.add_relation('agg', method_scope[var_name], "0..*")

            if isinstance(stmt, ast.Raise):
                if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                    if stmt.exc.func.id in file_scope:
                        cls_info.add_relation('dep', file_scope[stmt.exc.func.id])

    def _link_types(self, cls_info, annotation_node, kind, scope):
        found_types = get_base_types(annotation_node)
        for t_name in found_types:
            real_name = scope.get(t_name, t_name)
            if real_name in self.global_classes:
                card = "0..*" if "List" in format_annotation(annotation_node) else "1"
                cls_info.add_relation(kind, real_name, card)

    def _step_3_trace_main_flow(self):
        if str(self.entry_point) not in self.files_ast: return
        tree = self.files_ast[str(self.entry_point)]
        
        local_imports = {}
        for node in tree.body:
             if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    local_imports[alias.asname or alias.name] = alias.name

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    cls_name = node.value.func.id
                    real_cls = local_imports.get(cls_name, cls_name)
                    if real_cls in self.global_classes:
                        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                        var = targets[0] if targets else "obj"
                        self.main_flow.append(ExecutionStep(f"Instancia {var} : {real_cls}", node.lineno, self.entry_point.name))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Attribute):
                    method = node.value.func.attr
                    var = node.value.func.value.id if isinstance(node.value.func.value, ast.Name) else "?"
                    self.main_flow.append(ExecutionStep(f"Chama {var}.{method}()", node.lineno, self.entry_point.name))

    def _filter_scope(self):
        relevant_classes = set()
        abs_entry = str(self.entry_point)
        
        for name, info in self.global_classes.items():
            if info.filepath == abs_entry: relevant_classes.add(name)

        tree = self.files_ast.get(abs_entry)
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in self.global_classes:
                    relevant_classes.add(node.id)
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name in self.global_classes: relevant_classes.add(alias.name)

        queue = deque(relevant_classes)
        processed = set(relevant_classes)
        while queue:
            curr = queue.popleft()
            if curr not in self.global_classes: continue
            cls = self.global_classes[curr]
            neighbors = set(cls.parents)
            neighbors.update([x[0] for x in cls.compositions])
            neighbors.update([x[0] for x in cls.aggregations])
            neighbors.update(cls.dependencies)
            for n in neighbors:
                if n in self.global_classes and n not in processed:
                    processed.add(n); relevant_classes.add(n); queue.append(n)
        
        return {k: v for k, v in self.global_classes.items() if k in relevant_classes}, self.main_flow

# ==========================================
# 4. GERAÇÃO DE MARKDOWN
# ==========================================

def generate_markdown(classes, flow, title, root_dir, is_web=False, repo_url=""):
    lines = []
    lines.append(f"# Documentação: {title}")
    lines.append(f"> Gerado automaticamente via [AutoDoc.py](https://github.com/FrantzJupiter/AutoDocUML) - Criado por [FrantzJupiter](https://github.com/FrantzJupiter)")
    
    if flow:
        lines.append("\n## Fluxo de Execução (Main)")
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append("Start([Início])")
        last = "Start"
        for i, step in enumerate(flow):
            ident = f"S{i}"
            lines.append(f'{ident}["{step.text}"]')
            lines.append(f"{last} --> {ident}")
            last = ident
        lines.append(f"{last} --> End([Fim])")
        lines.append("```")

    lines.append("\n## Diagrama de Classes Unificado")
    lines.append("```mermaid")
    lines.append("classDiagram")
    lines.append("direction TB")
    
    drawn_links = set()

    for name, cls in classes.items():
        stereotypes = []
        if cls.is_abstract: stereotypes.append("<<Abstract>>")
        if cls.is_dataclass: stereotypes.append("<<Dataclass>>")
        if "Exception" in cls.parents or name.endswith("Exception"): stereotypes.append("<<Exception>>")
        
        lines.append(f"class {name} {{")
        for s in stereotypes: lines.append(f"  {s}")
        for attr, meta in list(cls.attrs.items())[:8]: 
            lines.append(f"  +{attr} : {meta['type']}")
        for meth in cls.methods[:8]:
            lines.append(f"  +{meth['name']}({meth['args']})")
        lines.append("}")

        for p in cls.parents:
            if p not in classes: lines.append(f"class {p} {{ \n <<External>> \n }}")
            link = f"{p} <|-- {name}"
            if link not in drawn_links: lines.append(link); drawn_links.add(link)

        for target, card in cls.compositions:
            if target in classes:
                l = f'{name} "1" *-- "{card}" {target} : composição'
                if l not in drawn_links: lines.append(l); drawn_links.add(l)

        for target, card in cls.aggregations:
            if target in classes:
                l = f'{name} "1" o-- "{card}" {target} : agregação'
                if l not in drawn_links: lines.append(l); drawn_links.add(l)

        for target in cls.dependencies:
            has_stronger = any(t == target for t, _ in cls.compositions | cls.aggregations)
            if target in classes and not has_stronger:
                l = f'{name} ..> {target} : usa'
                if l not in drawn_links: lines.append(l); drawn_links.add(l)

    lines.append("```")

    lines.append("\n## Índice de Navegação")
    by_file = defaultdict(list)
    for name, cls in classes.items():
        by_file[os.path.basename(cls.filepath)].append(cls)

    for filename in sorted(by_file.keys()):
        lines.append(f"\n### `{filename}`")
        for cls in sorted(by_file[filename], key=lambda x: x.name):
            link = get_link(cls.filepath, cls.lineno, root_dir, is_web, repo_url)
            lines.append(f"- **[{cls.name}]({link})** (Linha {cls.lineno})")
            
            if cls.attrs:
                lines.append("  - **Atributos:**")
                for attr, info in cls.attrs.items():
                    l = get_link(cls.filepath, info['line'], root_dir, is_web, repo_url)
                    lines.append(f"    - [{attr}]({l}) : `{info['type']}`")
            
            if cls.methods:
                lines.append("  - **Métodos:**")
                for m in cls.methods:
                    l = get_link(cls.filepath, m['line'], root_dir, is_web, repo_url)
                    lines.append(f"    - [{m['name']}()]({l})")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        try: sys.stdout.reconfigure(encoding='utf-8')
        except: pass
        
    parser = argparse.ArgumentParser(description="Gera documentacao UML e fluxos em Markdown a partir de codigo Python.")
    parser.add_argument("target_input", help="Caminho para o arquivo principal (.py)")
    parser.add_argument("--web", action="store_true", help="Gera links para o GitHub em vez do VS Code")
    parser.add_argument("--repo", default="https://github.com/FrantzJupiter/AutoDocUML", help="URL base do repositorio no GitHub")
    
    args = parser.parse_args()
    target_input = args.target_input

    if not os.path.exists(target_input):
        print("[Erro] Arquivo não encontrado.")
        sys.exit(1)

    analyzer = ProjectAnalyzer(target_input)
    classes, flow = analyzer.run()

    if not classes:
        print("[Aviso] Nenhuma classe detectada ou escopo vazio.")
        sys.exit(0)

    output_name = f"AutoDoc_{Path(target_input).stem}.md"
    
    md_content = generate_markdown(
        classes=classes, 
        flow=flow, 
        title=Path(target_input).name, 
        root_dir=analyzer.root_dir,
        is_web=args.web, 
        repo_url=args.repo
    )
    
    with open(output_name, "w", encoding="utf-8") as f: 
        f.write(md_content)
        
    print(f"[Sucesso] Documentação gerada: {output_name}")