# 毕业设计执行计划 - Plan 1

> 配套文件：[`README.md`](./README.md) · [`README.en.md`](./README.en.md) · [`background/Literature/literature.md`](./background/Literature/literature.md)
> 项目主题：**Uncertainty-aware calibration of first-order chlorine residual decay modelling in the Bristol Water Field Lab — a three-DMA comparative study**（基于 Bristol Water Field Lab 三个 DMA 的一阶余氯衰减不确定性感知校准）
> 研究区间：2026-05-15 至 2026-08-28（13 周论文 + 1 周 poster）
> 当前日期：**2026-05-25**（Week 1 收尾 / Week 2 启动）；下次会议：**2026-06-02 Tuesday**（导师本周出差）
>
> **2026-05-25 更新**：根据导师邮件正式锁定项目范围 —— 3 个监测 DMA + 10 个 chlorine monitors + first-order kinetics + ensemble-based uncertainty；明确排除水力校准 / MSX / 运营优化。详见 README §2、§5。

本文件回答两个问题：
1. **我总共要做什么？** —— 见第 1 节「总体任务地图」。
2. **下一步具体要怎么做？** —— 见第 2 节「Week 1 行动清单 + Week 2 启动」。

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

> 2026-05-25 更新：与导师邮件的 WP（Work Package）映射待 Tuesday 会议确认；以下 T1–T7 是仓库内部分工，不是 WP 正式编号。

| 模块 | 内容 | 主要输出 |
| --- | --- | --- |
| T1 文献综述 | 余氯衰减机理（A1/A2/A3/A4/A5/A6）、EPANET/WNTR（B1/B2/B3）、不确定性方法（E1/E3/E4/E5/E6/E7）、测量误差（D2/D3/D4/D5）、监管阈值（F1/F2） | 文献清单 + 综述章节 |
| T2 模型搭建 | 跑通导师 Jupyter notebook `simulate_chlorine(kb, kw)` → Net3 练手 → 切换 Bristol 3-DMA `.inp` 模型 | 可运行 3-DMA 模型 + baseline simulation |
| T3 数据组织 | 3 个 inlet monitors → time-varying source pattern；7 个 downstream monitors → calibration + validation 切分；DPD / 在线传感器测量误差模型 | 数据 schema + boundary pattern + 误差模型说明 |
| T4 确定性校准（baseline） | 在 `(k_b, k_w_A, k_w_B, k_w_C)` 上做 weighted least squares；NSE / RMSE / MAE 评估 | baseline 校准结果（单点估计） |
| T5 不确定性感知校准 | **Plan A**：GLUE（E6 Beven & Binley 1992）；**Plan B**：Bayesian hierarchical MCMC（E7 Gelman BDA Ch5/Ch11），3 个 `k_w` 共享族先验 partial pooling | 参数后验 / 5–95% 区间 / 节点低于阈值概率 |
| T6 跨 DMA 可迁移性 + 结果解释 | 后验预测检查（在 DMA-A 校准 → 预测 DMA-B/C）、CRPS / 覆盖率、`k_w` 后验小提琴图、阈值概率热力图 | Results 图表 + 工程解读 |
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

### 2.1 Week 1 完成定义（DoD） — 2026-05-25 回顾

完成 Week 1 意味着满足以下全部条件：

- [x] 仓库结构按 README §9.2 建好，并已推送到 GitHub。
- [x] Python 环境可一键复现，`wntr` + `epanet` 能 import 成功。
- [x] 至少跑通一个 WNTR 自带示例网络的水力 + 水质仿真，并保存结果图。
- [x] 整理出 ≥ 15 篇文献的初版清单，按主题分组（实际 28+ 条：A1–A6 / B1–B4 / C1–C6 / D1–D5 / E1–E7 / F1–F2）。
- [x] 列出所有需要导师在第一次/第二次 weekly meeting 确认的事项。
- [x] `plan1.md`（本文件）和 `README.md` 都已 commit。
- [x] **超额完成**：12 篇核心文献精读笔记入库（A1–A4 / C1, C2, C5 / D2 / E1, E3, E5 / F2）

