"""
图谱可视化器 - 生成可视化图表
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class GraphVisualizer:
    """知识图谱可视化器"""
    
    # 颜色方案
    COLORS = {
        'module': '#4A90D9',      # 蓝色
        'function': '#50C878',    # 绿色
        'class': '#FFD700',       # 金色
        'method': '#FF6B6B',      # 红色
        'import': '#9B59B6',      # 紫色
        'package': '#1ABC9C',     # 青色
    }
    
    EDGE_COLORS = {
        'contains': '#95A5A6',    # 灰色
        'calls': '#E74C3C',       # 红色
        'imports': '#3498DB',     # 蓝色
        'inherits': '#F39C12',    # 橙色
        'depends': '#9B59B6',     # 紫色
    }
    
    def __init__(self, nodes: Dict[str, Any], edges: List[Any]):
        self.nodes = nodes
        self.edges = edges
    
    def generate_dot(self, title: str = "Code Knowledge Graph") -> str:
        """生成Graphviz DOT格式"""
        dot = f'digraph "{title}" {{\n'
        dot += '  rankdir=TB;\n'
        dot += '  node [shape=box, style="rounded,filled", fontname="Arial"];\n'
        dot += '  edge [fontname="Arial", fontsize=10];\n\n'
        
        # 添加节点
        for node_id, node in self.nodes.items():
            color = self.COLORS.get(node.type.value, '#CCCCCC')
            label = node.label
            
            # 添加额外信息到标签
            if node.type.value == 'function' and node.properties.get('complexity', 1) > 5:
                label += f"\\n[复杂度:{node.properties['complexity']}]"
            
            escaped_id = self._escape_id(node_id)
            escaped_label = label.replace('"', '\\"')
            
            dot += f'  "{escaped_id}" [label="{escaped_label}", fillcolor="{color}"];\n'
        
        dot += '\n'
        
        # 添加边
        for edge in self.edges:
            color = self.EDGE_COLORS.get(edge.type.value, '#CCCCCC')
            source_id = self._escape_id(edge.source)
            target_id = self._escape_id(edge.target)
            
            dot += f'  "{source_id}" -> "{target_id}" [color="{color}"];\n'
        
        dot += '}\n'
        return dot
    
    def generate_mermaid(self) -> str:
        """生成Mermaid流程图格式"""
        mermaid = "```mermaid\ngraph TD\n"
        
        # 添加节点定义
        for node_id, node in self.nodes.items():
            short_id = node_id.replace(':', '_').replace('/', '_')
            label = node.label
            
            # 根据类型选择形状
            if node.type.value == 'module':
                mermaid += f"    {short_id}[{label}]\n"
            elif node.type.value == 'class':
                mermaid += f"    {short_id}{{{label}}}\n"
            else:
                mermaid += f"    {short_id}({label})\n"
        
        mermaid += "\n"
        
        # 添加边
        for edge in self.edges:
            source_short = edge.source.replace(':', '_').replace('/', '_')
            target_short = edge.target.replace(':', '_').replace('/', '_')
            edge_style = "-->"
            
            if edge.type.value == 'inherits':
                edge_style = "-.->"
            elif edge.type.value == 'contains':
                edge_style = "==>"
            
            mermaid += f"    {source_short} {edge_style} {target_short}\n"
        
        mermaid += "```\n"
        return mermaid
    
    def generate_html_interactive(self, title: str = "Code Knowledge Graph") -> str:
        """生成交互式HTML可视化"""
        # 准备节点和边数据
        nodes_data = []
        for node_id, node in self.nodes.items():
            nodes_data.append({
                'id': node_id,
                'label': node.label,
                'type': node.type.value,
                'file_path': node.file_path,
                'color': self.COLORS.get(node.type.value, '#CCCCCC'),
                'properties': node.properties
            })
        
        edges_data = []
        for edge in self.edges:
            edges_data.append({
                'source': edge.source,
                'target': edge.target,
                'type': edge.type.value,
                'color': self.EDGE_COLORS.get(edge.type.value, '#CCCCCC')
            })
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            overflow: hidden;
        }}
        
        #header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            padding: 0 20px;
            z-index: 1000;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        #header h1 {{
            font-size: 18px;
            margin-right: 20px;
        }}
        
        #search {{
            flex: 1;
            max-width: 300px;
        }}
        
        #search input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            outline: none;
        }}
        
        #search input::placeholder {{
            color: rgba(255,255,255,0.5);
        }}
        
        #legend {{
            position: fixed;
            top: 80px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            z-index: 100;
        }}
        
        #legend h3 {{
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 12px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            margin-right: 8px;
        }}
        
        #info-panel {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 350px;
            max-height: 400px;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 20px;
            overflow-y: auto;
            z-index: 100;
            display: none;
        }}
        
        #info-panel.active {{
            display: block;
        }}
        
        #info-panel h3 {{
            font-size: 16px;
            margin-bottom: 10px;
            color: #4A90D9;
        }}
        
        #info-panel .info-row {{
            margin: 8px 0;
            font-size: 13px;
        }}
        
        #info-panel .info-label {{
            color: rgba(255,255,255,0.6);
        }}
        
        #graph {{
            width: 100vw;
            height: 100vh;
            padding-top: 60px;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .node:hover {{
            filter: brightness(1.2);
        }}
        
        .node-label {{
            font-size: 11px;
            fill: #fff;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }}
        
        .link {{
            stroke-opacity: 0.6;
            transition: all 0.3s ease;
        }}
        
        .link:hover {{
            stroke-opacity: 1;
            stroke-width: 3px;
        }}
        
        #controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 100;
        }}
        
        .btn {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background: rgba(0,0,0,0.8);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: all 0.2s;
        }}
        
        .btn:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        #stats {{
            position: fixed;
            top: 80px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            z-index: 100;
            font-size: 12px;
        }}
        
        #stats div {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🔍 {title}</h1>
        <div id="search">
            <input type="text" id="searchInput" placeholder="搜索节点..." />
        </div>
    </div>
    
    <div id="stats">
        <div><strong>📊 统计</strong></div>
        <div>节点: {len(self.nodes)}</div>
        <div>边: {len(self.edges)}</div>
    </div>
    
    <div id="legend">
        <h3>📌 图例</h3>
        <div class="legend-item">
            <div class="legend-color" style="background: {self.COLORS['module']}"></div>
            <span>模块</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {self.COLORS['class']}"></div>
            <span>类</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {self.COLORS['function']}"></div>
            <span>函数</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: {self.COLORS['method']}"></div>
            <span>方法</span>
        </div>
    </div>
    
    <div id="info-panel">
        <h3 id="info-title">节点信息</h3>
        <div id="info-content"></div>
    </div>
    
    <div id="controls">
        <button class="btn" onclick="zoomIn()" title="放大">+</button>
        <button class="btn" onclick="zoomOut()" title="缩小">-</button>
        <button class="btn" onclick="resetZoom()" title="重置">⟲</button>
    </div>
    
    <div id="graph"></div>
    
    <script>
        const nodesData = {nodes_data};
        const edgesData = {edges_data};
        
        const width = window.innerWidth;
        const height = window.innerHeight - 60;
        
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // 添加缩放行为
        const g = svg.append("g");
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // 创建力导向模拟
        const simulation = d3.forceSimulation(nodesData)
            .force("link", d3.forceLink(edgesData).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));
        
        // 绘制边
        const link = g.append("g")
            .selectAll("line")
            .data(edgesData)
            .enter()
            .append("line")
            .attr("class", "link")
            .attr("stroke", d => d.color)
            .attr("stroke-width", 1.5);
        
        // 绘制节点
        const node = g.append("g")
            .selectAll("g")
            .data(nodesData)
            .enter()
            .append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // 节点圆形
        node.append("circle")
            .attr("r", d => d.type === 'module' ? 20 : 15)
            .attr("fill", d => d.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);
        
        // 节点标签
        node.append("text")
            .attr("class", "node-label")
            .attr("dx", 0)
            .attr("dy", d => d.type === 'module' ? 35 : 28)
            .attr("text-anchor", "middle")
            .text(d => d.label.length > 15 ? d.label.substring(0, 15) + '...' : d.label);
        
        // 节点点击事件
        node.on("click", (event, d) => {{
            showInfo(d);
        }});
        
        // 更新位置
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        // 拖拽函数
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // 显示节点信息
        function showInfo(d) {{
            const panel = document.getElementById('info-panel');
            const title = document.getElementById('info-title');
            const content = document.getElementById('info-content');
            
            title.textContent = d.label;
            
            let html = `
                <div class="info-row"><span class="info-label">类型:</span> ${{d.type}}</div>
                <div class="info-row"><span class="info-label">文件:</span> ${{d.file_path}}</div>
            `;
            
            if (d.properties.complexity) {{
                html += `<div class="info-row"><span class="info-label">复杂度:</span> ${{d.properties.complexity}}</div>`;
            }}
            
            if (d.properties.parameters) {{
                html += `<div class="info-row"><span class="info-label">参数:</span> ${{d.properties.parameters.join(', ') || '无'}}</div>`;
            }}
            
            if (d.properties.return_type) {{
                html += `<div class="info-row"><span class="info-label">返回类型:</span> ${{d.properties.return_type}}</div>`;
            }}
            
            if (d.properties.docstring) {{
                html += `<div class="info-row"><span class="info-label">文档:</span> ${{d.properties.docstring.substring(0, 100)}}...</div>`;
            }}
            
            content.innerHTML = html;
            panel.classList.add('active');
        }}
        
        // 缩放控制
        function zoomIn() {{
            svg.transition().call(zoom.scaleBy, 1.3);
        }}
        
        function zoomOut() {{
            svg.transition().call(zoom.scaleBy, 0.7);
        }}
        
        function resetZoom() {{
            svg.transition().call(zoom.transform, d3.zoomIdentity);
        }}
        
        // 搜索功能
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const term = e.target.value.toLowerCase();
            
            node.style('opacity', d => {{
                if (!term) return 1;
                return d.label.toLowerCase().includes(term) ? 1 : 0.2;
            }});
            
            link.style('opacity', d => {{
                if (!term) return 0.6;
                const sourceMatch = d.source.label.toLowerCase().includes(term);
                const targetMatch = d.target.label.toLowerCase().includes(term);
                return (sourceMatch || targetMatch) ? 1 : 0.1;
            }});
        }});
        
        // 点击空白处关闭信息面板
        svg.on("click", (event) => {{
            if (event.target.tagName === 'svg') {{
                document.getElementById('info-panel').classList.remove('active');
            }}
        }});
    </script>
</body>
</html>'''
        
        # 替换数据
        import json
        html = html.replace('{nodes_data}', json.dumps(nodes_data))
        html = html.replace('{edges_data}', json.dumps(edges_data))
        
        return html
    
    def _escape_id(self, node_id: str) -> str:
        """转义节点ID"""
        return node_id.replace('"', '\\"').replace('\n', '\\n')
    
    def export_svg(self, output_path: str) -> str:
        """导出为SVG（需要graphviz）"""
        try:
            import subprocess
            
            dot_content = self.generate_dot()
            
            # 使用dot命令生成SVG
            result = subprocess.run(
                ['dot', '-Tsvg'],
                input=dot_content,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                return output_path
            else:
                print(f"⚠️  Graphviz错误: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("⚠️  未找到Graphviz，请安装: apt-get install graphviz 或 brew install graphviz")
            return None
        except Exception as e:
            print(f"⚠️  导出SVG失败: {e}")
            return None
    
    def export_png(self, output_path: str, width: int = 1920, height: int = 1080) -> str:
        """导出为PNG（需要graphviz）"""
        try:
            import subprocess
            
            dot_content = self.generate_dot()
            
            result = subprocess.run(
                ['dot', '-Tpng', f'-Gsize={width/100},{height/100}', '-Gdpi=100'],
                input=dot_content,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                # 以二进制模式写入
                with open(output_path, 'wb') as f:
                    f.write(result.stdout.encode('latin-1') if isinstance(result.stdout, str) else result.stdout)
                return output_path
            else:
                print(f"⚠️  Graphviz错误: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("⚠️  未找到Graphviz，请安装: apt-get install graphviz 或 brew install graphviz")
            return None
        except Exception as e:
            print(f"⚠️  导出PNG失败: {e}")
            return None
