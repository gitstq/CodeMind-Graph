# 🔍 CodeMind-Graph

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version 1.0.0">
</p>

<p align="center">
  <b>代碼知識圖譜可視化與分析工具</b><br>
  將代碼庫轉換為交互式知識圖譜，讓代碼結構一目瞭然
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.zh-TW.md">繁體中文</a> |
  <a href="README.md">English</a>
</p>

---

## 🎉 項目介紹

**CodeMind-Graph** 是一款輕量級、零依賴的代碼知識圖譜生成工具。它能夠自動分析你的代碼庫，提取函數、類別、導入關係等元數據，並構建成可視化的知識圖譜。

### 💡 靈感來源

本項目靈感來源於 GitHub Trending 上的 [Understand-Anything](https://github.com/Lum1104/Understand-Anything)，但我們採用了不同的技術路線：
- **純 Python 實現** - 無需複雜的 TypeScript 構建流程
- **零外部依賴** - 僅使用 Python 標準庫，開箱即用
- **本地離線運行** - 無需 AI 平台插件，保護代碼隱私
- **輕量級設計** - 單倉庫可完整實現，易於理解和擴展

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **代碼分析** | 自動解析 Python、JavaScript、TypeScript 代碼結構 |
| 🕸️ **知識圖譜** | 構建模組、函數、類別之間的關聯圖譜 |
| 🎨 **交互可視化** | 生成可交互的 HTML 圖譜，支持縮放、拖拽、搜索 |
| 📊 **影響分析** | 分析代碼變更的影響範圍，評估風險 |
| 🔥 **熱點檢測** | 識別高依賴區域，發現技術債務 |
| 💀 **死代碼識別** | 找出未被調用的函數和方法 |
| 📦 **多格式導出** | 支持 JSON、GraphML、DOT、CSV、Markdown |
| 🚀 **CLI 工具** | 完整的命令行接口，易於集成到 CI/CD |

---

## 🚀 快速開始

### 環境要求

- **Python**: 3.8 或更高版本
- **操作系統**: Windows、macOS、Linux

### 安裝

#### 方式一：通過 pip 安裝（推薦）

```bash
pip install codemind-graph
```

#### 方式二：從源碼安裝

```bash
git clone https://github.com/gitstq/CodeMind-Graph.git
cd CodeMind-Graph
pip install -e .
```

### 快速使用

#### 1️⃣ 分析項目並生成交互式圖譜

```bash
codemind-graph analyze ./my-project --output ./output
```

分析完成後，打開 `./output/graph.html` 查看交互式圖譜。

#### 2️⃣ 查看項目統計信息

```bash
codemind-graph stats ./my-project
```

#### 3️⃣ 分析代碼變更影響

```bash
codemind-graph impact ./my-project --files src/main.py,src/utils.py --output impact-report.md
```

#### 4️⃣ 查找代碼熱點

```bash
codemind-graph hotspots ./my-project --top 10
```

#### 5️⃣ 檢測死代碼

```bash
codemind-graph deadcode ./my-project
```

---

## 📖 詳細使用指南

### 🔍 analyze 命令

分析代碼庫並生成知識圖譜。

```bash
codemind-graph analyze <project_path> [options]
```

**參數說明：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `project_path` | 項目路徑 | 必填 |
| `-o, --output` | 輸出目錄 | `./codemind-output` |
| `--formats` | 輸出格式，逗號分隔 | `html,json,dot` |
| `--exclude` | 排除模式，逗號分隔 | 空 |

**支持格式：**
- `html` - 交互式可視化圖譜
- `json` - 結構化數據
- `graphml` - Gephi/Cytoscape 格式
- `dot` - Graphviz 格式
- `csv` - 節點和邊 CSV 文件
- `md` - Markdown 文檔
- `svg` - 矢量圖（需安裝 graphviz）
- `png` - 位圖（需安裝 graphviz）

**示例：**

```bash
# 分析項目並生成所有格式
codemind-graph analyze ./my-project --formats html,json,dot,csv,md

# 排除測試文件
codemind-graph analyze ./my-project --exclude test,tests,docs
```

### ⚡ impact 命令

分析代碼變更的影響範圍。

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

查找代碼熱點（高依賴區域）。

```bash
codemind-graph hotspots <project_path> [options]
```

**示例：**

```bash
# 查找前 20 個熱點
codemind-graph hotspots ./my-project --top 20 --output hotspots.json
```

### 💀 deadcode 命令

查找可能的死代碼。

```bash
codemind-graph deadcode <project_path> [options]
```

### 📦 modularity 命令

分析項目模塊化程度。

```bash
codemind-graph modularity <project_path> [options]
```

### 📤 export 命令

導出圖譜為特定格式。

```bash
codemind-graph export <project_path> --format <format> --output <path>
```

---

## 💡 設計思路與迭代規劃

### 🎯 設計理念

1. **簡單優先** - 零依賴，開箱即用
2. **隱私保護** - 本地分析，不上傳代碼
3. **可擴展性** - 模塊化設計，易於擴展新語言支持
4. **開發者友好** - 清晰的 CLI 接口，完善的文檔

### 📈 技術選型

| 組件 | 選型 | 原因 |
|------|------|------|
| 解析器 | AST (標準庫) | 無需額外依賴，準確可靠 |
| 可視化 | D3.js (CDN) | 交互性強，無需本地安裝 |
| 圖譜格式 | 多格式支持 | 兼容主流圖譜工具 |

### 🗓️ 後續迭代計劃

- [ ] 支持更多語言（Java、Go、Rust）
- [ ] 代碼質量評分系統
- [ ] 架構建議引擎
- [ ] VS Code 插件
- [ ] Web 界面
- [ ] 團隊協作功能

---

## 📦 打包與部署

### 構建分發包

```bash
# 安裝構建工具
pip install build twine

# 構建
python -m build

# 上傳到 PyPI
python -m twine upload dist/*
```

### 系統要求

- **純 Python 實現** - 無需編譯
- **標準庫 only** - 無第三方依賴
- **跨平台** - Windows、macOS、Linux 全支持

### 可選依賴

如需導出 PNG/SVG 格式，需要安裝 Graphviz：

```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
choco install graphviz
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 提交 Issue

- 使用清晰的標題描述問題
- 提供復現步驟
- 附上相關代碼和錯誤信息

### 提交 PR

1. Fork 本倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 創建 Pull Request

### 代碼規範

- 遵循 PEP 8 規範
- 添加適當的文檔字符串
- 保持測試覆蓋率

---

## 📄 開源協議

本項目採用 [MIT License](LICENSE) 開源協議。

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