**Week 1 已完成 → 进入 Week 2**（详见 §3 下一步）。

### 2.2 任务分解（按建议顺序执行）

#### Step 1 — 仓库与目录骨架（预计 0.5 天）

目的：让后续所有产出都有"地方放"，避免文件散落。

具体动作：

1. 在 codes 仓库根目录创建以下空目录（按 README §9.2）：
   - `background/`、`data/`、`models/`、`src/`、`results/`、`thesis/`、`meetings/`
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
5. 把时间序列 + 网络拓扑图保存到 `results/week1_demo/`。
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
   - **E. 不确定性感知校准**：Monte Carlo、贝叶斯、概率风险评估
2. 每条记录最少包含：作者 + 年份 + 标题 + DOI/链接 + 一行「为什么收录」。
3. 优先用 Imperial Library / Google Scholar；导出 BibTeX 存入 `thesis/refs.bib`。
4. 不需要本周读完，本周目标是**清单成型**，本周末挑出 3 篇必读、Week 2 精读。

建议第一批关键词搜索：
- `"chlorine decay" pipe network calibration`
- `WNTR water network tool resilience`
- `EPANET water quality uncertainty`
- `Bayesian calibration water distribution chlorine`
- `DPD colorimetric chlorine measurement uncertainty`

#### Step 5 — 待导师确认事项清单（2026-05-25 邮件后更新）

目的：第一次/第二次 weekly meeting 不能"只带问题"，要带**问题 + 自己的建议**。

> **状态更新（2026-05-25）**：导师邮件已经回答了 Q1（用 Bristol 3-DMA 真实数据）、Q4（ensemble-based + Bayesian / hierarchical）、Q5（3 DMA，非合成）。剩余开放问题更新如下，整理到 `meetings/2026-06-02.md`（Tuesday 会议纪要预填）：

**已被邮件回答（不再需要问）**

| # | 已回答的问题 | 邮件答复 |
| --- | --- | --- |
| 1 | 真实管网数据是否可获取？ | ✅ 是，Bristol Water Field Lab 3 DMA + 10 chlorine monitors |
| 4 | 校准方法路线偏好？ | ✅ ensemble-based（GLUE 优先 → Bayesian/hierarchical 进阶） |
| 5 | 论文使用的网络规模？ | ✅ Bristol 3-DMA 实际管网（非合成 Net1/Net3） |

**Tuesday 2026-06-02 会议必问**

| # | 问题 | 我的初步建议 | 决策影响 |
| --- | --- | --- | --- |
| 1 | 10 个监测点的数据格式 / 频率 / 时间跨度？何时交付？ | 优先 ≥ 4 周连续 hourly 数据；CSV 或 SCADA dump 均可 | 决定 T3 数据管线工作量 |
| 2 | Bristol 3-DMA `.inp` 文件在哪？管材 / 管径 / 管龄信息齐全度？ | 若管材/管龄缺失，用 Hallam 2002 + Maleki 2023 范围作 informative prior | 决定能否做"分管材 `k_w`"细化 |
| 3 | `k_b` 共享假设：3 个 DMA 同一 `k_b`，还是各自估？ | 同一水源 ⇒ 倾向 pooled `k_b`；用 prior + bottle test 文献（A3 Powell）约束 | 影响参数个数：4 vs 6 |
| 4 | "ensemble-based method" 具体偏好：GLUE / ensemble Kalman / approximate Bayesian？ | Plan A = GLUE（E6）作为 robust baseline；Plan B = Bayesian hierarchical（E7） | 决定 Week 8–9 主算法 |
| 5 | WP1–WP5 正式结构是什么？WP5 = hierarchical Bayesian 已知 | 推测：WP1=Lit + Model setup, WP2=Baseline calib, WP3=Uncertainty, WP4=Cross-DMA, WP5=Bayesian | 影响进度报告对齐口径 |
| 6 | 阈值是否锁定 `0.2 mg/L`？是否要参照 UK SI 2016/614 + WHO ≥ 0.2 mg/L？ | 论文中先用 0.2 mg/L 占位 + 0.1 / 0.3 敏感性 | 影响所有「阈值概率」结果图 |
| 7 | 测量误差模型：用 DPD (D2 Soares) 还是在线传感器 (D3 Aisopou) 的不确定度？ | 入口 = 在线传感器误差（~5%）；下游若是 grab sample = DPD ±0.02 mg/L | 影响 likelihood 函数形式 |
| 8 | AI 工具使用披露口径？ | 按 CEE 模板写一节附录 | 论文格式风险 |

