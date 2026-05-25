"""
命令行接口 - CodeMind-Graph CLI
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from .analyzer import CodeAnalyzer
from .graph_builder import GraphBuilder
from .visualizer import GraphVisualizer
from .exporter import GraphExporter
from .impact_analyzer import ImpactAnalyzer


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='codemind-graph',
        description='🔍 CodeMind-Graph: 代码知识图谱可视化与分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 分析项目并生成交互式HTML
  codemind-graph analyze ./my-project --output ./output
  
  # 分析变更影响
  codemind-graph impact ./my-project --files src/main.py,src/utils.py
  
  # 查找代码热点
  codemind-graph hotspots ./my-project
  
  # 导出为特定格式
  codemind-graph export ./my-project --format dot --output graph.dot
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='分析代码库并生成知识图谱'
    )
    analyze_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        default='./codemind-output',
        help='输出目录 (默认: ./codemind-output)'
    )
    analyze_parser.add_argument(
        '--formats',
        default='html,json,dot',
        help='输出格式，逗号分隔 (默认: html,json,dot)'
    )
    analyze_parser.add_argument(
        '--exclude',
        default='',
        help='排除模式，逗号分隔 (例如: test,docs)'
    )
    
    # impact 命令
    impact_parser = subparsers.add_parser(
        'impact',
        help='分析代码变更的影响范围'
    )
    impact_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    impact_parser.add_argument(
        '--files',
        required=True,
        help='变更的文件，逗号分隔'
    )
    impact_parser.add_argument(
        '--functions',
        default='',
        help='变更的函数，逗号分隔'
    )
    impact_parser.add_argument(
        '-o', '--output',
        default='./impact-report.md',
        help='输出报告路径'
    )
    
    # hotspots 命令
    hotspots_parser = subparsers.add_parser(
        'hotspots',
        help='查找代码热点（高依赖区域）'
    )
    hotspots_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    hotspots_parser.add_argument(
        '-n', '--top',
        type=int,
        default=10,
        help='显示前N个热点 (默认: 10)'
    )
    hotspots_parser.add_argument(
        '-o', '--output',
        default='./hotspots.json',
        help='输出文件路径'
    )
    
    # deadcode 命令
    deadcode_parser = subparsers.add_parser(
        'deadcode',
        help='查找可能的死代码'
    )
    deadcode_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    deadcode_parser.add_argument(
        '-o', '--output',
        default='./deadcode.json',
        help='输出文件路径'
    )
    
    # modularity 命令
    modularity_parser = subparsers.add_parser(
        'modularity',
        help='分析项目模块化程度'
    )
    modularity_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    modularity_parser.add_argument(
        '-o', '--output',
        default='./modularity-report.md',
        help='输出报告路径'
    )
    
    # export 命令
    export_parser = subparsers.add_parser(
        'export',
        help='导出图谱为特定格式'
    )
    export_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    export_parser.add_argument(
        '--format',
        choices=['json', 'graphml', 'dot', 'csv', 'md'],
        required=True,
        help='导出格式'
    )
    export_parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出文件路径'
    )
    
    # stats 命令
    stats_parser = subparsers.add_parser(
        'stats',
        help='显示项目统计信息'
    )
    stats_parser.add_argument(
        'project_path',
        help='项目路径'
    )
    
    return parser


def analyze_command(args) -> int:
    """执行分析命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    
    # 添加排除模式
    if args.exclude:
        for pattern in args.exclude.split(','):
            analyzer.exclude_patterns.append(pattern.strip())
    
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    print(f"✅ 分析了 {len(modules)} 个文件")
    
    # 获取统计信息
    stats = analyzer.get_statistics()
    print(f"📊 统计: {stats['total_functions']} 个函数, {stats['total_classes']} 个类")
    
    # 构建图谱
    print("🏗️  正在构建知识图谱...")
    builder = GraphBuilder()
    nodes, edges = builder.build_from_modules({
        k: {
            'file_path': v.file_path,
            'language': v.language,
            'imports': v.imports,
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
                for f in v.functions
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
                for c in v.classes
            ]
        }
        for k, v in modules.items()
    })
    
    print(f"✅ 图谱构建完成: {len(nodes)} 个节点, {len(edges)} 条边")
    
    # 导出各种格式
    formats = args.formats.split(',')
    exporter = GraphExporter(nodes, edges)
    visualizer = GraphVisualizer(nodes, edges)
    
    for fmt in formats:
        fmt = fmt.strip().lower()
        
        if fmt == 'json':
            path = output_dir / 'graph.json'
            exporter.export_json(str(path))
            print(f"📄 导出 JSON: {path}")
        
        elif fmt == 'graphml':
            path = output_dir / 'graph.graphml'
            exporter.export_graphml(str(path))
            print(f"📄 导出 GraphML: {path}")
        
        elif fmt == 'dot':
            path = output_dir / 'graph.dot'
            exporter.export_dot(str(path))
            print(f"📄 导出 DOT: {path}")
        
        elif fmt == 'csv':
            nodes_path = output_dir / 'nodes.csv'
            edges_path = output_dir / 'edges.csv'
            exporter.export_csv(str(nodes_path), str(edges_path))
            print(f"📄 导出 CSV: {nodes_path}, {edges_path}")
        
        elif fmt == 'md':
            path = output_dir / 'graph.md'
            exporter.export_markdown(str(path), project_path.name)
            print(f"📄 导出 Markdown: {path}")
        
        elif fmt == 'html':
            path = output_dir / 'graph.html'
            html_content = visualizer.generate_html_interactive(project_path.name)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📄 导出 HTML: {path}")
        
        elif fmt == 'svg':
            path = output_dir / 'graph.svg'
            result = visualizer.export_svg(str(path))
            if result:
                print(f"📄 导出 SVG: {path}")
        
        elif fmt == 'png':
            path = output_dir / 'graph.png'
            result = visualizer.export_png(str(path))
            if result:
                print(f"📄 导出 PNG: {path}")
    
    # 保存分析数据
    analysis_path = output_dir / 'analysis.json'
    analyzer.export_json(str(analysis_path))
    print(f"📄 保存分析数据: {analysis_path}")
    
    print(f"\n✨ 分析完成！输出目录: {output_dir}")
    print(f"🌐 打开 {output_dir}/graph.html 查看交互式图谱")
    
    return 0


