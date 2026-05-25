"""
影响分析器 - 分析代码变更的影响范围
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChangeImpact:
    """变更影响"""
    changed_file: str
    changed_function: Optional[str]
    affected_files: Set[str] = field(default_factory=set)
    affected_functions: Set[str] = field(default_factory=set)
    risk_score: float = 0.0
    impact_chain: List[List[str]] = field(default_factory=list)


class ImpactAnalyzer:
    """代码变更影响分析器"""
    
    def __init__(self, nodes: Dict[str, Any], edges: List[Any]):
        self.nodes = nodes
        self.edges = edges
        self._build_dependency_graph()
    
    def _build_dependency_graph(self):
        """构建依赖图"""
        # 文件依赖图
        self.file_deps: Dict[str, Set[str]] = {}
        # 函数调用图
        self.func_calls: Dict[str, Set[str]] = {}
        # 反向依赖（谁依赖我）
        self.reverse_deps: Dict[str, Set[str]] = {}
        
        # 初始化
        for node in self.nodes.values():
            if node.type.value == 'module':
                self.file_deps[node.file_path] = set()
                self.reverse_deps[node.file_path] = set()
            elif node.type.value in ('function', 'method'):
                self.func_calls[node.id] = set()
                self.reverse_deps[node.id] = set()
        
        # 构建边关系
        for edge in self.edges:
            if edge.type.value == 'imports':
                source_file = edge.source.replace('module:', '')
                target_file = edge.target.replace('module:', '')
                if source_file in self.file_deps:
                    self.file_deps[source_file].add(target_file)
                if target_file in self.reverse_deps:
                    self.reverse_deps[target_file].add(source_file)
            
            elif edge.type.value == 'calls':
                if edge.source in self.func_calls:
                    self.func_calls[edge.source].add(edge.target)
                if edge.target in self.reverse_deps:
                    self.reverse_deps[edge.target].add(edge.source)
            
            elif edge.type.value == 'contains':
                # 记录函数/方法属于哪个文件
                if edge.target in self.nodes:
                    target_node = self.nodes[edge.target]
                    if hasattr(target_node, 'file_path'):
                        target_node.file_path = edge.source.replace('module:', '')
    
    def analyze_change_impact(
        self,
        changed_files: List[str],
        changed_functions: Optional[List[str]] = None
    ) -> List[ChangeImpact]:
        """分析变更影响范围"""
        impacts = []
        changed_functions = changed_functions or []
        
        for file_path in changed_files:
            impact = ChangeImpact(
                changed_file=file_path,
                changed_function=None
            )
            
            # 分析文件级影响
            affected = self._get_affected_files(file_path, depth=3)
            impact.affected_files = affected
            
            # 分析函数级影响
            for func_id in changed_functions:
                if func_id.startswith(file_path) or file_path in func_id:
                    func_affected = self._get_affected_functions(func_id, depth=3)
                    impact.affected_functions.update(func_affected)
                    impact.changed_function = func_id
            
            # 计算风险分数
            impact.risk_score = self._calculate_risk_score(impact)
            
            # 生成影响链
            impact.impact_chain = self._generate_impact_chain(file_path)
            
            impacts.append(impact)
        
        return impacts
    
    def _get_affected_files(self, file_path: str, depth: int = 3) -> Set[str]:
        """获取受影响的文件"""
        affected = set()
        current_level = {file_path}
        
        for _ in range(depth):
            next_level = set()
            for f in current_level:
                if f in self.reverse_deps:
                    for dep in self.reverse_deps[f]:
                        if dep != file_path:
                            affected.add(dep)
                            next_level.add(dep)
            current_level = next_level
        
        return affected
    
    def _get_affected_functions(self, func_id: str, depth: int = 3) -> Set[str]:
        """获取受影响的函数"""
        affected = set()
        current_level = {func_id}
        
        for _ in range(depth):
            next_level = set()
            for f in current_level:
                if f in self.reverse_deps:
                    for dep in self.reverse_deps[f]:
                        if dep != func_id:
                            affected.add(dep)
                            next_level.add(dep)
            current_level = next_level
        
        return affected
    
    def _calculate_risk_score(self, impact: ChangeImpact) -> float:
        """计算风险分数（0-100）"""
        score = 0.0
        
        # 基于受影响文件数量
        file_factor = min(len(impact.affected_files) * 5, 30)
        score += file_factor
        
        # 基于受影响函数数量
        func_factor = min(len(impact.affected_functions) * 2, 30)
        score += func_factor
        
        # 基于影响链长度
        chain_factor = min(len(impact.impact_chain) * 5, 20)
        score += chain_factor
        
        # 检查是否有循环依赖
        if self._has_circular_dependency(impact.changed_file):
            score += 20
        
        return min(score, 100)
    
    def _has_circular_dependency(self, file_path: str) -> bool:
        """检查是否存在循环依赖"""
        visited = set()
        
        def dfs(current, path):
            if current in path:
                return True
            if current in visited:
                return False
            
            visited.add(current)
            path.add(current)
            
            for dep in self.file_deps.get(current, []):
                if dfs(dep, path):
                    return True
            
            path.remove(current)
            return False
        
        return dfs(file_path, set())
    
    def _generate_impact_chain(self, file_path: str, max_depth: int = 5) -> List[List[str]]:
        """生成影响链"""
        chains = []
        
        def dfs(current, path, depth):
            if depth > max_depth:
                return
            
            if current in self.reverse_deps and self.reverse_deps[current]:
                for dep in self.reverse_deps[current]:
                    if dep not in path:  # 避免循环
                        new_path = path + [dep]
                        chains.append(new_path)
                        dfs(dep, new_path, depth + 1)
        
        dfs(file_path, [file_path], 1)
        
        # 去重并排序
        unique_chains = []
        seen = set()
        for chain in chains:
            chain_tuple = tuple(chain)
            if chain_tuple not in seen:
                seen.add(chain_tuple)
                unique_chains.append(chain)
        
        return sorted(unique_chains, key=len, reverse=True)[:10]  # 只保留前10条最长的链
    
    def find_hotspots(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """查找代码热点（高依赖区域）"""
        hotspots = []
        
        for node in self.nodes.values():
            # 计算入度（被依赖次数）
            in_degree = len(self.reverse_deps.get(node.id, set()))
            
            # 计算出度（依赖其他数量）
            if node.type.value == 'module':
                out_degree = len(self.file_deps.get(node.file_path, set()))
            else:
                out_degree = len(self.func_calls.get(node.id, set()))
            
            # 热度分数
            hotspot_score = in_degree * 2 + out_degree
            
            if in_degree > 0 or out_degree > 0:
                hotspots.append({
                    'id': node.id,
                    'label': node.label,
                    'type': node.type.value,
                    'file_path': node.file_path,
                    'in_degree': in_degree,
                    'out_degree': out_degree,
                    'hotspot_score': hotspot_score
                })
        
        # 按热度排序
        hotspots.sort(key=lambda x: x['hotspot_score'], reverse=True)
        return hotspots[:top_n]
    
    def find_dead_code(self) -> List[Dict[str, Any]]:
        """查找可能的死代码（未被调用的函数/方法）"""
        dead_code = []
        
        for node in self.nodes.values():
            if node.type.value in ('function', 'method'):
                # 检查是否被调用
                in_degree = len(self.reverse_deps.get(node.id, set()))
                
                # 排除特殊方法
                is_special = (
                    node.label.startswith('_') or  # 私有方法
                    node.label in ('__init__', '__main__', 'main') or  # 特殊方法
                    'test' in node.label.lower()  # 测试方法
                )
                
                if in_degree == 0 and not is_special:
                    dead_code.append({
                        'id': node.id,
                        'label': node.label,
                        'file_path': node.file_path,
                        'line': node.properties.get('line_start', 0)
                    })
        
        return dead_code
    
    def calculate_modularity(self) -> Dict[str, Any]:
        """计算项目模块化程度"""
        total_files = len([n for n in self.nodes.values() if n.type.value == 'module'])
        
        if total_files == 0:
            return {'score': 0, 'issues': []}
        
        issues = []
        
        # 检查高度耦合的文件
        for node in self.nodes.values():
            if node.type.value == 'module':
                deps = self.file_deps.get(node.file_path, set())
                reverse = self.reverse_deps.get(node.file_path, set())
                
                total_deps = len(deps) + len(reverse)
                
                if total_deps > 10:
                    issues.append({
                        'file': node.file_path,
                        'issue': '高度耦合',
                        'details': f'依赖了 {len(deps)} 个文件，被 {len(reverse)} 个文件依赖',
                        'severity': 'high' if total_deps > 20 else 'medium'
                    })
        
        # 计算模块化分数
        if issues:
            score = max(0, 100 - len(issues) * 10)
        else:
            score = 100
        
        return {
            'score': score,
            'total_files': total_files,
            'coupled_files': len([i for i in issues if i['severity'] == 'high']),
            'issues': issues
        }
    
    def generate_impact_report(self, impacts: List[ChangeImpact]) -> str:
        """生成影响分析报告"""
        report = "# 📊 代码变更影响分析报告\n\n"
        
        # 总体概览
        total_affected_files = set()
        total_affected_funcs = set()
        max_risk = 0
        
        for impact in impacts:
            total_affected_files.update(impact.affected_files)
            total_affected_funcs.update(impact.affected_functions)
            max_risk = max(max_risk, impact.risk_score)
        
        report += "## 📈 总体概览\n\n"
        report += f"- **变更文件数**: {len(impacts)}\n"
        report += f"- **受影响文件数**: {len(total_affected_files)}\n"
        report += f"- **受影响函数数**: {len(total_affected_funcs)}\n"
        report += f"- **最高风险分数**: {max_risk:.1f}/100\n\n"
        
        # 风险等级
        if max_risk >= 70:
            report += "⚠️ **高风险**: 建议进行全面的回归测试\n\n"
        elif max_risk >= 40:
            report += "⚡ **中等风险**: 建议进行针对性测试\n\n"
        else:
            report += "✅ **低风险**: 变更影响范围有限\n\n"
        
        # 详细影响分析
        report += "## 📋 详细影响分析\n\n"
        
        for i, impact in enumerate(impacts, 1):
            report += f"### {i}. {impact.changed_file}\n\n"
            
            if impact.changed_function:
                report += f"**变更函数**: `{impact.changed_function}`\n\n"
            
            report += f"**风险分数**: {impact.risk_score:.1f}/100\n\n"
            
            if impact.affected_files:
                report += "**受影响文件**:\n\n"
                for f in sorted(impact.affected_files)[:10]:
                    report += f"- `{f}`\n"
                if len(impact.affected_files) > 10:
                    report += f"- ... 还有 {len(impact.affected_files) - 10} 个文件\n"
                report += "\n"
            
            if impact.impact_chain:
                report += "**影响链**:\n\n"
                for chain in impact.impact_chain[:5]:
                    report += f"- {' → '.join(chain)}\n"
                report += "\n"
        
        # 建议
        report += "## 💡 建议\n\n"
        
        if max_risk >= 70:
            report += "1. 进行全面的单元测试和集成测试\n"
            report += "2. 考虑分阶段发布变更\n"
            report += "3. 增加代码审查的严格程度\n"
        elif max_risk >= 40:
            report += "1. 针对受影响模块进行重点测试\n"
            report += "2. 验证相关功能的兼容性\n"
        else:
            report += "1. 进行常规的单元测试\n"
            report += "2. 验证变更功能本身\n"
        
        return report
