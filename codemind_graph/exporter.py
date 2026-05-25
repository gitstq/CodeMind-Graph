"""
图谱导出器 - 支持多种格式导出
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class GraphExporter:
    """知识图谱导出器"""
    
    def __init__(self, nodes: Dict[str, Any], edges: List[Any]):
        self.nodes = nodes
        self.edges = edges
    
    def export_json(self, output_path: str) -> str:
        """导出为JSON格式"""
        data = {
            'nodes': [
                {
                    'id': node.id,
                    'type': node.type.value,
                    'label': node.label,
                    'file_path': node.file_path,
                    'properties': node.properties
                }
                for node in self.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'type': edge.type.value,
                    'properties': edge.properties
                }
                for edge in self.edges
            ],
            'metadata': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_graphml(self, output_path: str) -> str:
        """导出为GraphML格式（用于Gephi、Cytoscape等）"""
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="label" for="node" attr.name="label" attr.type="string"/>
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <key id="file_path" for="node" attr.name="file_path" attr.type="string"/>
  <key id="edge_type" for="edge" attr.name="edge_type" attr.type="string"/>
  <graph id="G" edgedefault="directed">
'''
        
        # 添加节点
        for node in self.nodes.values():
            xml += f'    <node id="{self._escape_xml(node.id)}">\n'
            xml += f'      <data key="label">{self._escape_xml(node.label)}</data>\n'
            xml += f'      <data key="type">{node.type.value}</data>\n'
            xml += f'      <data key="file_path">{self._escape_xml(node.file_path)}</data>\n'
            xml += '    </node>\n'
        
        # 添加边
        for i, edge in enumerate(self.edges):
            xml += f'    <edge id="e{i}" source="{self._escape_xml(edge.source)}" target="{self._escape_xml(edge.target)}">\n'
            xml += f'      <data key="edge_type">{edge.type.value}</data>\n'
            xml += '    </edge>\n'
        
        xml += '  </graph>\n</graphml>'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml)
        
        return output_path
    
    def export_dot(self, output_path: str, title: str = "Code Knowledge Graph") -> str:
        """导出为DOT格式"""
        colors = {
            'module': '#4A90D9',
            'function': '#50C878',
            'class': '#FFD700',
            'method': '#FF6B6B',
            'import': '#9B59B6',
            'package': '#1ABC9C',
        }
        
        dot = f'digraph "{title}" {{\n'
        dot += '  rankdir=TB;\n'
        dot += '  node [shape=box, style="rounded,filled", fontname="Arial"];\n\n'
        
        # 添加节点
        for node in self.nodes.values():
            color = colors.get(node.type.value, '#CCCCCC')
            escaped_id = node.id.replace('"', '\\"')
            escaped_label = node.label.replace('"', '\\"')
            dot += f'  "{escaped_id}" [label="{escaped_label}", fillcolor="{color}"];\n'
        
        dot += '\n'
        
        # 添加边
        for edge in self.edges:
            source_id = edge.source.replace('"', '\\"')
            target_id = edge.target.replace('"', '\\"')
            dot += f'  "{source_id}" -> "{target_id}";\n'
        
        dot += '}\n'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dot)
        
        return output_path
    
    def export_csv(self, nodes_path: str, edges_path: str) -> tuple:
        """导出为CSV格式（节点和边分开）"""
        # 导出节点
        with open(nodes_path, 'w', encoding='utf-8') as f:
            f.write('id,type,label,file_path\n')
            for node in self.nodes.values():
                f.write(f'"{node.id}","{node.type.value}","{node.label}","{node.file_path}"\n')
        
        # 导出边
        with open(edges_path, 'w', encoding='utf-8') as f:
            f.write('source,target,type\n')
            for edge in self.edges:
                f.write(f'"{edge.source}","{edge.target}","{edge.type.value}"\n')
        
        return nodes_path, edges_path
    
    def export_markdown(self, output_path: str, project_name: str = "Project") -> str:
        """导出为Markdown文档"""
        md = f"# 📊 {project_name} - 代码知识图谱\n\n"
        
        # 统计信息
        md += "## 📈 统计概览\n\n"
        md += f"- **总节点数**: {len(self.nodes)}\n"
        md += f"- **总边数**: {len(self.edges)}\n\n"
        
        # 节点类型统计
        type_counts = {}
        for node in self.nodes.values():
            type_counts[node.type.value] = type_counts.get(node.type.value, 0) + 1
        
        md += "### 节点类型分布\n\n"
        md += "| 类型 | 数量 |\n"
        md += "|------|------|\n"
        for node_type, count in sorted(type_counts.items()):
            md += f"| {node_type} | {count} |\n"
        
        md += "\n## 📁 模块列表\n\n"
        
        # 按模块分组
        modules = {}
        for node in self.nodes.values():
            if node.file_path not in modules:
                modules[node.file_path] = {'functions': [], 'classes': []}
            
            if node.type.value == 'function':
                modules[node.file_path]['functions'].append(node)
            elif node.type.value == 'class':
                modules[node.file_path]['classes'].append(node)
        
        for file_path, items in sorted(modules.items()):
            md += f"### {file_path}\n\n"
            
            if items['classes']:
                md += "**类**:\n\n"
                for cls in items['classes']:
                    md += f"- `{cls.label}`"
                    if cls.properties.get('bases'):
                        md += f" (继承: {', '.join(cls.properties['bases'])})"
                    md += "\n"
                md += "\n"
            
            if items['functions']:
                md += "**函数**:\n\n"
                for func in items['functions']:
                    md += f"- `{func.label}()`"
                    if func.properties.get('complexity', 1) > 5:
                        md += f" ⚠️ 复杂度: {func.properties['complexity']}"
                    md += "\n"
                md += "\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return output_path
    
    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
