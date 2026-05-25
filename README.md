# 🔍 CodeMind-Graph

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version 1.0.0">
</p>

<p align="center">
  <b>代码知识图谱可视化与分析工具</b><br>
  将代码库转换为交互式知识图谱，让代码结构一目了然
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.zh-TW.md">繁體中文</a> |
  <a href="README.md">English</a>
</p>

---

## 🎉 项目介绍

**CodeMind-Graph** 是一款轻量级、零依赖的代码知识图谱生成工具。它能够自动分析你的代码库，提取函数、类、导入关系等元数据，并构建成可视化的知识图谱。

### 💡 灵感来源

本项目灵感来源于 GitHub Trending 上的 [Understand-Anything](https://github.com/Lum1104/Understand-Anything)，但我们采用了不同的技术路线：
- **纯 Python 实现** - 无需复杂的 TypeScript 构建流程
- **零外部依赖** - 仅使用 Python 标准库，开箱即用
- **本地离线运行** - 无需 AI 平台插件，保护代码隐私
- **轻量级设计** - 单仓库可完整实现，易于理解和扩展

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **代码分析** | 自动解析 Python、JavaScript、TypeScript 代码结构 |
| 🕸️ **知识图谱** | 构建模块、函数、类之间的关联图谱 |
| 🎨 **交互可视化** | 生成可交互的 HTML 图谱，支持缩放、拖拽、搜索 |
| 📊 **影响分析** | 分析代码变更的影响范围，评估风险 |
| 🔥 **热点检测** | 识别高依赖区域，发现技术债务 |
| 💀 **死代码识别** | 找出未被调用的函数和方法 |
| 📦 **多格式导出** | 支持 JSON、GraphML、DOT、CSV、Markdown |
| 🚀 **CLI 工具** | 完整的命令行接口，易于集成到 CI/CD |

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows、macOS、Linux

### 安装

#### 方式一：通过 pip 安装（推荐）

```bash
pip install codemind-graph
```

#### 方式二：从源码安装

```bash
git clone https://github.com/gitstq/CodeMind-Graph.git
cd CodeMind-Graph
pip install -e .
```

### 快速使用

#### 1️⃣ 分析项目并生成交互式图谱

```bash
codemind-graph analyze ./my-project --output ./output
```

分析完成后，打开 `./output/graph.html` 查看交互式图谱。

#### 2️⃣ 查看项目统计信息

```bash
codemind-graph stats ./my-project
```

#### 3️⃣ 分析代码变更影响

```bash
codemind-graph impact ./my-project --files src/main.py,src/utils.py --output impact-report.md
```

#### 4️⃣ 查找代码热点

```bash
codemind-graph hotspots ./my-project --top 10
```

#### 5️⃣ 检测死代码

```bash
codemind-graph deadcode ./my-project
```

---

## 📖 详细使用指南

### 🔍 analyze 命令

分析代码库并生成知识图谱。

```bash
codemind-graph analyze <project_path> [options]
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `project_path` | 项目路径 | 必填 |
| `-o, --output` | 输出目录 | `./codemind-output` |
| `--formats` | 输出格式，逗号分隔 | `html,json,dot` |
| `--exclude` | 排除模式，逗号分隔 | 空 |

**支持格式：**
- `html` - 交互式可视化图谱
- `json` - 结构化数据
- `graphml` - Gephi/Cytoscape 格式
- `dot` - Graphviz 格式
- `csv` - 节点和边 CSV 文件
- `md` - Markdown 文档
- `svg` - 矢量图（需安装 graphviz）
- `png` - 位图（需安装 graphviz）

**示例：**

```bash
# 分析项目并生成所有格式
codemind-graph analyze ./my-project --formats html,json,dot,csv,md

# 排除测试文件
codemind-graph analyze ./my-project --exclude test,tests,docs
```

### ⚡ impact 命令

分析代码变更的影响范围。

```bash
codemind-graph impact <project_path> --files <changed_files> [options]
```

**示例：**

```bash
codemind-graph impact ./my-project \
  --files src/main.py,src/utils.py \
  --functions main,helper_function \
  --output impact-report.md
```

### 🔥 hotspots 命令

查找代码热点（高依赖区域）。

```bash
codemind-graph hotspots <project_path> [options]
```

**示例：**

```bash
# 查找前 20 个热点
codemind-graph hotspots ./my-project --top 20 --output hotspots.json
```

### 💀 deadcode 命令

查找可能的死代码。

```bash
codemind-graph deadcode <project_path> [options]
```

### 📦 modularity 命令

分析项目模块化程度。

```bash
codemind-graph modularity <project_path> [options]
```

### 📤 export 命令

导出图谱为特定格式。

```bash
codemind-graph export <project_path> --format <format> --output <path>
```

---

## 💡 设计思路与迭代规划

### 🎯 设计理念

1. **简单优先** - 零依赖，开箱即用
2. **隐私保护** - 本地分析，不上传代码
3. **可扩展性** - 模块化设计，易于扩展新语言支持
4. **开发者友好** - 清晰的 CLI 接口，完善的文档

### 📈 技术选型

| 组件 | 选型 | 原因 |
|------|------|------|
| 解析器 | AST (标准库) | 无需额外依赖，准确可靠 |
| 可视化 | D3.js (CDN) | 交互性强，无需本地安装 |
| 图谱格式 | 多格式支持 | 兼容主流图谱工具 |

### 🗓️ 后续迭代计划

- [ ] 支持更多语言（Java、Go、Rust）
- [ ] 代码质量评分系统
- [ ] 架构建议引擎
- [ ] VS Code 插件
- [ ] Web 界面
- [ ] 团队协作功能

---

## 📦 打包与部署

### 构建分发包

```bash
# 安装构建工具
pip install build twine

# 构建
python -m build

# 上传到 PyPI
python -m twine upload dist/*
```

### 系统要求

- **纯 Python 实现** - 无需编译
- **标准库 only** - 无第三方依赖
- **跨平台** - Windows、macOS、Linux 全支持

### 可选依赖

如需导出 PNG/SVG 格式，需要安装 Graphviz：

```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
choco install graphviz
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 提交 Issue

- 使用清晰的标题描述问题
- 提供复现步骤
- 附上相关代码和错误信息

### 提交 PR

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 规范
- 添加适当的文档字符串
- 保持测试覆盖率

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2026 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
