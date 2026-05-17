# 毕业设计执行计划 - Plan 1

> 配套文件：[`README.md`](./README.md)
> 项目主题：不确定性感知的供水管网余氯模型校准（CIVE70058 Research Dissertation）
> 研究区间：2026-05-15 至 2026-08-28（13 周论文 + 1 周 poster）
> 当前日期：2026-05-17（处于 Week 1）

本文件回答两个问题：
1. **我总共要做什么？** —— 见第 1 节「总体任务地图」。
2. **第一步具体要怎么做？** —— 见第 2 节「Week 1 行动清单」。

---

## 1. 总体任务地图

### 1.1 三类最终交付物

| 编号 | 交付物 | 截止时间 | 说明 |
| --- | --- | --- | --- |
| D1 | Research paper（≤ 12,000 words） | 2026-08-21 12:00 | 论文主体，按 Imperial CEE 论文格式 |
| D2 | Research poster | 2026-08-28 12:00 | 图表化方式呈现动机/方法/结果/结论 |
| D3 | 可复现代码 + 数据说明 + 图表 | 随论文一起 | 所有内容以 Git/GitHub 留痕 |

### 1.2 两个中期检查点

| 编号 | 节点 | 截止时间 | 必须准备的材料 |
| --- | --- | --- | --- |
| M1 | Supervisor checkpoint / progress report | 2026-06-19 | 进度总结、问题清单、下一步校准方案 |
| M2 | Student checkpoint / reflection | 2026-07-03 | 自我反思、baseline calibration 完成度 |

### 1.3 七大研究模块（贯穿整个项目）

| 模块 | 内容 | 主要输出 |
| --- | --- | --- |
| T1 文献综述 | 余氯衰减机理、EPANET/WNTR 应用、传感器不确定性、Monte Carlo / 贝叶斯校准 | 文献清单 + 综述章节 |
| T2 模型搭建 | 选定/构造 EPANET `.inp` 网络，配置水力 + 水质模拟 | 可运行 `.inp` 文件 + baseline simulation |
| T3 数据组织 | 整理观测余氯、采样信息、误差假设；真实数据缺失时使用合成或 benchmark 数据 | 数据 schema + 数据说明文档 |
| T4 确定性校准 | 围绕 bulk decay / wall decay 建立目标函数（RMSE / MAE 等） | baseline 校准结果 |
| T5 不确定性感知校准 | Monte Carlo 或概率方法传播 sensor uncertainty | 参数分布 + 预测区间 + 阈值概率 |
| T6 结果解释 | 空间分布、时间序列、敏感性、误差带、低于 0.2 mg/L 的概率图 | Results 图表 + 工程解读 |
| T7 论文写作 | Introduction / Background / Methodology / Results / Discussion / Conclusion | 论文主体 + poster |

### 1.4 13 周时间表（一图看全）

| 阶段 | 时间窗口 | 主目标 | 关键产出 | 与模块对应 |
| --- | --- | --- | --- | --- |
| **Week 1** | 05-15 → 05-22 | 明确论文结构、研究问题和工具链 | README、文献清单、Git 仓库、跑通 WNTR demo | T1, T2 启动 |
| Week 2 | 05-23 → 05-29 | 完成背景阅读和方法路线选择 | Introduction/Background 草稿；EPANET/WNTR 示例可运行 | T1, T2 |
| Week 3-4 | 05-30 → 06-12 | 建立或整理管网模型与数据格式 | 可运行 `.inp` 模型；数据 schema；baseline simulation | T2, T3 |
| **Week 5（M1 准备）** | 06-13 → 06-19 | Supervisor checkpoint | 进度报告、问题清单、下一步校准方案 | T1–T3 收口 |
| Week 6-7 | 06-20 → 07-03 | 完成确定性校准；Student checkpoint | baseline calibration；reflection | T4 |
| Week 8-9 | 07-04 → 07-17 | 加入 sensor uncertainty 与 Monte Carlo | 参数分布、预测区间、阈值概率 | T5 |
| Week 10 | 07-18 → 07-24 | 完成主要结果图 | Results 图表 + 初步讨论 | T6 |
| Week 11 | 07-25 → 07-31 | 集中写 Methodology / Results / Discussion | 论文主体初稿 | T7 |
| Week 12 | 08-01 → 08-07 | 完成完整论文初稿 | Full draft（提交导师反馈） | T7 |
| Week 13 | 08-08 → 08-21 | 修改、校对、提交 | 最终 research paper | D1 |
| Poster | 08-22 → 08-28 | 制作和提交 poster | 最终 research poster | D2 |

### 1.5 持续维护（每周必做）

- **每周会议纪要**：按 README §10 模板写，存入 `meetings/`。
- **Git commit**：每个阶段至少一次有意义的 commit；不提交大文件、原始数据和隐私数据。
- **AI 使用记录**：若用 AI 辅助代码、语言润色或图表说明，按 Imperial/CEE 要求留痕，最终披露。