def impact_command(args) -> int:
    """执行影响分析命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    # 构建图谱
    builder = GraphBuilder()
    nodes, edges = builder.build_from_modules({
        k: {
            'file_path': v.file_path,
            'language': v.language,
            'imports': v.imports,
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
                for f in v.functions
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
                for c in v.classes
            ]
        }
        for k, v in modules.items()
    })
    
    # 分析影响
    impact_analyzer = ImpactAnalyzer(nodes, edges)
    
    changed_files = [f.strip() for f in args.files.split(',')]
    changed_functions = [f.strip() for f in args.functions.split(',')] if args.functions else []
    
    print(f"📁 变更文件: {', '.join(changed_files)}")
    
    impacts = impact_analyzer.analyze_change_impact(changed_files, changed_functions)
    
    # 生成报告
    report = impact_analyzer.generate_impact_report(impacts)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 影响分析报告已保存: {args.output}")
    
    # 显示简要信息
    max_risk = max((i.risk_score for i in impacts), default=0)
    print(f"⚠️  最高风险分数: {max_risk:.1f}/100")
    
    return 0


def hotspots_command(args) -> int:
    """执行热点分析命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    # 构建图谱
    builder = GraphBuilder()
    nodes, edges = builder.build_from_modules({
        k: {
            'file_path': v.file_path,
            'language': v.language,
            'imports': v.imports,
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
                for f in v.functions
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
                for c in v.classes
            ]
        }
        for k, v in modules.items()
    })
    
    # 查找热点
    impact_analyzer = ImpactAnalyzer(nodes, edges)
    hotspots = impact_analyzer.find_hotspots(args.top)
    
    import json as json_module
    with open(args.output, 'w', encoding='utf-8') as f:
        json_module.dump(hotspots, f, indent=2, ensure_ascii=False)
    
    print(f"\n🔥 代码热点 (Top {args.top}):")
    print("-" * 60)
    for i, h in enumerate(hotspots, 1):
        print(f"{i}. {h['label']} ({h['type']})")
        print(f"   文件: {h['file_path']}")
        print(f"   被依赖: {h['in_degree']} | 依赖其他: {h['out_degree']} | 热度: {h['hotspot_score']}")
        print()
    
    print(f"✅ 热点数据已保存: {args.output}")
    
    return 0


