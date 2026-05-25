"""
代码分析器 - 解析代码文件，提取函数、类、导入关系等元数据
"""

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import json


@dataclass
class CodeEntity:
    """代码实体基类"""
    name: str
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)


@dataclass
class Function(CodeEntity):
    """函数/方法"""
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    is_method: bool = False
    is_async: bool = False
    complexity: int = 1
    calls: List[str] = field(default_factory=list)


@dataclass
class Class(CodeEntity):
    """类定义"""
    bases: List[str] = field(default_factory=list)
    methods: List[Function] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)


@dataclass
class Module:
    """模块/文件"""
    file_path: str
    imports: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)
    classes: List[Class] = field(default_factory=list)
    global_vars: List[str] = field(default_factory=list)
    language: str = "python"


class CodeAnalyzer:
    """代码分析器 - 支持Python、JavaScript、TypeScript等语言"""
    
    SUPPORTED_LANGUAGES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
    }
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.modules: Dict[str, Module] = {}
        self.exclude_patterns = [
            r'__pycache__', r'\.git', r'\.venv', r'venv', r'node_modules',
            r'\.pytest_cache', r'\.mypy_cache', r'dist', r'build',
            r'\.egg-info', r'\.tox', r'\.coverage'
        ]
    
    def should_exclude(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if re.search(pattern, path_str):
                return True
        return False
    
    def get_language(self, file_path: Path) -> Optional[str]:
        """根据文件扩展名获取语言"""
        ext = file_path.suffix.lower()
        return self.SUPPORTED_LANGUAGES.get(ext)
    
    def analyze_project(self) -> Dict[str, Module]:
        """分析整个项目"""
        for file_path in self.root_path.rglob('*'):
            if self.should_exclude(file_path):
                continue
            
            language = self.get_language(file_path)
            if language:
                try:
                    module = self.analyze_file(file_path, language)
                    if module:
                        relative_path = str(file_path.relative_to(self.root_path))
                        self.modules[relative_path] = module
                except Exception as e:
                    print(f"⚠️  分析文件失败 {file_path}: {e}")
        
        # 分析调用关系
        self._analyze_call_relationships()
        
        return self.modules
    
    def analyze_file(self, file_path: Path, language: str) -> Optional[Module]:
        """分析单个文件"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
        
        if language == 'python':
            return self._analyze_python_file(file_path, content)
        elif language in ('javascript', 'typescript'):
            return self._analyze_js_file(file_path, content, language)
        
        return None
    
    def _analyze_python_file(self, file_path: Path, content: str) -> Module:
        """分析Python文件"""
        module = Module(
            file_path=str(file_path.relative_to(self.root_path)),
            language='python'
        )
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return module
        
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module.imports.append(self._parse_import(node))
            
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                func = self._parse_function(node, lines, str(file_path.relative_to(self.root_path)))
                func.is_async = isinstance(node, ast.AsyncFunctionDef)
                module.functions.append(func)
            
            elif isinstance(node, ast.ClassDef):
                cls = self._parse_class(node, lines, str(file_path.relative_to(self.root_path)))
                module.classes.append(cls)
        
        return module
    
    def _parse_import(self, node: ast.AST) -> Dict[str, Any]:
        """解析导入语句"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'names': [{'name': alias.name, 'as': alias.asname} for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [{'name': alias.name, 'as': alias.asname} for alias in node.names],
                'level': node.level
            }
        return {}
    
    def _parse_function(self, node: ast.FunctionDef, lines: List[str], file_path: str) -> Function:
        """解析函数定义"""
        docstring = ast.get_docstring(node)
        
        # 计算圈复杂度
        complexity = self._calculate_complexity(node)
        
        # 提取参数
        params = []
        for arg in node.args.args:
            param_str = arg.arg
            if arg.annotation:
                param_str += f": {ast.unparse(arg.annotation)}"
            params.append(param_str)
        
        # 提取return类型
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # 提取装饰器
        decorators = []
        for decorator in node.decorator_list:
            try:
                decorators.append(ast.unparse(decorator))
            except:
                pass
        
        return Function(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            decorators=decorators,
            parameters=params,
            return_type=return_type,
            complexity=complexity,
            calls=self._extract_calls(node)
        )
    
    def _parse_class(self, node: ast.ClassDef, lines: List[str], file_path: str) -> Class:
        """解析类定义"""
        docstring = ast.get_docstring(node)
        
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except:
                pass
        
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = self._parse_function(item, lines, file_path)
                func.is_method = True
                methods.append(func)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return Class(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            bases=bases,
            methods=methods,
            attributes=attributes
        )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _extract_calls(self, node: ast.FunctionDef) -> List[str]:
        """提取函数调用"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                try:
                    if isinstance(child.func, ast.Name):
                        calls.append(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        calls.append(child.func.attr)
                except:
                    pass
        return list(set(calls))
    
    def _analyze_js_file(self, file_path: Path, content: str, language: str) -> Module:
        """分析JavaScript/TypeScript文件（简化版）"""
        module = Module(
            file_path=str(file_path.relative_to(self.root_path)),
            language=language
        )
        
        # 使用正则表达式提取基本结构
        # 提取导入
        import_pattern = r"(?:import|require)\s*\(?['\"]([^'\"]+)['\"]"
        for match in re.finditer(import_pattern, content):
            module.imports.append({
                'type': 'import',
                'names': [{'name': match.group(1), 'as': None}]
            })
        
        # 提取函数
        func_pattern = r"(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            lines_before = content[:match.start()].count('\n') + 1
            func = Function(
                name=match.group(1),
                file_path=str(file_path.relative_to(self.root_path)),
                line_start=lines_before,
                line_end=lines_before + 1,
                parameters=[p.strip() for p in match.group(2).split(',') if p.strip()],
                is_async=match.group(0).startswith('async')
            )
            module.functions.append(func)
        
        # 提取类
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{"
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            lines_before = content[:match.start()].count('\n') + 1
            bases = [match.group(2)] if match.group(2) else []
            cls = Class(
                name=match.group(1),
                file_path=str(file_path.relative_to(self.root_path)),
                line_start=lines_before,
                line_end=lines_before + 1,
                bases=bases
            )
            module.classes.append(cls)
        
        return module
    
    def _analyze_call_relationships(self):
        """分析函数调用关系"""
        # 建立函数名到模块的映射
        func_map = {}
        for module_path, module in self.modules.items():
            for func in module.functions:
                func_map[func.name] = (module_path, func)
            for cls in module.classes:
                for method in cls.methods:
                    func_map[f"{cls.name}.{method.name}"] = (module_path, method)
        
        # 解析调用关系
        for module_path, module in self.modules.items():
            for func in module.functions:
                resolved_calls = []
                for call in func.calls:
                    if call in func_map:
                        resolved_calls.append(func_map[call][0])
                func.calls = resolved_calls
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取项目统计信息"""
        stats = {
            'total_files': len(self.modules),
            'total_functions': 0,
            'total_classes': 0,
            'total_lines': 0,
            'languages': {},
            'complexity': {
                'average': 0,
                'max': 0,
                'high_complexity_functions': []
            }
        }
        
        total_complexity = 0
        
        for module_path, module in self.modules.items():
            lang = module.language
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
            
            stats['total_functions'] += len(module.functions)
            stats['total_classes'] += len(module.classes)
            
            for func in module.functions:
                total_complexity += func.complexity
                if func.complexity > stats['complexity']['max']:
                    stats['complexity']['max'] = func.complexity
                if func.complexity > 10:
                    stats['complexity']['high_complexity_functions'].append({
                        'name': func.name,
                        'file': module_path,
                        'complexity': func.complexity
                    })
            
            for cls in module.classes:
                stats['total_functions'] += len(cls.methods)
                for method in cls.methods:
                    total_complexity += method.complexity
                    if method.complexity > stats['complexity']['max']:
                        stats['complexity']['max'] = method.complexity
                    if method.complexity > 10:
                        stats['complexity']['high_complexity_functions'].append({
                            'name': f"{cls.name}.{method.name}",
                            'file': module_path,
                            'complexity': method.complexity
                        })
        
        if stats['total_functions'] > 0:
            stats['complexity']['average'] = round(total_complexity / stats['total_functions'], 2)
        
        return stats
    
    def export_json(self, output_path: str):
        """导出分析结果为JSON"""
        data = {
            'modules': {},
            'statistics': self.get_statistics()
        }
        
        for module_path, module in self.modules.items():
            data['modules'][module_path] = {
                'file_path': module.file_path,
                'language': module.language,
                'imports': module.imports,
                'functions': [
                    {
                        'name': f.name,
                        'line_start': f.line_start,
                        'line_end': f.line_end,
                        'parameters': f.parameters,
                        'return_type': f.return_type,
                        'is_async': f.is_async,
                        'complexity': f.complexity,
                        'calls': f.calls,
                        'docstring': f.docstring
                    }
                    for f in module.functions
                ],
                'classes': [
                    {
                        'name': c.name,
                        'line_start': c.line_start,
                        'line_end': c.line_end,
                        'bases': c.bases,
                        'attributes': c.attributes,
                        'methods': [
                            {
                                'name': m.name,
                                'parameters': m.parameters,
                                'return_type': m.return_type,
                                'is_async': m.is_async,
                                'complexity': m.complexity
                            }
                            for m in c.methods
                        ],
                        'docstring': c.docstring
                    }
                    for c in module.classes
                ]
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
