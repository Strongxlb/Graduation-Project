# results/

仿真与分析输出：图（PNG）、表格（CSV）、汇总统计。

**Week 1 解读 → [`结果解释.md`](结果解释.md)（中文）· [`结果解释-en.md`](结果解释-en.md)（English）**

## Week 1（Net1 demo）

| 目录 | 内容 | 生成脚本 |
| --- | --- | --- |
| `week1_demo/` | 修改版 Demo：4 张图 + 2 个 CSV | `src/01_demo_wntr.py` |
| `week1_original/` | 原始 `.inp` 基线：4 张图 + 2 个 CSV | `src/02_demo_wntr_original.py` |
| `week1_compare/` | 两版并排对比：2 张图 + 2 个汇总 CSV | `src/02_demo_wntr_original.py`（Step d） |

## 约定

- 每个实验一个子目录，**图和表放在同一目录**。
- 大文件放 `results/raw/` 或 `results/large/`（已在 `.gitignore` 中忽略）。