def deadcode_command(args) -> int:
    """执行死代码检测命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    # 构建图谱
    builder = GraphBuilder()
    nodes, edges = builder.build_from_modules({
        k: {
            'file_path': v.file_path,
            'language': v.language,
            'imports': v.imports,
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
                for f in v.functions
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
                for c in v.classes
            ]
        }
        for k, v in modules.items()
    })
    
    # 查找死代码
    impact_analyzer = ImpactAnalyzer(nodes, edges)
    dead_code = impact_analyzer.find_dead_code()
    
    import json as json_module
    with open(args.output, 'w', encoding='utf-8') as f:
        json_module.dump(dead_code, f, indent=2, ensure_ascii=False)
    
    if dead_code:
        print(f"\n⚠️  发现 {len(dead_code)} 个可能的死代码:")
        print("-" * 60)
        for item in dead_code:
            print(f"- {item['label']} in {item['file_path']}:{item['line']}")
    else:
        print("\n✅ 未发现明显的死代码")
    
    print(f"\n✅ 死代码数据已保存: {args.output}")
    
    return 0


def modularity_command(args) -> int:
    """执行模块化分析命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    # 构建图谱
    builder = GraphBuilder()
    nodes, edges = builder.build_from_modules({
        k: {
            'file_path': v.file_path,
            'language': v.language,
            'imports': v.imports,
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
                for f in v.functions
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
                for c in v.classes
            ]
        }
        for k, v in modules.items()
    })
    
    # 分析模块化
    impact_analyzer = ImpactAnalyzer(nodes, edges)
    modularity = impact_analyzer.calculate_modularity()
    
    # 生成报告
    report = f"""# 📦 项目模块化分析报告

## 📊 总体评分

**模块化分数**: {modularity['score']}/100

"""
    
    if modularity['score'] >= 80:
        report += "✅ **优秀**: 项目结构良好，模块间耦合度低\n\n"
    elif modularity['score'] >= 60:
        report += "⚡ **良好**: 项目结构基本合理，有少量改进空间\n\n"
    else:
        report += "⚠️ **需改进**: 项目存在较多耦合问题，建议重构\n\n"
    
    report += f"""## 📈 统计信息

- **总文件数**: {modularity['total_files']}
- **高度耦合文件数**: {modularity['coupled_files']}

"""
    
    if modularity['issues']:
        report += "## ⚠️ 耦合问题\n\n"
        for issue in modularity['issues']:
            severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡"
            report += f"{severity_emoji} **{issue['file']}**\n"
            report += f"   - 问题: {issue['issue']}\n"
            report += f"   - 详情: {issue['details']}\n\n"
    
    report += """## 💡 改进建议

1. **降低模块耦合**: 减少文件间的直接依赖
2. **提取公共模块**: 将共享功能抽取到独立模块
3. **使用接口隔离**: 通过接口/抽象类降低依赖
4. **分层架构**: 明确分层，避免跨层调用
"""
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📦 模块化分数: {modularity['score']}/100")
    print(f"📁 总文件数: {modularity['total_files']}")
    print(f"⚠️  耦合问题: {len(modularity['issues'])}")
    print(f"\n✅ 报告已保存: {args.output}")
    
    return 0


def export_command(args) -> int:
    """执行导出命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    # 构建图谱
    builder = GraphBuilder()
    nodes, edges = builder.build_from_modules({
        k: {
            'file_path': v.file_path,
            'language': v.language,
            'imports': v.imports,
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
                for f in v.functions
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
                for c in v.classes
            ]
        }
        for k, v in modules.items()
    })
    
    # 导出
    exporter = GraphExporter(nodes, edges)
    
    if args.format == 'json':
        exporter.export_json(args.output)
    elif args.format == 'graphml':
        exporter.export_graphml(args.output)
    elif args.format == 'dot':
        exporter.export_dot(args.output)
    elif args.format == 'csv':
        base = args.output.replace('.csv', '')
        exporter.export_csv(f"{base}-nodes.csv", f"{base}-edges.csv")
    elif args.format == 'md':
        exporter.export_markdown(args.output, project_path.name)
    
    print(f"✅ 导出完成: {args.output}")
    
    return 0


def stats_command(args) -> int:
    """执行统计命令"""
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"❌ 错误: 项目路径不存在: {project_path}")
        return 1
    
    print(f"🔍 正在分析项目: {project_path}")
    
    # 分析代码
    analyzer = CodeAnalyzer(project_path)
    modules = analyzer.analyze_project()
    
    if not modules:
        print("⚠️  未找到可分析的代码文件")
        return 1
    
    stats = analyzer.get_statistics()
    
    print("\n" + "=" * 50)
    print("📊 项目统计信息")
    print("=" * 50)
    print(f"📁 文件总数: {stats['total_files']}")
    print(f"🔧 函数总数: {stats['total_functions']}")
    print(f"📦 类总数: {stats['total_classes']}")
    print()
    print("🌐 语言分布:")
    for lang, count in stats['languages'].items():
        print(f"   - {lang}: {count} 个文件")
    print()
    print("📈 复杂度分析:")
    print(f"   - 平均复杂度: {stats['complexity']['average']}")
    print(f"   - 最高复杂度: {stats['complexity']['max']}")
    print(f"   - 高复杂度函数: {len(stats['complexity']['high_complexity_functions'])} 个")
    
    if stats['complexity']['high_complexity_functions']:
        print("\n⚠️  高复杂度函数列表:")
        for func in stats['complexity']['high_complexity_functions'][:5]:
            print(f"   - {func['name']} ({func['file']}): {func['complexity']}")
    
    return 0


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'analyze': analyze_command,
        'impact': impact_command,
        'hotspots': hotspots_command,
        'deadcode': deadcode_command,
        'modularity': modularity_command,
        'export': export_command,
        'stats': stats_command,
    }
    
    command_func = commands.get(args.command)
    if command_func:
        return command_func(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
