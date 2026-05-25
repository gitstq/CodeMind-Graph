"""
图谱构建器 - 将代码分析结果构建为知识图谱
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum


class NodeType(Enum):
    """节点类型"""
    MODULE = "module"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    IMPORT = "import"
    PACKAGE = "package"


class EdgeType(Enum):
    """边类型"""
    CONTAINS = "contains"           # 包含关系
    CALLS = "calls"                 # 调用关系
    IMPORTS = "imports"             # 导入关系
    INHERITS = "inherits"           # 继承关系
    DEPENDS = "depends"             # 依赖关系


@dataclass
class Node:
    """图谱节点"""
    id: str
    type: NodeType
    label: str
    file_path: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type.value,
            'label': self.label,
            'file_path': self.file_path,
            'properties': self.properties
        }


@dataclass
class Edge:
    """图谱边"""
    source: str
    target: str
    type: EdgeType
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type.value,
            'properties': self.properties
        }


class GraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.module_nodes: Dict[str, str] = {}  # file_path -> node_id
        self.function_nodes: Dict[str, str] = {}  # "file_path::func_name" -> node_id
        self.class_nodes: Dict[str, str] = {}  # "file_path::class_name" -> node_id
    
    def build_from_modules(self, modules: Dict[str, Any]) -> Tuple[Dict[str, Node], List[Edge]]:
        """从模块数据构建知识图谱"""
        # 第一步：创建所有节点
        for module_path, module_data in modules.items():
            self._create_module_node(module_path, module_data)
        
        # 第二步：创建边关系
        for module_path, module_data in modules.items():
            self._create_module_edges(module_path, module_data)
        
        return self.nodes, self.edges
    
    def _create_module_node(self, module_path: str, module_data: Dict):
        """创建模块节点及其子节点"""
        # 创建模块节点
        module_id = f"module:{module_path}"
        module_node = Node(
            id=module_id,
            type=NodeType.MODULE,
            label=module_path.split('/')[-1] if '/' in module_path else module_path,
            file_path=module_path,
            properties={
                'full_path': module_path,
                'language': module_data.get('language', 'unknown'),
                'import_count': len(module_data.get('imports', [])),
                'function_count': len(module_data.get('functions', [])),
                'class_count': len(module_data.get('classes', []))
            }
        )
        self.nodes[module_id] = module_node
        self.module_nodes[module_path] = module_id
        
        # 创建函数节点
        for func in module_data.get('functions', []):
            func_id = f"func:{module_path}::{func['name']}"
            func_node = Node(
                id=func_id,
                type=NodeType.FUNCTION,
                label=func['name'],
                file_path=module_path,
                properties={
                    'line_start': func.get('line_start', 0),
                    'line_end': func.get('line_end', 0),
                    'parameters': func.get('parameters', []),
                    'return_type': func.get('return_type'),
                    'is_async': func.get('is_async', False),
                    'complexity': func.get('complexity', 1),
                    'docstring': func.get('docstring', '')
                }
            )
            self.nodes[func_id] = func_node
            self.function_nodes[f"{module_path}::{func['name']}"] = func_id
            
            # 添加包含边
            self.edges.append(Edge(
                source=module_id,
                target=func_id,
                type=EdgeType.CONTAINS
            ))
        
        # 创建类节点
        for cls in module_data.get('classes', []):
            cls_id = f"class:{module_path}::{cls['name']}"
            cls_node = Node(
                id=cls_id,
                type=NodeType.CLASS,
                label=cls['name'],
                file_path=module_path,
                properties={
                    'line_start': cls.get('line_start', 0),
                    'line_end': cls.get('line_end', 0),
                    'bases': cls.get('bases', []),
                    'attributes': cls.get('attributes', []),
                    'method_count': len(cls.get('methods', [])),
                    'docstring': cls.get('docstring', '')
                }
            )
            self.nodes[cls_id] = cls_node
            self.class_nodes[f"{module_path}::{cls['name']}"] = cls_id
            
            # 添加包含边
            self.edges.append(Edge(
                source=module_id,
                target=cls_id,
                type=EdgeType.CONTAINS
            ))
            
            # 创建方法节点
            for method in cls.get('methods', []):
                method_id = f"method:{module_path}::{cls['name']}.{method['name']}"
                method_node = Node(
                    id=method_id,
                    type=NodeType.METHOD,
                    label=method['name'],
                    file_path=module_path,
                    properties={
                        'class': cls['name'],
                        'parameters': method.get('parameters', []),
                        'return_type': method.get('return_type'),
                        'is_async': method.get('is_async', False),
                        'complexity': method.get('complexity', 1)
                    }
                )
                self.nodes[method_id] = method_node
                self.function_nodes[f"{module_path}::{cls['name']}.{method['name']}"] = method_id
                
                # 添加包含边
                self.edges.append(Edge(
                    source=cls_id,
                    target=method_id,
                    type=EdgeType.CONTAINS
                ))
    
    def _create_module_edges(self, module_path: str, module_data: Dict):
        """创建模块间的边关系"""
        module_id = self.module_nodes.get(module_path)
        if not module_id:
            return
        
        # 处理导入关系
        for imp in module_data.get('imports', []):
            if imp.get('type') == 'from_import':
                imported_module = imp.get('module', '')
                if imported_module:
                    # 尝试找到被导入的模块
                    for mp, mid in self.module_nodes.items():
                        if imported_module in mp or mp.endswith(imported_module.replace('.', '/') + '.py'):
                            self.edges.append(Edge(
                                source=module_id,
                                target=mid,
                                type=EdgeType.IMPORTS,
                                properties={'imported_names': [n['name'] for n in imp.get('names', [])]}
                            ))
                            break
        
        # 处理函数调用关系
        for func in module_data.get('functions', []):
            func_id = f"func:{module_path}::{func['name']}"
            if func_id not in self.nodes:
                continue
            
            for call in func.get('calls', []):
                # 尝试找到被调用的函数
                target_id = self._resolve_call_target(call, module_path)
                if target_id and target_id in self.nodes:
                    self.edges.append(Edge(
                        source=func_id,
                        target=target_id,
                        type=EdgeType.CALLS
                    ))
        
        # 处理类继承关系
        for cls in module_data.get('classes', []):
            cls_id = f"class:{module_path}::{cls['name']}"
            if cls_id not in self.nodes:
                continue
            
            for base in cls.get('bases', []):
                # 尝试找到基类
                base_id = self._resolve_class_target(base, module_path)
                if base_id and base_id in self.nodes:
                    self.edges.append(Edge(
                        source=cls_id,
                        target=base_id,
                        type=EdgeType.INHERITS
                    ))
    
    def _resolve_call_target(self, call_name: str, current_module: str) -> Optional[str]:
        """解析函数调用目标"""
        # 首先在当前模块中查找
        target_id = self.function_nodes.get(f"{current_module}::{call_name}")
        if target_id:
            return target_id
        
        # 在所有模块中查找
        for key, node_id in self.function_nodes.items():
            if key.endswith(f"::{call_name}") or key.endswith(f".{call_name}"):
                return node_id
        
        return None
    
    def _resolve_class_target(self, class_name: str, current_module: str) -> Optional[str]:
        """解析类目标"""
        # 首先在当前模块中查找
        target_id = self.class_nodes.get(f"{current_module}::{class_name}")
        if target_id:
            return target_id
        
        # 在所有模块中查找
        for key, node_id in self.class_nodes.items():
            if key.endswith(f"::{class_name}"):
                return node_id
        
        return None
    
    def get_subgraph(self, node_id: str, depth: int = 1) -> Tuple[List[Node], List[Edge]]:
        """获取节点的子图"""
        if node_id not in self.nodes:
            return [], []
        
        visited = {node_id}
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for edge in self.edges:
                if edge.source in current_level:
                    visited.add(edge.target)
                    next_level.add(edge.target)
                if edge.target in current_level:
                    visited.add(edge.source)
                    next_level.add(edge.source)
            current_level = next_level
        
        subgraph_nodes = [self.nodes[nid] for nid in visited if nid in self.nodes]
        subgraph_edges = [
            edge for edge in self.edges
            if edge.source in visited and edge.target in visited
        ]
        
        return subgraph_nodes, subgraph_edges
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """查找循环依赖"""
        # 构建模块依赖图
        module_deps = {mp: set() for mp in self.module_nodes.keys()}
        
        for edge in self.edges:
            if edge.type == EdgeType.IMPORTS:
                source_module = edge.source.replace('module:', '')
                target_module = edge.target.replace('module:', '')
                if source_module in module_deps:
                    module_deps[source_module].add(target_module)
        
        # DFS查找循环
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in module_deps.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for node in module_deps:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def calculate_centrality(self) -> Dict[str, float]:
        """计算节点中心性（简化版PageRank）"""
        # 构建邻接表
        adjacency = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge.target)
        
        # 初始化
        centrality = {node_id: 1.0 for node_id in self.nodes}
        damping = 0.85
        iterations = 100
        
        for _ in range(iterations):
            new_centrality = {}
            for node_id in self.nodes:
                rank = (1 - damping)
                for other_id, targets in adjacency.items():
                    if node_id in targets:
                        rank += damping * centrality[other_id] / len(targets) if targets else 0
                new_centrality[node_id] = rank
            centrality = new_centrality
        
        # 归一化
        max_rank = max(centrality.values()) if centrality else 1
        return {k: v / max_rank for k, v in centrality.items()}
    
    def export_graph_json(self, output_path: str):
        """导出图谱为JSON格式"""
        data = {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges],
            'metadata': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'node_types': {},
                'edge_types': {}
            }
        }
        
        # 统计节点类型
        for node in self.nodes.values():
            type_name = node.type.value
            data['metadata']['node_types'][type_name] = data['metadata']['node_types'].get(type_name, 0) + 1
        
        # 统计边类型
        for edge in self.edges:
            type_name = edge.type.value
            data['metadata']['edge_types'][type_name] = data['metadata']['edge_types'].get(type_name, 0) + 1
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_graphml(self, output_path: str):
        """导出为GraphML格式（用于Gephi等工具）"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="label" for="node" attr.name="label" attr.type="string"/>
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <key id="file_path" for="node" attr.name="file_path" attr.type="string"/>
  <key id="edge_type" for="edge" attr.name="edge_type" attr.type="string"/>
  <graph id="G" edgedefault="directed">
'''
        
        # 添加节点
        for node in self.nodes.values():
            xml_content += f'    <node id="{node.id}">\n'
            xml_content += f'      <data key="label">{self._escape_xml(node.label)}</data>\n'
            xml_content += f'      <data key="type">{node.type.value}</data>\n'
            xml_content += f'      <data key="file_path">{self._escape_xml(node.file_path)}</data>\n'
            xml_content += '    </node>\n'
        
        # 添加边
        for i, edge in enumerate(self.edges):
            xml_content += f'    <edge id="e{i}" source="{edge.source}" target="{edge.target}">\n'
            xml_content += f'      <data key="edge_type">{edge.type.value}</data>\n'
            xml_content += '    </edge>\n'
        
        xml_content += '  </graph>\n</graphml>'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return output_path
    
    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