---

## 2. Week 1 行动清单（2026-05-15 → 2026-05-22）

> 当前时间为 2026-05-17（周日），距 Week 1 截止还有 **5 天**。
> Week 1 的核心目标只有三个：**研究范围确认 + 工具链跑通 + 初步知识储备**。
> 不要陷入"现在就开始写校准代码"的陷阱，本周一行业务代码都不写，重点是搭好骨架。

### 2.1 Week 1 完成定义（DoD）

完成 Week 1 意味着满足以下全部条件：

- [ ] 仓库结构按 README §9.2 建好，并已推送到 GitHub。
- [ ] Python 环境可一键复现，`wntr` + `epanet` 能 import 成功。
- [ ] 至少跑通一个 WNTR 自带示例网络的水力 + 水质仿真，并保存结果图。
- [ ] 整理出 ≥ 15 篇文献的初版清单，按主题分组。
- [ ] 列出所有需要导师在第一次/第二次 weekly meeting 确认的事项。
- [ ] `plan1.md`（本文件）和 `README.md` 都已 commit。

### 2.2 任务分解（按建议顺序执行）

#### Step 1 — 仓库与目录骨架（预计 0.5 天）

目的：让后续所有产出都有"地方放"，避免文件散落。

具体动作：

1. 在 codes 仓库根目录创建以下空目录（按 README §9.2）：
   - `background/`、`data/`、`models/`、`src/`、`results/`、`figures/`、`thesis/`、`meetings/`
   - 每个目录下建一个 `.gitkeep` 空文件，保证 Git 能追踪空目录。
2. 写 `.gitignore`，至少屏蔽：
   - Python：`__pycache__/`、`*.pyc`、`.venv/`、`.ipynb_checkpoints/`
   - 数据/结果：`data/raw/`、`results/*.csv`（视情况）、`*.h5`、`*.npz`
   - 系统：`.DS_Store`、`Thumbs.db`、`.idea/`、`.vscode/`（视情况保留）
3. 在 GitHub 上建私有仓库（建议私有，论文提交前公开），将本地仓库 push 上去。
4. commit 信息：`chore: scaffold project directories per README §9.2`。

#### Step 2 — Python 工具链（预计 0.5 天）

目的：让"跑模型"这件事在任何机器上 5 分钟就能复现。

具体动作：

1. 创建虚拟环境（`python -m venv .venv` 或 `conda create -n cive70058 python=3.11`）。
2. 安装核心依赖：
   - `wntr`（含 EPANET 引擎绑定）
   - `numpy`、`pandas`、`scipy`、`matplotlib`
   - `jupyterlab`（用于探索）
   - 之后会用到：`pyDOE`、`SALib`（敏感性 / 采样）、`emcee` 或 `pymc`（贝叶斯校准，Week 8+ 再加）
3. 把当前装好的版本固化到 `requirements.txt`（`pip freeze > requirements.txt`）。
4. 在 `README.md` 顶部加一段「快速开始」（如何创建环境 + 装依赖）—— 后续给导师/审阅者复现用。

#### Step 3 — 跑通第一个 WNTR demo（预计 0.5–1 天）

目的：确认水力 + 水质链路全通，建立后续工作的"参照系"。

具体动作：

1. 在 `src/` 下新建 `01_demo_wntr.py`（或 `notebooks/01_demo_wntr.ipynb`）。
2. 加载 WNTR 自带的 `Net1.inp` 或 `Net3.inp`（不需要先找真实管网）。
3. 跑一次水力仿真，打印节点压力、管段流量；确认结果合理（无负压、无奇怪值）。
4. 跑一次水质仿真：把 source node 设为 chlorine source，给一个 bulk decay 系数（如 -0.5 /day），输出某节点的 chlorine 时间序列。
5. 把时间序列 + 网络拓扑图保存到 `figures/week1_demo/`。
6. commit 信息：`feat: minimal WNTR hydraulic + chlorine demo on Net1`。

> 这一步只是"打通管线"，不要纠结参数是否真实，下周才开始动模型。

#### Step 4 — 文献清单初版（预计 1.5 天）

目的：避免后面写综述时"现搜现读现写"的低效循环。

具体动作：

1. 在 `background/literature.md` 建文献表，按以下主题分组（每组 3–5 篇起步）：
   - **A. Chlorine decay 机理**：bulk decay、wall decay、温度/有机物影响（先找经典综述）
   - **B. EPANET/WNTR 工具与方法学**：WNTR 官方论文、EPANET 2.2 manual、若干典型案例
   - **C. 水质模型校准**：参数估计、目标函数、敏感性分析
   - **D. 测量不确定性**：DPD / colorimetric error、在线传感器精度规格、采样设计
   - **E. 不确定性感知校准**：Monte Carlo、贝叶斯、GLUE、概率风险评估