#### Step 6 — 本周 commit 与会议准备（预计 0.5 天）

1. 把 Week 1 所有产出 commit 到 GitHub，至少包含：
   - 目录骨架 + `.gitignore`
   - `requirements.txt`
   - `src/01_demo_wntr.py` + `results/week1_demo/*`
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

## 3. 下一步：Week 2 启动（2026-05-23 → 2026-06-02 Tuesday 会议）

> 注：导师本周（05-25 → 05-30）出差，下次会议改到 **2026-06-02 周二**。Week 2 的有效工作窗实际跨越 11 天。

### 3.1 Week 2 优先任务

按优先级排序，**前 3 项必须在 Tuesday 会议前完成**：

| # | 任务 | 预计工时 | 关联模块 |
| --- | --- | --- | --- |
| 1 | **跑通导师 Jupyter notebook** `simulate_chlorine(kb, kw)`（Net3 练手） | 2h | T2 |
| 2 | **下载并速读** B1 Klise 2017 WNTR 论文 + B2 EPANET 2.2 Manual（仅水质章节）+ A6 Vasconcelos 1997 | 4h | T1 |
| 3 | **整理 `meetings/2026-06-02.md`**：上周完成 / 当前阻碍 / 8 个问题（见 §2.2 Step 5）+ 自己的建议 | 1h | M1 准备 |
| 4 | 速读 E6 Beven & Binley 1992 GLUE（理论部分，~10 页核心即可） | 2h | T1 |
| 5 | 速读 E7 Gelman BDA Ch 5（hierarchical models 概念） | 2h | T1 |
| 6 | 在仓库根目录建 `notebooks/`，把导师的 `.ipynb` 放进去并跑通；commit 信息 `feat(notebook): supervisor starter simulate_chlorine on Net3` | 1h | T2 |
| 7 | 在 WNTR demo 基础上把 chlorine source、bulk decay、wall decay 三个参数改成可配置变量（为 Week 3 切到 Bristol 模型做准备） | 2h | T2 |

### 3.2 Week 2 收尾产出（commit 到仓库）

- `meetings/2026-06-02.md`：会议纪要 + 问题清单
- `notebooks/01_supervisor_starter.ipynb`：跑通 + 截图
- `notebooks/02_configurable_kb_kw.ipynb`：参数可配置版本
- `background/notes/A/A6_Vasconcelos1997.md`：速读笔记（按已有 tutorial-style 模板）
- `background/notes/B/B1_Klise2017.md` + `B2_EPANET22Manual.md`：速读笔记
- `background/notes/E/E6_BevenBinley1992.md`：速读笔记（GLUE 方法）

### 3.3 Week 3+ 的方向（提前看）

待 Tuesday 会议确认数据交付后：

- Week 3–4：拿到 Bristol 3-DMA `.inp` + 数据 → 切换基线模型 → baseline 确定性校准
- Week 5（M1 06-19 准备）：完成 baseline + Plan A（GLUE）跑通 + 给导师 progress report
- Week 6+：进入 Plan B（Bayesian hierarchical MCMC）+ 跨 DMA 可迁移性评估

Week 2 之后的细化计划在 `plan2.md`（届时再写）。

---

## 4. 本计划的版本约定

- 本文件 = Plan 1 = Week 1 的详细计划 + 全局任务地图。
- 后续每周开始前新增 `planN.md`，只写当周细化 + 必要的全局调整。
- 任何与 README 冲突的内容以 README 为准；本文件被视作 README 的"执行视图"。
