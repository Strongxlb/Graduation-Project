# `learning/` — 学习与起步资料

本目录存放：

- 项目相关的教程性文档（如 `git_learning.md`）。
- 导师提供的起步代码与练习。
- 自学练习的 Jupyter notebooks。

---

## Notebook 提交约定（重要）

**不把 `.ipynb` 文件提交到 git。** 取而代之，每个 notebook 配套提交其**渲染后的 HTML 导出**作为可审阅的"快照"。

理由：

- Notebook 是 JSON，里面的 image base64、execution_count、cell metadata 都会被 git 当成内容变动，造成大量噪声 diff。
- 即便代码完全没动，重跑一次 outputs 就变，难以 review。
- HTML export 是只读静态产物，文件大但 diff 友好（如果只关心图，每次重新导出即可）。

### 操作流程

```bash
# 编辑/运行 .ipynb 后，导出 HTML：
jupyter nbconvert --to html learning/your_notebook.ipynb

# 只 commit 生成的 .html：
git add learning/your_notebook.html
git commit -m "docs(learning): refresh HTML export of your_notebook"
```

`.gitignore` 已设置 `*.ipynb` 忽略全部 notebook 源文件。如某个 notebook 例外要追踪（如稳定且不会重跑的教学样板），可在 `.gitignore` 末尾加 `!path/to/keep.ipynb`。

---

## 当前内容

| 文件 | 说明 |
| --- | --- |
| `git_learning.md` | Git/GitHub 基础教程（本仓库使用规范） |
| `wntr_chlorine_getting_started.ipynb` | **导师 2026-05-25 邮件附件**：WNTR 余氯仿真起步 notebook，定义全项目核心函数 `simulate_chlorine(kb, kw)`，含 5 道练习题 — **本地保留，不提交** |
| `wntr_chlorine_getting_started.html` | 上述 notebook 的渲染快照（含运行输出与 3 张图） |
| `02_exercises.ipynb` | **自学练习本**：把导师 §7 的 5 道题展开成"题目 + 骨架代码 + 提示 + 反思"格式，逐题做完后即具备 Bristol 真实建模的全部基础工具 — **本地保留，不提交** |
| `_build_exercises_nb.py` | 生成 `02_exercises.ipynb` 的脚本（源于此可重新生成、修改题目） |
| `net3_topology.png` | Net3 网络拓扑图：2 个 reservoir (River+Lake) · 3 个 tank · 6 个 monitor |
| `kb_kw_compensation.png` | k_b / k_w 联合扫描的误差地形图：直观演示 identifiability 问题（"补偿沟"） |

---

## 推荐做练习的顺序

1. **先看** `wntr_chlorine_getting_started.html` —— 把导师的 5 道题快速过一遍（5 分钟）
2. **打开** `02_exercises.ipynb` —— 一题一题做（每题 20-40 分钟）
3. **每题做完**：在 markdown 的"✏️ 你的发现"下用 1-2 句话写结论
4. **5 题全做完后**：
   - 你已经掌握 `simulate_chlorine(kb, kw)` 的用法和扩展
   - 知道 bulk/wall 衰减的物理含义和数量级
   - 会用 add_source 注入时变边界（Bristol 必备）
   - 亲手做过最朴素的网格校准，理解 identifiability 问题
5. **下一步**：等到拿到 Bristol 3-DMA `.inp` 和 SCADA 数据，可直接把 `PRACTICE_INP` 和 `MONITOR_NODES` 替换掉