2. 每条记录最少包含：作者 + 年份 + 标题 + DOI/链接 + 一行「为什么收录」。
3. 优先用 Imperial Library / Google Scholar；导出 BibTeX 存入 `thesis/refs.bib`。
4. 不需要本周读完，本周目标是**清单成型**，本周末挑出 3 篇必读、Week 2 精读。

建议第一批关键词搜索：
- `"chlorine decay" pipe network calibration`
- `WNTR water network tool resilience`
- `EPANET water quality uncertainty`
- `Bayesian calibration water distribution chlorine`
- `DPD colorimetric chlorine measurement uncertainty`

#### Step 5 — 待导师确认事项清单（预计 0.5 天）

目的：第一次/第二次 weekly meeting 不能"只带问题"，要带**问题 + 自己的建议**。

把以下条目整理到 `meetings/open_questions.md`：

| # | 问题 | 我的初步建议 | 决策影响 |
| --- | --- | --- | --- |
| 1 | 真实管网数据是否可获取？ | 若否，使用 WNTR 自带 Net1/Net3 + 合成观测 | 决定 T2/T3 是否需要数据清洗周 |
| 2 | 余氯阈值是否锁定为 0.2 mg/L？ | 论文中先用 0.2 mg/L 占位，并做 0.1 / 0.3 敏感性 | 影响所有「阈值概率」结果图 |
| 3 | 测量误差分布形式？ | 先用 `N(0, σ²)` + 相对误差 5–10%，待数据后再定 | 影响 Monte Carlo 设计 |
| 4 | 校准方法路线偏好？ | Plan A：MC + 最小二乘；Plan B：贝叶斯（emcee/pymc） | 决定 Week 8–9 工作量 |
| 5 | 论文使用的网络规模？ | 建议中等规模（Net3 量级，≥ 90 节点） | 影响计算成本 |
| 6 | AI 工具使用披露口径？ | 按 CEE 模板写一节附录 | 论文格式风险 |

#### Step 6 — 本周 commit 与会议准备（预计 0.5 天）

1. 把 Week 1 所有产出 commit 到 GitHub，至少包含：
   - 目录骨架 + `.gitignore`
   - `requirements.txt`
   - `src/01_demo_wntr.py` + `figures/week1_demo/*`
   - `background/literature.md`
   - `meetings/open_questions.md`
   - `plan1.md`（本文件）
2. 在 `meetings/` 下用 README §10 模板新建 `2026-05-22.md`（或下次会议日期），预填：
   - 上周完成：Step 1–5 的勾选状态
   - 当前阻碍：见 open_questions
   - 我的建议：同上表第 3 列
   - 下周计划：进入 Week 2 — 精读 3 篇核心文献 + Introduction/Background 草稿

### 2.3 Week 1 时间预算（建议）

| 日期 | 建议工作量 | 重点 |
| --- | --- | --- |
| 05-17 周日（今天） | 2–3h | Step 1（仓库骨架）+ Step 2（环境） |
| 05-18 周一 | 2–3h | Step 3（WNTR demo） |
| 05-19 周二 | 2h | Step 4 启动（文献检索） |
| 05-20 周三 | 2h | Step 4 继续（清单成型） |
| 05-21 周四 | 1.5h | Step 5（导师问题清单） |
| 05-22 周五 | 1h | Step 6（commit + 会议纪要模板） |

总计约 **10–12 小时**，保留缓冲应对环境安装/依赖踩坑。

### 2.4 Week 1 风险与应对

| 风险 | 触发信号 | 应对 |
| --- | --- | --- |
| `wntr` 安装失败（EPANET 二进制兼容） | macOS arm64 报错 | 改用 `conda install -c conda-forge wntr` |
| 找不到合适网络 | Net1 节点太少不够写论文 | Week 1 用 Net1 跑通即可，Week 3 再换 Net3 / BWSN benchmark |
| 文献过多无从下手 | 检索结果 > 200 篇 | 限定近 10 年 + ≥ 20 引用；按摘要快速筛选 |
| 导师暂无回复 | 周中未回邮件 | 用上述「初步建议」继续推进，不阻塞 |

---

## 3. 下一步（提前看一眼 Week 2）

Week 1 收尾后，Week 2（05-23 → 05-29）的核心任务是：

- 精读 Step 4 文献清单中标记为「必读」的 3 篇（每篇 1.5h 笔记）。
- 写 Introduction 和 Background 章节的**结构骨架**（不写完整段落，只写每段的论点要点）。
- 在 WNTR demo 基础上，把 chlorine source、bulk decay、wall decay 三个参数改成可配置变量，为 Week 3 的 baseline simulation 做准备。

Week 2 的细化计划在 `plan2.md`（届时再写），本文件不展开。

---

## 4. 本计划的版本约定

- 本文件 = Plan 1 = Week 1 的详细计划 + 全局任务地图。
- 后续每周开始前新增 `planN.md`，只写当周细化 + 必要的全局调整。
- 任何与 README 冲突的内容以 README 为准；本文件被视作 README 的"执行视图"。
